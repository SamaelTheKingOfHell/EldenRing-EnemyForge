using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using SoulsFormats;
using SoulsFormats.Cryptography;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Orchestrates regulation decryption, param loading, phantom character injection,
    /// carried loot drop mapping, and AES-256 re-encryption.
    /// Incorporates all engine limit checks (16-bit row ceiling) and error handling.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class PatchService
    {
        public static void ExecutePatch(Dictionary<string, string> options)
        {
            string inputPath = options["--input"];
            string outputPath = options["--output"];
            string defsPath = options["--defs"];
            string specPath = options["--spec"];
            string? msgPath = options.GetValueOrDefault("--msg");

            if (!File.Exists(inputPath)) throw new FileNotFoundException($"Input regulation not found: {inputPath}");
            if (!File.Exists(specPath)) throw new FileNotFoundException($"Patch specification not found: {specPath}");
            if (!Directory.Exists(defsPath)) throw new DirectoryNotFoundException($"Paramdefs directory not found: {defsPath}");

            Console.WriteLine($"[RegTool] Decrypting Elden Ring regulation from: {inputPath}...");
            BND4 regBnd = RegulationDecryptor.DecryptERRegulation(inputPath);

            Console.WriteLine($"[RegTool] Reading phantom patch specification: {specPath}...");
            string jsonText = File.ReadAllText(specPath);
            using var doc = JsonDocument.Parse(jsonText);
            var root = doc.RootElement;

            // Load required PARAM tables into cache
            var paramCache = new Dictionary<string, (PARAM Param, BinderFile File)>(StringComparer.OrdinalIgnoreCase);
            var tableToDef = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["NpcParam"] = "NpcParam",
                ["CharaInitParam"] = "CharaInitParam",
                ["FaceParam"] = "FaceParam",
                ["ItemLotParam_enemy"] = "ItemLotParam"
            };

            foreach (var kvp in tableToDef)
            {
                string tableName = kvp.Key;
                string defName = kvp.Value;

                var file = regBnd.Files.FirstOrDefault(f => Path.GetFileNameWithoutExtension(f.Name).Equals(tableName, StringComparison.OrdinalIgnoreCase));
                if (file == null)
                {
                    throw new InvalidOperationException($"Required parameter '{tableName}' not found inside regulation.bin");
                }

                string defXml = Path.Combine(defsPath, $"{defName}.xml");
                if (!File.Exists(defXml))
                {
                    throw new FileNotFoundException($"Paramdef XML not found: {defXml}");
                }

                Console.WriteLine($"[RegTool] Loading paramdef '{defName}' and parsing '{tableName}'...");
                var def = PARAMDEF.XmlDeserialize(defXml, false, false);
                var param = PARAM.Read(file.Bytes);
                param.ApplyParamdef(def);
                paramCache[tableName] = (param, file);
            }

            var npcParam = paramCache["NpcParam"].Param;
            var charaInitParam = paramCache["CharaInitParam"].Param;
            var faceParam = paramCache["FaceParam"].Param;
            var itemLotParam = paramCache["ItemLotParam_enemy"].Param;

            var phantomNamesToInject = new List<FmgInjector.PhantomNameEntry>();

            JsonElement enemiesArray = default;
            bool hasEnemies = (root.TryGetProperty("enemies", out enemiesArray) && enemiesArray.ValueKind == JsonValueKind.Array) ||
                              (root.TryGetProperty("phantoms", out enemiesArray) && enemiesArray.ValueKind == JsonValueKind.Array);

            if (hasEnemies)
            {
                Console.WriteLine($"[RegTool] Processing {enemiesArray.GetArrayLength()} character enemy/phantom(s)...");
                foreach (JsonElement enemySpec in enemiesArray.EnumerateArray())
                {
                    string name = enemySpec.GetProperty("name").GetString() ?? "World Enemy";
                    int npcId = enemySpec.GetProperty("npc_param_id").GetInt32();
                    int itemLotId = enemySpec.GetProperty("item_lot_id").GetInt32();

                    // 1. Inject Humanoid Enemy Parameters (NpcParam, CharaInitParam, FaceParam)
                    EnemyInjector.InjectEnemyParams(npcParam, charaInitParam, faceParam, enemySpec);
                    phantomNamesToInject.Add(new FmgInjector.PhantomNameEntry(npcId, name));

                    // 2. Inject Carried Loot Drops (ItemLotParam_enemy)
                    var carriedDrops = new List<LootInjector.LootDropItem>();
                    if (enemySpec.TryGetProperty("carried_drops", out JsonElement dropsArray) && dropsArray.ValueKind == JsonValueKind.Array)
                    {
                        foreach (JsonElement dropElem in dropsArray.EnumerateArray())
                        {
                            int itemId = dropElem.GetProperty("item_id").GetInt32();
                            string itemType = dropElem.GetProperty("item_type").GetString() ?? "protector";
                            int prob = dropElem.TryGetProperty("probability", out JsonElement p) ? p.GetInt32() : 1000;
                            int qty = dropElem.TryGetProperty("quantity", out JsonElement q) ? q.GetInt32() : 1;
                            carriedDrops.Add(new LootInjector.LootDropItem(itemId, itemType, prob, qty));
                        }
                    }

                    LootInjector.InjectCarriedLootDrops(itemLotParam, itemLotId, name, carriedDrops);
                }
            }

            // 3. FMG Name Injection (if message directory is present)
            if (!string.IsNullOrEmpty(msgPath) && Directory.Exists(msgPath))
            {
                string itemMsgBndPath = Path.Combine(msgPath, "item.msgbnd.dcx");
                if (File.Exists(itemMsgBndPath))
                {
                    Console.WriteLine($"[RegTool] Injecting phantom names into message archive: {itemMsgBndPath}...");
                    try
                    {
                        BND4 msgBnd = BND4.Read(itemMsgBndPath);
                        FmgInjector.InjectPhantomNames(msgBnd, phantomNamesToInject);
                        msgBnd.Write(itemMsgBndPath);
                        Console.WriteLine($"[RegTool] Successfully saved updated message archive.");
                    }
                    catch (Exception ex)
                    {
                        Console.Error.WriteLine($"[RegTool WARNING] FMG injection failed: {ex.Message}");
                    }
                }
            }

            // 4. Validate and serialize modified params
            foreach (var kvp in paramCache)
            {
                var (param, file) = kvp.Value;
                if (param.Rows.Count > ushort.MaxValue)
                {
                    throw new InvalidOperationException(
                        $"Table '{kvp.Key}' has {param.Rows.Count} rows, exceeding FromSoftware engine maximum of {ushort.MaxValue} (16-bit row limit).");
                }

                Console.WriteLine($"[RegTool] Serializing table: {kvp.Key} ({param.Rows.Count} rows)...");
                try
                {
                    file.Bytes = param.Write();
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"[RegTool ERROR] Failed to serialize param '{kvp.Key}': {ex.Message}");
                    throw;
                }
            }

            // 5. Re-encrypt regulation with AES-256
            string? outDir = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(outDir) && !Directory.Exists(outDir))
            {
                Directory.CreateDirectory(outDir);
            }

            Console.WriteLine($"[RegTool] Encrypting and saving regulation to: {outputPath}...");
            RegulationDecryptor.EncryptERRegulation(outputPath, regBnd);
            Console.WriteLine("[RegTool] Patch complete! Regulation successfully forged.");
        }
    }
}
