using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Injects humanoid enemy parameters (NpcParam, CharaInitParam, FaceParam)
    /// representing character presets as active world enemies.
    /// Supports both normal human flesh models and phantom invader auras.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class EnemyInjector
    {
        public static void InjectEnemyParams(
            PARAM npcParam,
            PARAM charaInitParam,
            PARAM faceParam,
            JsonElement enemySpec)
        {
            int npcParamId = enemySpec.GetProperty("npc_param_id").GetInt32();
            int charaInitId = enemySpec.GetProperty("chr_asm_id").GetInt32();
            int faceParamId = enemySpec.GetProperty("face_param_id").GetInt32();
            int itemLotId = enemySpec.GetProperty("item_lot_id").GetInt32();
            string enemyName = enemySpec.GetProperty("name").GetString() ?? "World Enemy";

            // 1. Inject CharaInitParam (Character Initialization / Assembly: Weapons, Armor, Sex, Face link)
            InjectCharaInit(charaInitParam, charaInitId, faceParamId, enemyName, enemySpec);

            // 2. Inject FaceParam (Facial sliders, skin/hair colors)
            InjectFace(faceParam, faceParamId, enemyName, enemySpec);

            // 3. Inject NpcParam (Hostile Humanoid NPC stats, AI, drops, visual appearance)
            InjectNpc(npcParam, npcParamId, itemLotId, enemyName, enemySpec);

            // 4. Also patch base_enemy_id if provided (e.g. 42000010 for immediate live world appearance)
            if (enemySpec.TryGetProperty("base_enemy_id", out JsonElement baseElem) && baseElem.GetInt32() > 0)
            {
                int baseId = baseElem.GetInt32();
                InjectNpc(npcParam, baseId, itemLotId, enemyName, enemySpec);
            }
        }

        private static void InjectCharaInit(PARAM charaInitParam, int charaInitId, int faceParamId, string name, JsonElement spec)
        {
            PARAM.Row? existingRow = charaInitParam.Rows.FirstOrDefault(r => r.ID == charaInitId);
            PARAM.Row baseRow = existingRow ?? charaInitParam.Rows.FirstOrDefault(r => r.ID == 3000) ?? charaInitParam.Rows.First();

            PARAM.Row targetRow;
            if (existingRow == null)
            {
                targetRow = ParamHelper.CopyRow(baseRow, charaInitId, $"[EF] {name} CharaInit");
                charaInitParam.Rows.Add(targetRow);
            }
            else
            {
                targetRow = existingRow;
                targetRow.Name = $"[EF] {name} CharaInit";
            }

            // Link face parameter ID
            ParamHelper.SetCellIfExists(targetRow, "face", faceParamId);

            if (spec.TryGetProperty("equipment", out JsonElement equip))
            {
                if (equip.TryGetProperty("head_id", out JsonElement h)) ParamHelper.SetCellIfExists(targetRow, "equip_Helm", h.GetInt32());
                if (equip.TryGetProperty("body_id", out JsonElement b)) ParamHelper.SetCellIfExists(targetRow, "equip_Armer", b.GetInt32());
                if (equip.TryGetProperty("arms_id", out JsonElement a)) ParamHelper.SetCellIfExists(targetRow, "equip_Gaunt", a.GetInt32());
                if (equip.TryGetProperty("legs_id", out JsonElement l)) ParamHelper.SetCellIfExists(targetRow, "equip_Leg", l.GetInt32());
                if (equip.TryGetProperty("right_weapon_1_id", out JsonElement rw1)) ParamHelper.SetCellIfExists(targetRow, "equip_Wep_Right", rw1.GetInt32());
                if (equip.TryGetProperty("right_weapon_2_id", out JsonElement rw2)) ParamHelper.SetCellIfExists(targetRow, "equip_Subwep_Right", rw2.GetInt32());
                if (equip.TryGetProperty("left_weapon_1_id", out JsonElement lw1)) ParamHelper.SetCellIfExists(targetRow, "equip_Wep_Left", lw1.GetInt32());
                if (equip.TryGetProperty("left_weapon_2_id", out JsonElement lw2)) ParamHelper.SetCellIfExists(targetRow, "equip_Subwep_Left", lw2.GetInt32());
                if (equip.TryGetProperty("arrow_id", out JsonElement arr)) ParamHelper.SetCellIfExists(targetRow, "equip_Arrow", arr.GetInt32());
                if (equip.TryGetProperty("bolt_id", out JsonElement blt)) ParamHelper.SetCellIfExists(targetRow, "equip_Bolt", blt.GetInt32());
            }

            if (spec.TryGetProperty("gender", out JsonElement genderElem))
            {
                int genderVal = genderElem.GetInt32(); // 0 = Male, 1 = Female
                ParamHelper.SetCellIfExists(targetRow, "sex", (byte)genderVal);
            }
        }

        private static void InjectFace(PARAM faceParam, int faceParamId, string name, JsonElement spec)
        {
            PARAM.Row? existingRow = faceParam.Rows.FirstOrDefault(r => r.ID == faceParamId);
            PARAM.Row baseRow = existingRow ?? faceParam.Rows.FirstOrDefault(r => r.ID == 1000) ?? faceParam.Rows.First();

            PARAM.Row targetRow;
            if (existingRow == null)
            {
                targetRow = ParamHelper.CopyRow(baseRow, faceParamId, $"[EF] {name} Face");
                faceParam.Rows.Add(targetRow);
            }
            else
            {
                targetRow = existingRow;
                targetRow.Name = $"[EF] {name} Face";
            }

            if (spec.TryGetProperty("face_params", out JsonElement faceVals) && faceVals.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty prop in faceVals.EnumerateObject())
                {
                    ParamHelper.SetCellIfExists(targetRow, prop.Name, prop.Value.GetInt32());
                }
            }
        }

        private static void InjectNpc(
            PARAM npcParam,
            int npcParamId,
            int itemLotId,
            string name,
            JsonElement spec)
        {
            PARAM.Row? existingRow = npcParam.Rows.FirstOrDefault(r => r.ID == npcParamId);
            PARAM.Row baseRow = existingRow ?? npcParam.Rows.FirstOrDefault(r => r.ID == 100000) ?? npcParam.Rows.First();

            PARAM.Row targetRow;
            if (existingRow == null)
            {
                targetRow = ParamHelper.CopyRow(baseRow, npcParamId, $"[EF] {name}");
                npcParam.Rows.Add(targetRow);
            }
            else
            {
                targetRow = existingRow;
                targetRow.Name = $"[EF] {name}";
            }

            // Link drops and AI
            ParamHelper.SetCellIfExists(targetRow, "itemLotId_enemy", itemLotId);

            if (spec.TryGetProperty("think_param_id", out JsonElement thinkId))
            {
                ParamHelper.SetCellIfExists(targetRow, "npcThinkParamId", thinkId.GetInt32());
            }

            // Humanoid model type (c0000 = Human/Tarnished)
            ParamHelper.SetCellIfExists(targetRow, "subChrId", 0);
            ParamHelper.SetCellIfExists(targetRow, "chrType", 5); // 5 = Hostile NPC / Enemy

            // SpEffect aura: 0 = Normal human flesh/armor appearance; 7000+ = Red Invader glow
            int auraId = 0;
            if (spec.TryGetProperty("sp_effect_aura_id", out JsonElement auraElem))
            {
                auraId = auraElem.GetInt32();
            }
            ParamHelper.SetCellIfExists(targetRow, "spEffectID0", auraId);

            // Health, Poise, and Runes scaling (ER NpcParam cells: hp, stamina, getSoul, superArmorDurability)
            if (spec.TryGetProperty("hp_max", out JsonElement hp))
            {
                ParamHelper.SetCellIfExists(targetRow, "hp", hp.GetInt32());
                ParamHelper.SetCellIfExists(targetRow, "hpMax", hp.GetInt32());
            }
            if (spec.TryGetProperty("mp_max", out JsonElement mp))
            {
                ParamHelper.SetCellIfExists(targetRow, "mp", mp.GetInt32());
                ParamHelper.SetCellIfExists(targetRow, "mpMax", mp.GetInt32());
            }
            if (spec.TryGetProperty("stamina_max", out JsonElement sta))
            {
                ParamHelper.SetCellIfExists(targetRow, "stamina", (ushort)sta.GetInt32());
                ParamHelper.SetCellIfExists(targetRow, "staminaMax", sta.GetInt32());
            }
            if (spec.TryGetProperty("get_soul", out JsonElement runes)) ParamHelper.SetCellIfExists(targetRow, "getSoul", runes.GetInt32());
            if (spec.TryGetProperty("poise", out JsonElement poise)) ParamHelper.SetCellIfExists(targetRow, "superArmorDurability", (float)poise.GetInt32());
        }
    }
}
