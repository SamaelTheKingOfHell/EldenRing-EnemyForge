# EnemyForge UI Components

Modular Qt desktop interface presentation components, styling definitions, parameter schema, and inspectors.
Adheres to `[CS-MODULAR]`, `[CS-DECOUPLE]`, `[CS-GRANULARITY]`, and `[CS-DEBUG]`.

## Modules

| Module | Component | Purpose |
| :--- | :--- | :--- |
| [`INDEX.md`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/INDEX.md) | - | Index and architectural documentation for UI modules. |
| [`theme.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/theme.py) | `DARK_SOULS_QSS` | Dark Souls / Elden Ring themed QSS stylesheet and color palette constants. |
| [`param_schema.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/param_schema.py) | `ParamSchema` | Typed parameter metadata descriptors decoupling schema definitions from UI layouts. |
| [`param_widget_factory.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/param_widget_factory.py) | `ParamWidgetFactory` | Data-driven factory constructing styled parameter cards and controls. |
| [`preset_inspector.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/preset_inspector.py) | `PresetInspectorWidget` | Interactive dual-tab inspector for discovered enemy presets, equipment, and world encounters. |
| [`prototype_card.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/prototype_card.py) | `PrototypeCard` | Dedicated card and asynchronous worker for the Crossbreed Priscilla DS1 porting pipeline. |
| [`console_drawer.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/console_drawer.py) | `ConsoleDrawer` | Floating developer console drawer displaying real-time system logs with polling. |
| [`forge_worker.py`](file:///d:/The%20Order%27s%20Operations/Projects/modding/FromSoftware/Elden%20Ring/EnemyForge/src/ui/forge_worker.py) | `ForgeWorker` | Background worker thread executing encounter assignment and regulation injection. |
