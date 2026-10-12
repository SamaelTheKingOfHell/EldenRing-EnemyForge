using System;
using System.Linq;
using System.Text.Json;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Utility methods for reading, writing, and type-converting PARAM cell values.
    /// Adheres to [CS-MODULAR] and [CS-GRANULARITY].
    /// </summary>
    public static class ParamHelper
    {
        public static int GetCellInt(PARAM.Row row, string fieldName)
        {
            var cell = row.Cells.FirstOrDefault(c => string.Equals(c.Def.InternalName, fieldName, StringComparison.OrdinalIgnoreCase));
            if (cell == null || cell.Value == null) return 0;
            try
            {
                return Convert.ToInt32(cell.Value);
            }
            catch
            {
                return 0;
            }
        }

        public static void SetCellIfExists(PARAM.Row row, string fieldName, object value)
        {
            var cell = row.Cells.FirstOrDefault(c => string.Equals(c.Def.InternalName, fieldName, StringComparison.OrdinalIgnoreCase));
            if (cell != null && value != null)
            {
                cell.Value = CoerceValue(cell.Def.DisplayType, value);
            }
        }

        public static object CoerceValue(PARAMDEF.DefType type, object value)
        {
            if (value == null) return null!;
            try
            {
                switch (type)
                {
                    case PARAMDEF.DefType.s8: return Convert.ToSByte(value);
                    case PARAMDEF.DefType.u8: return Convert.ToByte(value);
                    case PARAMDEF.DefType.s16: return Convert.ToInt16(value);
                    case PARAMDEF.DefType.u16: return Convert.ToUInt16(value);
                    case PARAMDEF.DefType.s32:
                    case PARAMDEF.DefType.b32: return Convert.ToInt32(value);
                    case PARAMDEF.DefType.u32: return Convert.ToUInt32(value);
                    case PARAMDEF.DefType.f32:
                    case PARAMDEF.DefType.angle32: return Convert.ToSingle(value);
                    case PARAMDEF.DefType.f64: return Convert.ToDouble(value);
                    case PARAMDEF.DefType.fixstr:
                    case PARAMDEF.DefType.fixstrW: return Convert.ToString(value) ?? "";
                    default: return value;
                }
            }
            catch
            {
                return value;
            }
        }

        public static void SetCellValue(PARAM.Cell cell, JsonElement jsonVal)
        {
            switch (cell.Def.DisplayType)
            {
                case PARAMDEF.DefType.s8:
                    cell.Value = (sbyte)jsonVal.GetInt32();
                    break;
                case PARAMDEF.DefType.u8:
                    cell.Value = (byte)jsonVal.GetInt32();
                    break;
                case PARAMDEF.DefType.s16:
                    cell.Value = (short)jsonVal.GetInt32();
                    break;
                case PARAMDEF.DefType.u16:
                    cell.Value = (ushort)jsonVal.GetInt32();
                    break;
                case PARAMDEF.DefType.s32:
                case PARAMDEF.DefType.b32:
                    cell.Value = jsonVal.GetInt32();
                    break;
                case PARAMDEF.DefType.u32:
                    cell.Value = (uint)jsonVal.GetInt64();
                    break;
                case PARAMDEF.DefType.f32:
                    cell.Value = (float)jsonVal.GetDouble();
                    break;
                case PARAMDEF.DefType.f64:
                    cell.Value = jsonVal.GetDouble();
                    break;
                case PARAMDEF.DefType.fixstr:
                case PARAMDEF.DefType.fixstrW:
                    cell.Value = jsonVal.GetString() ?? "";
                    break;
                default:
                    break;
            }
        }

        public static PARAM.Row CopyRow(PARAM.Row source, int newId, string newName)
        {
            var newRow = new PARAM.Row(newId, newName, source.Def);
            for (int i = 0; i < source.Cells.Count; i++)
            {
                newRow.Cells[i].Value = source.Cells[i].Value;
            }
            return newRow;
        }
    }
}
