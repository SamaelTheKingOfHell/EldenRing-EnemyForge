# RegTool: Regulation & Enemy Injection CLI

Command-line utility in C# (.NET 9) for decrypting Elden Ring `regulation.bin`, inspecting installed/modded gear sets, injecting character preset enemies as active humanoid enemies (`NpcParam`, `CharaInitParam`, `FaceParam`), automatically generating carried loot drop tables (`ItemLotParam_enemy`), injecting FMG enemy names, and re-encrypting with AES-256.

Adheres to `[CS-MODULAR]`, `[CS-GRANULARITY]`, and `[CS-DECOUPLE]`.

## Source Modules

| File | Class / Component | Purpose |
| :--- | :--- | :--- |
| [`Program.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/Program.cs) | `Program` | Entry point, CLI argument parsing, and command routing (`patch`, `verify`, `inspect-gear`). |
| [`PatchService.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/PatchService.cs) | `PatchService` | Regulation decryption, paramdef loading, patch orchestration, and AES-256 re-encryption. |
| [`EnemyInjector.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/EnemyInjector.cs) | `EnemyInjector` | Clones and configures `NpcParam`, `CharaInitParam`, and `FaceParam` rows for humanoid enemies. |
| [`LootInjector.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/LootInjector.cs) | `LootInjector` | Generates `ItemLotParam_enemy` rows ensuring enemies drop the exact gear they carry. |
| [`GearInspectorService.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/GearInspectorService.cs) | `GearInspectorService` | Decrypts and audits regulation files to identify installed and custom modded armor sets and weapons. |
| [`FmgInjector.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/FmgInjector.cs) | `FmgInjector` | Injects localized enemy names into `NpcName.fmg` within message archives. |
| [`DiagnosticService.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/DiagnosticService.cs) | `DiagnosticService` | Decrypts and audits regulation files to verify required parameter presence. |
| [`ParamHelper.cs`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/ParamHelper.cs) | `ParamHelper` | Safe PARAM cell value getters, setters, type coercion, and row cloning. |
| [`RegTool.csproj`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/RegTool/RegTool.csproj) | - | .NET 9 project configuration linking `SoulsFormats`. |
