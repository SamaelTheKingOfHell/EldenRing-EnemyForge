using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Injects drop tables (ItemLotParam_enemy) containing the exact gear
    /// that character phantoms carry in their loadout.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class LootInjector
    {
        private const uint CATEGORY_WEAPON = 0x20000000;
        private const uint CATEGORY_PROTECTOR = 0x10000000;
        private const uint CATEGORY_GOODS = 0x40000000;

        public record LootDropItem(
            int ItemId,
            string ItemType, // "weapon", "protector", "goods"
            int ProbabilityPoint, // 1000 = 100%
            int Quantity
        );

        public static void InjectCarriedLootDrops(
            PARAM itemLotParam,
            int itemLotId,
            string phantomName,
            List<LootDropItem> carriedItems)
        {
            if (carriedItems == null || carriedItems.Count == 0) return;

            // Find or copy template enemy lot row (e.g. 10000 or first row)
            PARAM.Row? existingRow = itemLotParam.Rows.FirstOrDefault(r => r.ID == itemLotId);
            PARAM.Row baseRow = existingRow ?? itemLotParam.Rows.FirstOrDefault(r => r.ID == 10000) ?? itemLotParam.Rows.First();

            PARAM.Row targetRow;
            if (existingRow == null)
            {
                targetRow = ParamHelper.CopyRow(baseRow, itemLotId, $"[PF] {phantomName} Carried Drops");
                itemLotParam.Rows.Add(targetRow);
            }
            else
            {
                targetRow = existingRow;
                targetRow.Name = $"[PF] {phantomName} Carried Drops";
            }

            // Clear all 8 slots first to ensure clean drop state
            for (int i = 1; i <= 8; i++)
            {
                string suffix = i.ToString("D2");
                ParamHelper.SetCellIfExists(targetRow, $"lotItemId{suffix}", 0);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemCategory{suffix}", 0);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemBasePoint{suffix}", 0);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemNum{suffix}", 0);
                ParamHelper.SetCellIfExists(targetRow, $"enableFlagId{suffix}", 0);
            }

            // Populate up to 8 carried equipment pieces
            int slotCount = Math.Min(carriedItems.Count, 8);
            for (int i = 0; i < slotCount; i++)
            {
                var drop = carriedItems[i];
                string suffix = (i + 1).ToString("D2");

                uint categoryCode = drop.ItemType.ToLower() switch
                {
                    "weapon" => CATEGORY_WEAPON,
                    "protector" => CATEGORY_PROTECTOR,
                    "armor" => CATEGORY_PROTECTOR,
                    "goods" => CATEGORY_GOODS,
                    _ => CATEGORY_PROTECTOR
                };

                ParamHelper.SetCellIfExists(targetRow, $"lotItemId{suffix}", drop.ItemId);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemCategory{suffix}", categoryCode);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemBasePoint{suffix}", drop.ProbabilityPoint);
                ParamHelper.SetCellIfExists(targetRow, $"lotItemNum{suffix}", Math.Max(1, drop.Quantity));
            }

            Console.WriteLine($"[LootInjector] Configured {slotCount} carried item drop(s) for phantom '{phantomName}' (Lot ID: {itemLotId}).");
        }
    }
}
