# EnemyForge: Repository Index

Cross-platform desktop application and mod engine for *Elden Ring* that ingests character presets, spawns them as hostile humanoid roaming enemies, duelists, and invader encounters across the Lands Between, and guarantees that defeating them drops the exact weapons, shields, and armor that they carry.

Adheres strictly to the guidelines of The Order (`[CS-MODULAR]`, `[CS-DECOUPLE]`, `[CS-INDEXING]`, `[CS-LOCALIZATION]`, `[CS-DEBUG]`, `[CS-NO-MOCK]`).

## Directory & File Structure

| Path / File | Purpose |
| :--- | :--- |
| [`README.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/README.md) | Main project overview, architecture, quick start, and usage documentation. |
| [`OBJECTIVE.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/OBJECTIVE.md) | Architectural invariants, mission statement, and core requirements. |
| [`ROADMAP.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/ROADMAP.md) | Development roadmap, milestones, and release statuses. |
| [`INDEX.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/INDEX.md) | Root repository navigation and inventory. |
| [`run_enemyforge.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/run_enemyforge.py) | Application launcher supporting interactive web UI, headless CLI, and instant 1-click rollback. |
| [`run_phantomforge.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/run_phantomforge.py) | Backwards-compatible forwarder to `run_enemyforge.py`. |
| [`rebuild_regtool.bat`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/rebuild_regtool.bat) | Batch script to build the C# RegTool (.NET 9) with environment configuration. |
| [`config.json`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/config.json) | Default generator and UI configuration. |
| [`src/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/INDEX.md) | Python core engine (preset loading, world placement, carried loot tables, regulation orchestration). |
| [`ui/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/ui/INDEX.md) | Modern Souls-themed interactive desktop dashboard and developer console. |
| [`data/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/data/INDEX.md) | Built-in character presets, fallback base game regulation template, world encounters, and localization catalogs. |
| [`input_presets/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/input_presets/INDEX.md) | User dropzone for custom character preset JSON files. |
| [`tools/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tools/INDEX.md) | Native tools and compilers, including C# RegTool and vendor libraries. |
| [`backups/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/backups/INDEX.md) | Timestamped pre-write backups and pristine vanilla fallback snapshots with SHA-256 verification. |
| [`tests/`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/INDEX.md) | Automated unit and integration test suite (`[CS-NO-MOCK]`). |
| [`ELDEN_RING_ORIGINAL_MONSTER_CREATION_RESEARCH_2026-10-12.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/ELDEN_RING_ORIGINAL_MONSTER_CREATION_RESEARCH_2026-10-12.md) | Canonical research on original monster creation, Havok rigging, TAE timelines, and AI. |
| [`FROM_SOFTWARE_ENEMY_PORTING_RESEARCH_2026-10-12.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/FROM_SOFTWARE_ENEMY_PORTING_RESEARCH_2026-10-12.md) | Canonical research on porting enemies and bosses from Dark Souls 1, 2, and 3 into Elden Ring. |
