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
    }
}
