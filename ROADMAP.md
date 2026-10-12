# PhantomForge: Development Roadmap

## Phase 1: Core Engine & Data Foundations (Completed)
- [x] Initialized standalone Git repository in `Projects/modding/FromSoftware/Elden Ring/PhantomForge`.
- [x] Established domain models (`CharacterPreset`, `EquipmentLoadout`, `WorldEncounter`, `PhantomEnemy`).
- [x] Implemented `PresetLoader` supporting built-in templates and `input_presets/` dropzone.
- [x] Implemented `IdAllocator` for collision-free partitioning (`9500000+` range).
- [x] Built curated collection of 8 legendary character presets across distinct archetypes.
- [x] Built world encounters database spanning Limgrave, Liurnia, Caelid, Altus, and Mountaintops.

## Phase 2: Carried Loot & Regulation Patching (Completed)
- [x] Developed `PhantomBuilder` extracting carried gear into `ItemLotParam_enemy` rows.
- [x] Built C# RegTool (.NET 9) with `RegulationDecryptor`, `PhantomInjector`, and `LootInjector`.
- [x] Resolved .NET 9 SDK toolchain integration and environment resolution.
- [x] Incorporated 16-bit row limit validation (`ushort.MaxValue`) and cell type coercion (`ParamHelper.cs`).
- [x] Implemented `BackupManager` with timestamped snapshots and SHA-256 verification.
- [x] Implemented `ManifestStore` for 1-click clean uninstallation.

## Phase 3: Desktop UI & Localization (Completed)
- [x] Built Souls-themed dashboard (obsidian slate `#08090d`, phantom crimson `#dc2626`, antique gold `#c5a059`).
- [x] Interactive preset inspector cards displaying carried loot drops.
- [x] World encounter placement table and settings drawer.
- [x] Floating real-time developer console (`[CS-DEBUG]`).
- [x] Centralized English and Portuguese (BR) localization catalogs (`[CS-LOCALIZATION]`).

## Phase 4: Automated Verification & Expansion (In Progress)
- [x] Unit test suite verifying preset loading, carried loot generation, and ID allocation.
- [x] Localization key parity test (`[CS-LOCALIZATION]`).
- [x] Regulation patching integration test.
- [ ] Future: Custom voice archetype assignment.
- [ ] Future: Direct integration with character creation save file (.sl2 / .co2) preset extraction.
