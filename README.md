# PhantomForge: Character Preset Enemy & Carried Loot Injector

**PhantomForge** is a cross-platform desktop application and mod engine for *Elden Ring* (Windows & Linux / Steam Deck). It transforms player character presets into formidable hostile humanoid phantoms and roaming NPC enemies across the Lands Between, and **guarantees that every phantom drops the exact weapons, shields, and armor that they carry in their build**.

---

## Key Features

1. **Hostile Character Presets in the World**:
   - Ingests custom or built-in character presets (fashion souls, weapon arsenals, level scaling, and AI combat styles).
   - Generates authentic humanoid enemies (`c0000`) with level-scaled attributes, poise, runes, and visual invader auras (`SpEffect 7000`).

2. **Carried Loot Drops (100% on Kill)**:
   - **"They should drop the loot that they carry"**: Defeating a phantom guarantees receiving every single piece of gear they wielded:
     - Head, Chest, Gauntlets, and Greaves armor pieces.
     - Primary and secondary right-hand weapons.
     - Left-hand weapons, shields, catalysts, and seals.
   - Automatically populates `ItemLotParam_enemy` rows linked to the phantom's `NpcParam.itemLotId_enemy`.

3. **Tactical World Placement Engine**:
   - **Thematic Regional**: Matches phantom strength and equipment tier to regional difficulty (Limgrave -> Liurnia -> Caelid -> Altus Plateau -> Mountaintops).
   - **Roaming Invasions**: Places phantoms as hostile red invaders at landmark exploration bottlenecks.
   - **Champion Duels**: Positions phantoms at crossroads and arena approaches.
   - **Chaos Expedition**: Shuffles phantoms across valid world encounter coordinates.

4. **Safety & 1-Click Rollback**:
   - Timestamped pre-write regulation snapshots (`regulation.bin.bak_YYYYMMDD_HHMMSS`) with SHA-256 verification.
   - Reversible manifest (`phantomforge_manifest.json`) enabling 1-click clean uninstallation.

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

### 2. Launch PhantomForge
Run the launcher:

```bash
python run_phantomforge.py
```

The application will start the local server and open your default browser to `http://127.0.0.1:8484`.

### 3. Review & Forge
1. Click **Scan Presets** to preview presets and their carried loot.
2. Select your preferred **World Placement Strategy** in Settings.
3. Click **✦ Forge Phantoms & Inject Loot**.
4. Launch Elden Ring via ModEngine 2 (`launchmod_eldenring.bat`).

---

## Project Structure

```text
PhantomForge/
  ├── INDEX.md               # Root navigation index
  ├── OBJECTIVE.md           # Mission statement and invariants
  ├── ROADMAP.md             # Development roadmap
  ├── README.md              # Project documentation
  ├── run_phantomforge.py    # Desktop launcher & CLI runner
  ├── rebuild_regtool.bat    # RegTool compilation script
  ├── config.json            # Generator configuration
  ├── data/                  # Built-in presets, encounters, and i18n
  ├── src/                   # Python core engine
  ├── ui/                    # Souls-themed web dashboard
  ├── input_presets/         # User preset dropzone
  ├── tools/                 # C# RegTool and vendor dependencies
  ├── backups/               # Pre-write regulation backups
  └── tests/                 # Automated test suite
```

---

## Testing

Run the automated test suite:

```bash
python -m unittest discover tests
```
