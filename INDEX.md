# PhantomForge: Repository Index

Cross-platform desktop application and mod engine for *Elden Ring* that ingests character presets, spawns them as hostile humanoid phantoms and roaming NPC enemies across the Lands Between, and guarantees that defeating them drops the exact weapons, shields, and armor that they carry.

Adheres strictly to the guidelines of The Order (`[CS-MODULAR]`, `[CS-DECOUPLE]`, `[CS-INDEXING]`, `[CS-LOCALIZATION]`, `[CS-DEBUG]`, `[CS-NO-MOCK]`).

## Directory & File Structure

| Path / File | Purpose |
| :--- | :--- |
| [`README.md`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/README.md) | Main project overview, architecture, quick start, and usage documentation. |
| [`OBJECTIVE.md`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/OBJECTIVE.md) | Architectural invariants, mission statement, and core requirements. |
| [`ROADMAP.md`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/ROADMAP.md) | Development roadmap, milestones, and release statuses. |
| [`INDEX.md`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/INDEX.md) | Root repository navigation and inventory. |
| [`run_phantomforge.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/run_phantomforge.py) | Application launcher supporting interactive web UI or headless CLI execution. |
| [`rebuild_regtool.bat`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/rebuild_regtool.bat) | Batch script to build the C# RegTool (.NET 9) with environment configuration. |
| [`config.json`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/config.json) | Default generator and UI configuration. |
| [`src/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/src/INDEX.md) | Python core engine (preset loading, world placement, carried loot tables, regulation orchestration). |
| [`ui/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/ui/INDEX.md) | Modern Souls-themed interactive desktop dashboard and developer console. |
| [`data/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/data/INDEX.md) | Built-in character presets, world encounters database, and localization catalogs. |
| [`input_presets/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/input_presets/INDEX.md) | User dropzone for custom character preset JSON files. |
| [`tools/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tools/INDEX.md) | Native tools and compilers, including C# RegTool and vendor libraries. |
| [`backups/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/backups/INDEX.md) | Timestamped pre-write backups of regulation files with SHA-256 verification. |
| [`tests/`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/INDEX.md) | Automated unit and integration test suite (`[CS-NO-MOCK]`). |
