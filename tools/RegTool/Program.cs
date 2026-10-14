using System;
using System.Collections.Generic;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Command-line interface entry point for PhantomForge RegTool.
    /// Manages CLI routing, argument validation, and invocation.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class Program
    {
        public static int Main(string[] args)
        {
            if (args.Length == 0 || args[0] is "-h" or "--help")
            {
                PrintHelp();
                return 0;
            }

            string command = args[0].ToLowerInvariant();
            var options = ParseOptions(args, 1);

            try
            {
                switch (command)
                {
                    case "patch":
                        ValidateRequiredOptions(options, "--input", "--output", "--defs", "--spec");
                        PatchService.ExecutePatch(options);
                        return 0;

                    case "verify":
                        ValidateRequiredOptions(options, "--input");
                        DiagnosticService.VerifyRegulation(options["--input"]);
                        return 0;

                    case "inspect-gear":
                        ValidateRequiredOptions(options, "--input", "--defs", "--output");
                        GearInspectorService.InspectGear(options);
                        return 0;

                    case "inspect-map":
                        ValidateRequiredOptions(options, "--input");
                        DiagnosticService.InspectMap(options["--input"]);
                        return 0;

                    default:
                        Console.Error.WriteLine($"[RegTool ERROR] Unknown command: '{command}'");
                        PrintHelp();
                        return 1;
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[RegTool ERROR] {ex.Message}");
                if (ex.InnerException != null)
                {
                    Console.Error.WriteLine($"[RegTool INNER] {ex.InnerException.Message}");
                }
                return 1;
            }
        }

        private static Dictionary<string, string> ParseOptions(string[] args, int startIndex)
        {
            var options = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            for (int i = startIndex; i < args.Length; i++)
            {
                if (args[i].StartsWith("--") && i + 1 < args.Length && !args[i + 1].StartsWith("--"))
                {
                    options[args[i]] = args[i + 1];
                    i++;
                }
            }
            return options;
        }

        private static void ValidateRequiredOptions(Dictionary<string, string> options, params string[] required)
        {
            foreach (var req in required)
            {
                if (!options.ContainsKey(req))
                {
                    throw new ArgumentException($"Missing required option: {req}");
                }
            }
        }

        private static void PrintHelp()
        {
            Console.WriteLine("PhantomForge Regulation Tool (RegTool)");
            Console.WriteLine("Usage:");
            Console.WriteLine("  RegTool patch --input <source_reg> --output <target_reg> --defs <paramdex_defs> --spec <phantom_spec.json> [--msg <msg_dir>]");
            Console.WriteLine("  RegTool verify --input <regulation.bin>");
            Console.WriteLine("  RegTool inspect-gear --input <regulation.bin> --defs <paramdex_defs> --output <gear_catalog.json>");
        }
    }
}
