# PhantomForge Custom Presets Ingestion Dropzone

Users can drop custom character presets in `.json` format into this directory.

PhantomForge automatically scans and parses any `.json` file placed here during `Scan Presets` or application startup.

## Sample Custom Preset Format

```json
{
  "preset_id": "my_custom_champion",
  "name": "Champion Malakor",
  "title": "Recusant Duelist",
  "archetype": "Greatsword Knight",
  "gender": 0,
  "level": 110,
  "scaling": {
    "hp_max": 2800,
    "mp_max": 200,
    "stamina_max": 180,
    "poise": 60,
    "runes": 18000
  },
  "equipment": {
    "head_id": 403000,
    "body_id": 403100,
    "arms_id": 403200,
    "legs_id": 403300,
    "right_weapon_1_id": 2010000,
    "left_weapon_1_id": 31050000
  },
  "carried_loot": {
    "guaranteed_drop": true,
    "drop_probability_percent": 100.0
  },
  "spawn_preference": {
    "region": "Limgrave",
    "zone": "Stormhill Crossroads",
    "danger_tier": 1
  }
}
```
