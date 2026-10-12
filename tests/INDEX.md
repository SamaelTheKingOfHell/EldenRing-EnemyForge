# PhantomForge Automated Test Suite

Test suite verifying core domain models, preset loaders, collision-free ID allocators, carried loot table builders, world encounter placers, regulation patching, and localization string parity.

Adheres to `[CS-NO-MOCK]`, `[CS-LOCALIZATION]`, and `[CS-STABILITY]`.

## Test Modules Index

| File | Target Tested | Verification Scope |
| :--- | :--- | :--- |
| [`test_preset_loader.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_preset_loader.py) | `PresetLoader` | Discovers built-in templates and verifies carried equipment extraction. |
| [`test_phantom_builder.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_phantom_builder.py) | `PhantomBuilder` | Verifies specification building and **guaranteed carried loot drop tables (`ItemLotParam_enemy`)**. |
| [`test_id_allocator.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_id_allocator.py) | `IdAllocator` | Verifies sequential non-colliding ID generation across all parameter tables. |
| [`test_world_placer.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_world_placer.py) | `WorldPlacer` | Verifies encounter mapping across Thematic Regional, Roaming Invasions, and Chaos modes. |
| [`test_backup_and_manifest.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_backup_and_manifest.py) | `BackupManager`, `ManifestStore` | Verifies SHA-256 backup creation, restore, and manifest persistence. |
| [`test_localization.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_localization.py) | Localization Catalogs | Enforces mandatory `[CS-LOCALIZATION]` 100% key parity between `en.json` and `pt_br.json`. |
| [`test_regtool_integration.py`](file:///Z:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/PhantomForge/tests/test_regtool_integration.py) | `RegulationManager`, `RegTool` | End-to-end integration test verifying real regulation patching and carried loot drop table injection. |
