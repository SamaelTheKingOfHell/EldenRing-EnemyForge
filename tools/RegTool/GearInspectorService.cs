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
    /// Service to inspect regulation.bin for installed armor sets and weapons.
    /// Distinguishes between base game items and patched/modded items (e.g. from LootForge).
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class GearInspectorService
    {
        public static void InspectGear(Dictionary<string, string> options)
        {
            string inputPath = options["--input"];
            string defsPath = options["--defs"];
            string outputPath = options["--output"];

            if (!File.Exists(inputPath)) throw new FileNotFoundException($"Input regulation not found: {inputPath}");
            if (!Directory.Exists(defsPath)) throw new DirectoryNotFoundException($"Paramdefs directory not found: {defsPath}");

            Console.WriteLine($"[RegTool] Inspecting regulation for installed gear: {inputPath}...");
            BND4 regBnd = RegulationDecryptor.DecryptERRegulation(inputPath);

            var protectorFile = regBnd.Files.FirstOrDefault(f => Path.GetFileNameWithoutExtension(f.Name).Equals("EquipParamProtector", StringComparison.OrdinalIgnoreCase));
            var weaponFile = regBnd.Files.FirstOrDefault(f => Path.GetFileNameWithoutExtension(f.Name).Equals("EquipParamWeapon", StringComparison.OrdinalIgnoreCase));

            if (protectorFile == null || weaponFile == null)
            {
                throw new InvalidOperationException("EquipParamProtector or EquipParamWeapon not found inside regulation.bin");
            }

            string protectorDefPath = Path.Combine(defsPath, "EquipParamProtector.xml");
            string weaponDefPath = Path.Combine(defsPath, "EquipParamWeapon.xml");

            var protectorDef = PARAMDEF.XmlDeserialize(protectorDefPath, false, false);
            var weaponDef = PARAMDEF.XmlDeserialize(weaponDefPath, false, false);

            var protectorParam = PARAM.Read(protectorFile.Bytes);
            protectorParam.ApplyParamdef(protectorDef);

            var weaponParam = PARAM.Read(weaponFile.Bytes);
            weaponParam.ApplyParamdef(weaponDef);

            var moddedProtectors = new List<object>();
            var moddedWeapons = new List<object>();

            // 1. Scan Protectors (0=Head, 1=Body, 2=Arms, 3=Legs)
            foreach (var row in protectorParam.Rows)
            {
                bool isModded = row.ID >= 8000000 || (row.Name != null && (row.Name.Contains("[LF]") || row.Name.Contains("[EF]")));
                if (!isModded) continue;

                int category = 0;
                var cell = row["protectorCategory"];
                if (cell != null && cell.Value != null)
                {
                    category = Convert.ToInt32(cell.Value);
                }

                string name = string.IsNullOrWhiteSpace(row.Name) ? $"Modded Protector {row.ID}" : row.Name.Replace("[LF]", "").Replace("[EF]", "").Trim();
                moddedProtectors.Add(new
                {
                    id = row.ID,
                    name = name,
                    category = category
                });
            }

            // 2. Scan Weapons
            foreach (var row in weaponParam.Rows)
            {
                bool isModded = row.ID >= 8000000 || (row.Name != null && (row.Name.Contains("[LF]") || row.Name.Contains("[EF]")));
                if (!isModded) continue;

                int wepType = 0;
                var cell = row["wepType"];
                if (cell != null && cell.Value != null)
                {
                    wepType = Convert.ToInt32(cell.Value);
                }

                string name = string.IsNullOrWhiteSpace(row.Name) ? $"Modded Weapon {row.ID}" : row.Name.Replace("[LF]", "").Replace("[EF]", "").Trim();
                moddedWeapons.Add(new
                {
                    id = row.ID,
                    name = name,
                    wep_type = wepType
                });
            }

            var catalog = new
            {
                regulation_path = inputPath,
                modded_protectors_count = moddedProtectors.Count,
                modded_weapons_count = moddedWeapons.Count,
                modded_protectors = moddedProtectors,
                modded_weapons = moddedWeapons
            };

            string json = JsonSerializer.Serialize(catalog, new JsonSerializerOptions { WriteIndented = true });
            
            string? outDir = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(outDir) && !Directory.Exists(outDir))
            {
                Directory.CreateDirectory(outDir);
            }

            File.WriteAllText(outputPath, json);
            Console.WriteLine($"[RegTool] Gear inspection complete. Found {moddedProtectors.Count} modded protectors and {moddedWeapons.Count} modded weapons.");
        }
    }
}
