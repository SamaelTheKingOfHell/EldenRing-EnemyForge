# EnemyForge Automated Test Suite

Test suite verifying core domain models, preset loaders, collision-free ID allocators, carried loot table builders, world encounter placers, regulation patching, cross-game asset extraction, and native Qt desktop application.

Adheres to `[CS-NO-MOCK]`, `[CS-LOCALIZATION]`, and `[CS-STABILITY]`.

## Test Modules Index

| File | Target Tested | Verification Scope |
| :--- | :--- | :--- |
| [`test_preset_loader.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_preset_loader.py) | `PresetLoader` | Discovers built-in templates and verifies carried equipment extraction. |
| [`test_phantom_builder.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_phantom_builder.py) | `PhantomBuilder` | Verifies specification building and **guaranteed carried loot drop tables (`ItemLotParam_enemy`)**. |
| [`test_id_allocator.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_id_allocator.py) | `IdAllocator` | Verifies sequential non-colliding ID generation across all parameter tables. |
| [`test_world_placer.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_world_placer.py) | `WorldPlacer` | Verifies encounter mapping across Thematic Regional, Roaming Invasions, and Chaos modes. |
| [`test_backup_and_manifest.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_backup_and_manifest.py) | `BackupManager`, `ManifestStore` | Verifies SHA-256 backup creation, restore, and manifest persistence. |
| [`test_localization.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_localization.py) | Localization Catalogs | Enforces mandatory `[CS-LOCALIZATION]` 100% key parity between `en.json` and `pt_br.json`. |
| [`test_regtool_integration.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_regtool_integration.py) | `RegulationManager`, `RegTool` | End-to-end integration test verifying real regulation patching and carried loot drop table injection. |
| [`test_priscilla_pipeline.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_priscilla_pipeline.py) | `DS1Extractor`, `PrototypeOrchestrator` | Verifies zero-dependency DS1 extraction, BHD5 hash matching, Priscilla encounter builder, and live injection. |
| [`test_qt_app.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/tests/test_qt_app.py) | `EnemyForgeMainWindow`, Qt UI | Headless unit testing for Qt window, preset inspector, prototype card, and console drawer. |
