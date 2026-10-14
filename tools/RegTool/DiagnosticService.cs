using System;
using System.IO;
using System.Linq;
using SoulsFormats;
using SoulsFormats.Cryptography;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Diagnostics and verification utility for Elden Ring regulation files and FMG archives.
    /// Adheres to [CS-DEBUG] and [CS-GRANULARITY].
    /// </summary>
    public static class DiagnosticService
    {
        public static void VerifyRegulation(string regPath)
        {
            if (!File.Exists(regPath))
            {
                Console.Error.WriteLine($"[RegTool ERROR] File not found: {regPath}");
                Environment.Exit(1);
            }

            try
            {
                Console.WriteLine($"[RegTool] Decrypting regulation: {regPath}...");
                BND4 regBnd = RegulationDecryptor.DecryptERRegulation(regPath);
                Console.WriteLine($"[RegTool] Successfully decrypted regulation. BND4 format: {regBnd.Format}, files: {regBnd.Files.Count}");

                var paramFiles = regBnd.Files.Where(f => f.Name.EndsWith(".param", StringComparison.OrdinalIgnoreCase)).ToList();
                Console.WriteLine($"[RegTool] Found {paramFiles.Count} parameter files inside regulation.");

                string[] keyParams = { "NpcParam", "CharaInitParam", "FaceParam", "ItemLotParam_enemy" };
                foreach (var kp in keyParams)
                {
                    var file = paramFiles.FirstOrDefault(f => Path.GetFileNameWithoutExtension(f.Name).Equals(kp, StringComparison.OrdinalIgnoreCase));
                    if (file != null)
                    {
                        Console.WriteLine($"  ✓ {kp} present ({file.Bytes.Length} bytes)");
                        if (kp == "NpcParam")
                        {
                            var p = PARAM.Read(file.Bytes);
                            string defXml = Path.Combine(Path.GetDirectoryName(regPath)!, "..", "..", "..", "..", "..", "..", "..", "The Order's Operations", "Projects", "modding", "FromSoftware", "Elden Ring", "EnemyForge", "tools", "vendor", "Paramdex", "ER", "Defs", "NpcParam.xml");
                            if (!File.Exists(defXml)) defXml = @"D:\The Order's Operations\Projects\modding\FromSoftware\Elden Ring\EnemyForge\tools\vendor\Paramdex\ER\Defs\NpcParam.xml";
                            if (File.Exists(defXml))
                            {
                                var def = PARAMDEF.XmlDeserialize(defXml, false, false);
                                p.ApplyParamdef(def);
                                var nerijus = p.Rows.FirstOrDefault(r => r.ID == 543430000);
                                if (nerijus != null)
                                {
                                    Console.WriteLine($"  [Nerijus NpcParam cells]:");
                                    foreach (var c in nerijus.Cells)
                                    {
                                        if (c.Value != null && c.Value.ToString() != "0" && c.Value.ToString() != "-1" && c.Value.ToString() != "False")
                                        {
                                            Console.WriteLine($"     {c.Def.InternalName} = {c.Value}");
                                        }
                                    }
                                }
                            }
                        }
                        else if (kp == "CharaInitParam")
                        {
                            var cp = PARAM.Read(file.Bytes);
                            Console.WriteLine($"  [CharaInitParam] Rows count: {cp.Rows.Count}. Min: {cp.Rows.Min(r => r.ID)}, Max: {cp.Rows.Max(r => r.ID)}");
                            var nerijusChr = cp.Rows.FirstOrDefault(r => r.ID == 543430000 || r.ID == 543430010);
                            Console.WriteLine($"  Nerijus in CharaInitParam: {(nerijusChr != null ? nerijusChr.ID.ToString() : "Not found")}");
                            var namedChr = cp.Rows.Where(r => !string.IsNullOrEmpty(r.Name)).Take(10).ToList();
                            foreach (var r in namedChr) Console.WriteLine($"     ChrInit ID: {r.ID}, Name: '{r.Name}'");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"  ✗ {kp} MISSING");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[RegTool ERROR] Verification failed: {ex.GetType().Name}: {ex.Message}");
                Environment.Exit(1);
            }
        }

        public static void InspectMap(string msbPath)
        {
            if (!File.Exists(msbPath))
            {
                Console.Error.WriteLine($"[RegTool ERROR] Map file not found: {msbPath}");
                Environment.Exit(1);
            }

            try
            {
                Console.WriteLine($"[RegTool] Reading MSB: {msbPath}...");
                MSBE msb = MSBE.Read(msbPath);
                Console.WriteLine($"[RegTool] Models: {msb.Models.GetEntries().Count}, Enemies: {msb.Parts.Enemies.Count}, Regions: {msb.Regions.GetEntries().Count}");
                foreach (var r in msb.Regions.GetEntries().Take(20))
                {
                    Console.WriteLine($"  Region '{r.Name}': Pos=({r.Position.X:F1}, {r.Position.Y:F1}, {r.Position.Z:F1})");
                }
                foreach (var e in msb.Parts.Enemies)
                {
                    Console.WriteLine($"  Enemy '{e.Name}': Model='{e.ModelName}', NPCParamID={e.NPCParamID}, ThinkParamID={e.ThinkParamID}, CharaInitID={e.CharaInitID}, Pos=({e.Position.X:F1}, {e.Position.Y:F1}, {e.Position.Z:F1})");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[RegTool ERROR] Map inspection failed: {ex.GetType().Name}: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
}
