using System;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Text.Json;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Injects enemy entities directly into Elden Ring MSB map files (m60_XX_XX_00.msb.dcx).
    /// Ensures enemies physically spawn in the live world at designated world coordinates.
    /// Adheres to [CS-MODULAR], [CS-SAFETY], and [CS-GRANULARITY].
    /// </summary>
    public static class MapInjectorService
    {
        public static bool InjectMapEnemies(
            string sourceMsbPath,
            string targetMsbPath,
            JsonElement enemySpec)
        {
            if (!File.Exists(sourceMsbPath))
            {
                Console.WriteLine($"[RegTool WARNING] Base map MSB not found: {sourceMsbPath}");
                return false;
            }

            try
            {
                Console.WriteLine($"[RegTool] Loading MSB map from: {sourceMsbPath}...");
                MSBE msb = MSBE.Read(sourceMsbPath);

                string name = enemySpec.TryGetProperty("name", out var n) ? n.GetString() ?? "World Enemy" : "World Enemy";
                string enemyPartName = name.Replace(" ", "_").Replace("-", "_");
                string modelName = enemySpec.TryGetProperty("model_name", out var m) ? m.GetString() ?? "c0000" : "c0000";
                int npcId = enemySpec.GetProperty("npc_param_id").GetInt32();
                int thinkId = enemySpec.TryGetProperty("think_param_id", out var th) ? th.GetInt32() : 100000;
                int chrInitId = enemySpec.GetProperty("chr_asm_id").GetInt32();

                // 1. Ensure Model exists in msb.Models.Enemies
                if (!msb.Models.Enemies.Any(e => string.Equals(e.Name, modelName, StringComparison.OrdinalIgnoreCase)))
                {
                    msb.Models.Enemies.Add(new MSBE.Model.Enemy { Name = modelName });
                    Console.WriteLine($"[RegTool] Registered model '{modelName}' in MSB Models table.");
                }

                // 2. Resolve World Placement Coordinates
                float posX = 135.0f, posY = 14.0f, posZ = 130.0f;
                if (enemySpec.TryGetProperty("world_placement", out var wp) && wp.TryGetProperty("coordinates", out var coords))
                {
                    if (coords.TryGetProperty("x", out var x)) posX = (float)x.GetDouble();
                    if (coords.TryGetProperty("y", out var y)) posY = (float)y.GetDouble();
                    if (coords.TryGetProperty("z", out var z)) posZ = (float)z.GetDouble();
                }

                Vector3 targetPos = new Vector3(posX, posY, posZ);
                Vector3 targetRot = new Vector3(0.0f, -45.0f, 0.0f);

                // 3. Find template enemy for collision assignment
                var template = msb.Parts.Enemies.FirstOrDefault(e => e.ModelName == "c4200") ?? msb.Parts.Enemies.FirstOrDefault();
                string collisionName = template?.CollisionPartName ?? "";

                // 4. Inject or Update Enemy Part
                var existingPart = msb.Parts.Enemies.FirstOrDefault(e => string.Equals(e.Name, enemyPartName, StringComparison.OrdinalIgnoreCase));
                if (existingPart != null)
                {
                    existingPart.ModelName = modelName;
                    existingPart.NPCParamID = npcId;
                    existingPart.ThinkParamID = thinkId;
                    existingPart.CharaInitID = chrInitId;
                    existingPart.Position = targetPos;
                    existingPart.Rotation = targetRot;
                    Console.WriteLine($"[RegTool] Updated existing map part '{enemyPartName}'.");
                }
                else
                {
                    var newEnemy = new MSBE.Part.Enemy
                    {
                        Name = enemyPartName,
                        ModelName = modelName,
                        NPCParamID = npcId,
                        ThinkParamID = thinkId,
                        CharaInitID = chrInitId,
                        Position = targetPos,
                        Rotation = targetRot,
                        CollisionPartName = collisionName
                    };
                    msb.Parts.Enemies.Add(newEnemy);
                    Console.WriteLine($"[RegTool] Injected new map part '{enemyPartName}' at ({posX:F1}, {posY:F1}, {posZ:F1}) into MSB.");
                }

                // 5. Also update live world anchor enemy if base_enemy_id is provided
                if (enemySpec.TryGetProperty("base_enemy_id", out var baseElem) && baseElem.GetInt32() > 0)
                {
                    int baseEnemyId = baseElem.GetInt32();
                    var anchorEnemy = msb.Parts.Enemies.FirstOrDefault(e => e.NPCParamID == baseEnemyId);
                    if (anchorEnemy != null)
                    {
                        anchorEnemy.CharaInitID = chrInitId;
                        anchorEnemy.ModelName = modelName;
                        Console.WriteLine($"[RegTool] Synchronized anchor enemy '{anchorEnemy.Name}' (NPC {baseEnemyId}) with CharaInit {chrInitId}.");
                    }
                }

                // 6. Write target MSB file
                string? targetDir = Path.GetDirectoryName(targetMsbPath);
                if (!string.IsNullOrEmpty(targetDir) && !Directory.Exists(targetDir))
                {
                    Directory.CreateDirectory(targetDir);
                }

                Console.WriteLine($"[RegTool] Saving injected MSB to: {targetMsbPath}...");
                msb.Write(targetMsbPath);
                Console.WriteLine($"[RegTool] MSB map injection completed successfully!");
                return true;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[RegTool ERROR] Failed to inject MSB map: {ex.GetType().Name}: {ex.Message}");
                return false;
            }
        }
    }
}
