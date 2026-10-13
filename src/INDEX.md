# EnemyForge Core Engine (src)

Core engine modules powering character preset ingestion, collision-free ID partitioning, world encounter mapping, regulation patching, backup safety, and the web application server.

Adheres to `[CS-MODULAR]`, `[CS-DECOUPLE]`, `[CS-GRANULARITY]`, and `[CS-DEBUG]`.

## Source Modules

| File | Purpose |
| :--- | :--- |
| [`models.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/models.py) | Data contracts: `CharacterPreset`, `EquipmentLoadout`, `WorldEncounter`, `EnemyInstance`, `EnemyForgeConfig`, and `EnemyForgeManifest`. |
| [`logger.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/logger.py) | Centralized thread-safe logging and in-memory log buffer for the real-time UI console (`[CS-DEBUG]`). |
| [`preset_loader.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/preset_loader.py) | Discovers, parses, and validates `.json` preset files from `input_presets/` and `data/presets/`. |
| [`id_allocator.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/id_allocator.py) | Allocates collision-free IDs across `NpcParam` (9500000+), `ChrAsmParam` (9510000+), `FaceParam` (9520000+), and `ItemLotParam_enemy` (9530000+). |
| [`world_placer.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/world_placer.py) | Maps enemies to world encounters based on selected `PlacementMode` (`Thematic Regional`, `Roaming Invasions`, `Champion Duels`, `Chaos Expedition`). |
| [`enemy_builder.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/enemy_builder.py) | Builds the unified regulation patch spec and **extracts all carried equipment into drop tables (`ItemLotParam_enemy`)**. |
| [`phantom_builder.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/phantom_builder.py) | Backward-compatible forwarder to `enemy_builder.py`. |
| [`backup_manager.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/backup_manager.py) | Manages timestamped pre-write backups (`regulation.bin.bak_YYYYMMDD_HHMMSS`) and pristine vanilla fallback with SHA-256 verification. |
| [`manifest_store.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/manifest_store.py) | Tracks all injected row IDs in `enemyforge_manifest.json` enabling 1-click clean uninstallation. |
| [`regulation_manager.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/regulation_manager.py) | Coordinates backup creation, executes `RegTool.dll` CLI, verifies outputs, handles fallback, and coordinates 1-click rollback. |
| [`server.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/server.py) | Pure standard library HTTP server and REST API for the modern Souls desktop dashboard. |
