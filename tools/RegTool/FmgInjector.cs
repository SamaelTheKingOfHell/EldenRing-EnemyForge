using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Service responsible for injecting phantom names into Elden Ring FMG message archives.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class FmgInjector
    {
        public record PhantomNameEntry(
            int NpcId,
            string Name
        );

        public static int InjectPhantomNames(
            BND4 msgBnd,
            List<PhantomNameEntry> phantomNames)
        {
            var fmgFileCache = new Dictionary<string, (FMG Fmg, BinderFile File)>(StringComparer.OrdinalIgnoreCase);

            foreach (var file in msgBnd.Files)
            {
                string fileName = Path.GetFileName(file.Name);
                if (fileName.EndsWith(".fmg", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        var fmg = FMG.Read(file.Bytes);
                        fmgFileCache[fileName] = (fmg, file);
                    }
                    catch
                    {
                        // Skip unreadable files
                    }
                }
            }

            int injectedCount = 0;
            // Target FMG files for NPC names in Elden Ring
            string[] targetFmgNames = { "NpcName.fmg", "NPCName.fmg", "Title.fmg" };

            foreach (var targetName in targetFmgNames)
            {
                var kvp = fmgFileCache.FirstOrDefault(f => string.Equals(f.Key, targetName, StringComparison.OrdinalIgnoreCase));
                if (kvp.Value.Fmg != null)
                {
                    var fmg = kvp.Value.Fmg;
                    foreach (var entry in phantomNames)
                    {
                        if (string.IsNullOrWhiteSpace(entry.Name)) continue;

                        var existingEntry = fmg.Entries.FirstOrDefault(e => e.ID == entry.NpcId);
                        if (existingEntry != null)
                        {
                            existingEntry.Text = entry.Name;
                        }
                        else
                        {
                            fmg.Entries.Add(new FMG.Entry(entry.NpcId, entry.Name));
                        }
                        injectedCount++;
                    }

                    kvp.Value.File.Bytes = fmg.Write();
                    Console.WriteLine($"[FmgInjector] Injected {phantomNames.Count} phantom name(s) into '{targetName}'.");
                }
            }

            return injectedCount;
        }
    }
}
