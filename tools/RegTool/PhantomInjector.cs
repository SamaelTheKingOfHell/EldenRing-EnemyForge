using System.Text.Json;
using SoulsFormats;

namespace PhantomForge.RegTool
{
    /// <summary>
    /// Forwarder for backwards compatibility.
    /// </summary>
    public static class PhantomInjector
    {
        public static void InjectPhantomParams(
            PARAM npcParam,
            PARAM charaInitParam,
            PARAM faceParam,
            JsonElement phantomSpec)
        {
            EnemyInjector.InjectEnemyParams(npcParam, charaInitParam, faceParam, phantomSpec);
        }
    }
}
