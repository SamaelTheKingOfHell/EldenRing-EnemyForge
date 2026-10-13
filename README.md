# EnemyForge: Character Preset Enemy & Carried Loot Injector

**EnemyForge** is a cross-platform desktop application and mod engine for *Elden Ring* (Windows & Linux / Steam Deck). It transforms player character presets into formidable hostile humanoid roaming enemies, duelists, minibosses, and red invaders across the Lands Between, and **guarantees that every enemy drops the exact weapons, shields, and armor that they carry in their build**.

---

## Key Features

1. **Hostile Character Presets in the World**:
   - Ingests custom or built-in character presets (fashion souls, weapon arsenals, level scaling, and AI combat styles).
   - Generates authentic humanoid enemies (`c0000`) with level-scaled attributes, poise, runes, and optional flesh-and-blood models or spectral invader auras (`SpEffect 7000`).

2. **Carried Loot Drops (100% on Kill)**:
   - **"They should drop the loot that they carry"**: Defeating an enemy guarantees receiving every single piece of gear they wielded:
     - Head, Chest, Gauntlets, and Greaves armor pieces.
     - Primary and secondary right-hand weapons.
     - Left-hand weapons, shields, catalysts, and seals.
   - Automatically populates `ItemLotParam_enemy` rows linked to the enemy's `NpcParam.itemLotId_enemy`.

3. **Tactical World Placement Engine**:
   - **Thematic Regional**: Matches enemy strength and equipment tier to regional difficulty (Limgrave -> Liurnia -> Caelid -> Altus Plateau -> Mountaintops).
   - **Roaming Invasions**: Places enemies as hostile red invaders at landmark exploration bottlenecks.
   - **Champion Duels**: Positions enemies at crossroads and arena approaches.
   - **Chaos Expedition**: Shuffles enemies across valid world encounter coordinates.

4. **Base File Fallback & 1-Click Rollback**:
   - **Base Game Fallback**: If no active `regulation.bin` is designated, EnemyForge automatically falls back to the pristine base game `regulation.bin` in `data/regulation.bin`.
   - **1-Click Rollback**: Run `python run_enemyforge.py --rollback` or click Restore in the UI to instantly rollback the regulation to pristine vanilla state.
   - Timestamped pre-write regulation snapshots (`regulation.bin.bak_YYYYMMDD_HHMMSS`) with SHA-256 verification.
   - Reversible manifest (`enemyforge_manifest.json`) enabling 1-click clean uninstallation.

5. **Modern Souls-Themed GUI & Real-Time Diagnostics**:
   - Deep obsidian slate surfaces, phantom crimson accents, and antique gold highlights.
   - Floating circular developer console (`[CS-DEBUG]`) with live streamed diagnostics.
   - Full universal localization (`[CS-LOCALIZATION]`) supporting English and Brazilian Portuguese.

---

## Quick Start

### 1. Place Custom Presets (Optional)
Drop any custom `.json` character preset into `input_presets/`:

```json
{
  "preset_id": "my_duelist",
  "name": "Duelist Roger",
  "archetype": "Spellblade",
  "level": 90,
  "equipment": {
    "head_id": 400000,
    "body_id": 400100,
    "arms_id": 400200,
    "legs_id": 400300,
    "right_weapon_1_id": 3120000,
    "left_weapon_1_id": 33070000
  }
}
```

### 2. Launch EnemyForge
Run the launcher:

```bash
python run_enemyforge.py
```

Or run headlessly via CLI:

```bash
python run_enemyforge.py --cli
```

To rollback to base vanilla state at any time:

```bash
python run_enemyforge.py --rollback
```

---

## Project Structure

- `src/`: Python core engine (preset parsing, ID allocation, world encounters, backup manager, regulation coordinator).
- `tools/RegTool/`: Native C# (.NET 9) regulation reader, decryptor, and param injector built with SoulsFormatsNEXT.
- `data/`: Built-in archetype character presets, baseline game files, world encounters, and localization catalogs.
- `input_presets/`: User dropzone for custom character presets.
- `ui/`: Desktop Souls-themed interface with live WebSocket/HTTP event log streaming.
- `backups/`: Pre-write regulation snapshots with SHA-256 verification.
- `tests/`: Automated unit and integration test suite (`[CS-NO-MOCK]`).
