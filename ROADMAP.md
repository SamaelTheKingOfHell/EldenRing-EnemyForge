# EnemyForge: Development Roadmap

## Phase 1: Core Engine & Data Foundations (Completed)
- [x] Initialized standalone Git repository in `Projects/modding/FromSoftware/Elden Ring/EnemyForge`.
- [x] Established domain models (`CharacterPreset`, `EquipmentLoadout`, `WorldEncounter`, `EnemyInstance`).
- [x] Implemented `PresetLoader` supporting built-in templates and `input_presets/` dropzone.
- [x] Implemented `IdAllocator` for collision-free partitioning (`9500000+` range).
- [x] Built curated collection of 8 legendary character presets across distinct archetypes.
- [x] Built world encounters database spanning Limgrave, Liurnia, Caelid, Altus, and Mountaintops.

## Phase 2: Carried Loot, Fallback Ingestion & Rollback (Completed)
- [x] Developed `EnemyBuilder` extracting carried gear into `ItemLotParam_enemy` rows.
- [x] Built C# RegTool (.NET 9) with `RegulationDecryptor`, `EnemyInjector`, and `LootInjector`.
- [x] Integrated base game fallback from Steam Elden Ring directory (`data/regulation.bin`).
- [x] Implemented `BackupManager` with timestamped snapshots and SHA-256 verification.
- [x] Implemented `--rollback` CLI flag and 1-click `/api/rollback` endpoint for clean vanilla restore.
- [x] Implemented `ManifestStore` (`enemyforge_manifest.json`) for clean uninstallation.
- [x] 16-bit row limit validation (`ushort.MaxValue`) and cell type coercion (`ParamHelper.cs`).

## Phase 3: Desktop UI & Localization (Completed)
- [x] Souls-themed dashboard (obsidian slate `#08090d`, phantom crimson `#dc2626`, antique gold `#c5a059`).
- [x] Interactive preset inspector cards displaying carried loot drops.
- [x] World encounter placement table and settings drawer.
- [x] Floating real-time developer console (`[CS-DEBUG]`).
- [x] Centralized English and Portuguese (BR) localization catalogs (`[CS-LOCALIZATION]`).

## Phase 4: Automated Verification & Expansion (Active)
- [x] Unit test suite verifying preset loading, carried loot generation, and ID allocation.
- [x] Localization key parity test (`[CS-LOCALIZATION]`).
- [x] Regulation patching integration test.
- [x] Published public GitHub repository for community collaboration.
- [ ] Future: Custom voice archetype assignment.
- [ ] Future: Direct integration with character creation save file (.sl2 / .co2) preset extraction.

## Phase 5: The Monster Forge (Original Creature Creation & Host Rigging) (Research Phase)
- [x] Canonical research into FromSoftware Havok engine anatomy, FLVER v2, DummyPolys, and TAE timelines ([Research Document](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/ELDEN_RING_ORIGINAL_MONSTER_CREATION_RESEARCH_2026-10-12.md)).
- [x] Canonical research into porting enemies from Dark Souls 1, 2, and 3 into Elden Ring ([Research Document](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/FROM_SOFTWARE_ENEMY_PORTING_RESEARCH_2026-10-12.md)).
- [ ] Establish `CreatureArchetype` catalog in Python core (Quadrupeds `c4000`/`c4320`, Brutes `c4200`/`c4520`, Stalkers `c2010`, Dragons `c4700`).
- [ ] Automated standalone Chr ID allocator (`c9100` - `c9499`) with container cloning (`.chrbnd`, `.anibnd`, `.behbnd`).
- [ ] Creature Param Synthesizer: level-scaled `NpcParam`, elemental damage split generator for `AtkParam_Npc`, and `NpcThinkParam` aggression profiles.
- [ ] Thematic Monster Loot Forge: guaranteed boss remembrances, trophies, talismans, and signature creature drops in `ItemLotParam_enemy`.
- [ ] World Encounter Monster Placements: injecting standalone creature encounters across open world sectors via MSB Map Parts.
- [ ] Blender starter asset packs (.blend) with pre-rigged FromSoft skeletons and positioned DummyPolys for mod authors.
