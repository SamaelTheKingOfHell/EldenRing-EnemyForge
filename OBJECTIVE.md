# PhantomForge: Objective & Mission Statement

## 1. Mission Statement

Develop a cross-platform desktop application and mod engine for *Elden Ring* that breathes life into custom character presets by spawning them as hostile humanoid phantoms, roaming duelists, and red invader encounters in the Lands Between.

Crucially, **every phantom enemy drops the exact weapons, shields, catalysts, and armor that they carry in their build**, rewarding the player directly for overcoming difficult player-character encounters.

---

## 2. Core Architectural Invariants

1. **Preset Ingestion & Representation**:
   - Ingests player character presets (`.json`) specifying complete fashion souls, weapon loadouts, stats, gender, hair, and combat styles.
   - Built-in legendary templates provided out of the box (Bloody Finger Eleanor, Crucible Severus, Carian Spellblade Laura, Frenzied Zealot Ignis, Black Knife Vesper, Juggernaut Gorgon, Death Cultist Moros, Paladin Aurelius).

2. **Carried Loot Guarantee ("They should drop the loot that they carry")**:
   - The engine automatically extracts every non-zero item from the phantom's `ChrAsmParam` (head, body, arms, legs, right-hand weapons, left-hand weapons, shields).
   - Generates an `ItemLotParam_enemy` row that assigns 100% drop probability (or user-tuned chance) for every single item the phantom carries.
   - Defeating the phantom guarantees earning their complete arsenal and armor set.

3. **World Placement Engine**:
   - Organically distributes phantoms across the Lands Between according to selectable placement strategies:
     - `Thematic Regional`: Matches phantom power and gear tier to regional danger (Limgrave -> Liurnia -> Caelid -> Altus -> Mountaintops).
     - `Roaming Invasions`: Injects phantoms as hostile red invaders near churches and exploration bottlenecks.
     - `Champion Duels`: Places phantoms as guardians at crossroads and arenas.
     - `Chaos Expedition`: Shuffles phantoms across valid world encounter points.

4. **Engine & Regulation Safety (Lessons from LootForge)**:
   - 16-bit row limit guard: Explicitly validates table size against `ushort.MaxValue` (65,535) before serialization.
   - Robust type coercion in `ParamHelper.cs` to prevent invalid cast exceptions across primitive cell types.
   - Collision-free ID partitioning in the safe `9500000+` range for `NpcParam`, `ChrAsmParam`, `FaceParam`, and `ItemLotParam_enemy`.
   - Pre-write timestamped snapshots (`regulation.bin.bak_YYYYMMDD_HHMMSS`) with SHA-256 verification and 1-click clean restore.
   - Reversible manifest store (`phantomforge_manifest.json`) tracking all injected rows for clean uninstallation.

5. **Universal Standards Compliance**:
   - `[CS-LOCALIZATION]`: Zero hardcoded user-facing strings; dual English and Portuguese (BR) catalogs with automated 100% key parity verification.
   - `[CS-DEBUG]`: Centralized structured logging and floating real-time console drawer.
   - `[CS-MODULAR]`: Single-responsibility files under 300 lines with zero cross-module coupling.
