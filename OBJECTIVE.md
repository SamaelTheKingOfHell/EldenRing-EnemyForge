# EnemyForge: Objective & Mission Statement

## 1. Mission Statement

Develop a cross-platform desktop application and mod engine for *Elden Ring* that breathes life into custom character presets by spawning them as hostile humanoid roaming enemies, duelists, minibosses, and red invader encounters in the Lands Between.

Crucially, **every enemy drops the exact weapons, shields, catalysts, and armor that they carry in their build**, rewarding the player directly for overcoming difficult player-character encounters.

---

## 2. Core Architectural Invariants

1. **Preset Ingestion & Representation**:
   - Ingests player character presets (`.json`) specifying complete fashion souls, weapon loadouts, stats, gender, hair, and combat styles.
   - Built-in legendary templates provided out of the box (Bloody Finger Eleanor, Crucible Severus, Carian Spellblade Laura, Frenzied Zealot Ignis, Black Knife Vesper, Juggernaut Gorgon, Death Cultist Moros, Paladin Aurelius).
   - Allows choosing between natural flesh-and-blood Tarnished models (`sp_effect_aura_id = 0`) and spectral/invader auras (`sp_effect_aura_id = 7000+`).

2. **Carried Loot Guarantee ("They should drop the loot that they carry")**:
   - The engine automatically extracts every non-zero item from the enemy's `ChrAsmParam` (head, body, arms, legs, right-hand weapons, left-hand weapons, shields).
   - Generates an `ItemLotParam_enemy` row that assigns 100% drop probability (or user-tuned chance) for every single item the enemy carries.
   - Defeating the enemy guarantees earning their complete arsenal and armor set.

3. **World Placement Engine**:
   - Organically distributes enemies across the Lands Between according to selectable placement strategies:
     - `Thematic Regional`: Matches enemy power and gear tier to regional danger (Limgrave -> Liurnia -> Caelid -> Altus -> Mountaintops).
     - `Roaming Invasions`: Injects enemies as hostile red invaders near churches and exploration bottlenecks.
     - `Champion Duels`: Places enemies as guardians at crossroads and arenas.
     - `Chaos Expedition`: Shuffles enemies across valid world encounter points.

4. **Base File Fallback & Rollback Safety**:
   - Automatic Base Game Fallback: If no active `regulation.bin` is designated by the user, the engine seamlessly uses the base game template in `data/regulation.bin` copied from the Steam installation directory.
   - 1-Click Complete Rollback: Supports immediate restoration to the pristine vanilla state (`--rollback` CLI flag and `/api/rollback` endpoint) backed by SHA-256 verified snapshots.
   - 16-bit row limit guard: Explicitly validates table size against `ushort.MaxValue` (65,535) before serialization.
   - Robust type coercion in `ParamHelper.cs` to prevent invalid cast exceptions across primitive cell types.
   - Collision-free ID partitioning in the safe `9500000+` range for `NpcParam`, `ChrAsmParam`, `FaceParam`, and `ItemLotParam_enemy`.
   - Reversible manifest store (`enemyforge_manifest.json`) tracking all injected rows for clean uninstallation.

5. **Universal Standards Compliance**:
   - `[CS-LOCALIZATION]`: Zero hardcoded user-facing strings; dual English and Portuguese (BR) catalogs with automated 100% key parity verification.
   - `[CS-DEBUG]`: Centralized structured logging and floating real-time console drawer.
   - `[CS-MODULAR]`: Single-responsibility files under 300 lines with zero cross-module coupling.
