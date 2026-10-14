using System;
using System.IO;
using System.Linq;
using System.Numerics;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Relocates a named enemy within an MSB map file to new world coordinates.
    /// Used for dynamic positioning and debug testing during live gameplay.
    /// Adheres to [CS-MODULAR] and [CS-SAFETY].
    /// </summary>
    public static class RelocateEnemyService
    {
        public static bool Relocate(string msbPath, string enemyName, float x, float y, float z)
        {
            if (!File.Exists(msbPath))
            {
                Console.Error.WriteLine($"[RegTool ERROR] MSB file not found: {msbPath}");
                return false;
            }

            try
            {
                Console.WriteLine($"[RegTool] Reading MSB: {msbPath}...");
                MSBE msb = MSBE.Read(msbPath);

                var enemy = msb.Parts.Enemies.FirstOrDefault(e => string.Equals(e.Name, enemyName, StringComparison.OrdinalIgnoreCase))
                         ?? msb.Parts.Enemies.FirstOrDefault(e => e.Name.IndexOf(enemyName, StringComparison.OrdinalIgnoreCase) >= 0);

                if (enemy == null)
                {
                    Console.Error.WriteLine($"[RegTool ERROR] Enemy '{enemyName}' not found in MSB: {msbPath}");
                    return false;
                }

                Vector3 oldPos = enemy.Position;
                enemy.Position = new Vector3(x, y, z);
                Console.WriteLine($"[RegTool] Relocated '{enemy.Name}' from ({oldPos.X:F1}, {oldPos.Y:F1}, {oldPos.Z:F1}) to ({x:F1}, {y:F1}, {z:F1})");

                msb.Write(msbPath);
                Console.WriteLine($"[RegTool] Successfully saved relocated enemy to {msbPath}");
                return true;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[RegTool ERROR] Failed to relocate enemy: {ex.Message}");
                return false;
            }
        }
    }
}
