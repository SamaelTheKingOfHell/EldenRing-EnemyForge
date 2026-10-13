# Cross-Game Extraction & Porting Subsystem (src/cross_game)

This module implements the cross-game entity extraction, asset decryption, and conversion pipeline for porting enemies from legacy FromSoftware titles (*Dark Souls 1 PTDE*, *Dark Souls 2 SotFS*, *Dark Souls 3*) into *Elden Ring*.

Adheres strictly to `[CS-MODULAR]`, `[CS-DECOUPLE]`, `[CS-NO-MOCK]`, and copyright preservation guidelines (requires local legal installation of source games; zero redistribution of copyrighted assets).

## Source Modules

| File | Purpose |
| :--- | :--- |
| [`ds1_extractor.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/cross_game/ds1_extractor.py) | Zero-dependency BHD5/BDT reader and extractor for local *Dark Souls: Prepare to Die Edition* installations. |
| [`priscilla_builder.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/cross_game/priscilla_builder.py) | Synthesizes Crossbreed Priscilla into an Elden Ring entity with boss stats, Lifehunt Scythe, and carried loot. |
| [`prototype_orchestrator.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/cross_game/prototype_orchestrator.py) | Orchestrates the end-to-end pipeline: extraction, regulation injection, and world placement at the tutorial cave exit. |
