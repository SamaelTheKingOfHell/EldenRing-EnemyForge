# RegTool: Regulation & Phantom Injection CLI

Command-line utility in C# (.NET 9) for decrypting Elden Ring `regulation.bin`, injecting character preset phantoms as active humanoid enemies (`NpcParam`, `CharaInitParam`, `FaceParam`), automatically generating carried loot drop tables (`ItemLotParam_enemy`), injecting FMG phantom names, and re-encrypting with AES-256.

Adheres to `[CS-MODULAR]`, `[CS-GRANULARITY]`, and `[CS-DECOUPLE]`.

## Source Modules

| File | Class / Component | Purpose |
| :--- | :--- | :--- |
| [`Program.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/Program.cs) | `Program` | Entry point, CLI argument parsing, and command execution. |
| [`PatchService.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/PatchService.cs) | `PatchService` | Regulation decryption, paramdef loading, patch orchestration, and AES-256 re-encryption. |
| [`PhantomInjector.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/PhantomInjector.cs) | `PhantomInjector` | Clones and configures `NpcParam`, `CharaInitParam`, and `FaceParam` rows for character preset phantoms. |
| [`LootInjector.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/LootInjector.cs) | `LootInjector` | Generates `ItemLotParam_enemy` rows ensuring phantoms drop the exact gear they carry. |
| [`FmgInjector.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/FmgInjector.cs) | `FmgInjector` | Injects localized phantom names into `NpcName.fmg` within message archives. |
| [`DiagnosticService.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/DiagnosticService.cs) | `DiagnosticService` | Decrypts and audits regulation files to verify required parameter presence. |
| [`ParamHelper.cs`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/ParamHelper.cs) | `ParamHelper` | Safe PARAM cell value getters, setters, type coercion, and row cloning. |
| [`RegTool.csproj`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/RegTool/RegTool.csproj) | - | .NET 9 project configuration linking `SoulsFormats`. |
