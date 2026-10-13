/**
 * EnemyForge Main Frontend Controller
 * Implements i18n localization [CS-LOCALIZATION], preset scanner,
 * review table configuration, and forge execution with 1-click rollback.
 */

class EnemyForgeApp {
  constructor() {
    this.currentLocale = "en";
    this.strings = {};
    this.presets = [];
    this.encounters = [];
    this.selectedPresets = new Set();
    this.init();
  }

  async init() {
    this.bindEvents();
    await this.loadLocalization(this.currentLocale);
    await this.refreshStatus();
    await this.scanPresets();
  }

  bindEvents() {
    // Language switcher
    const langSelect = document.getElementById("langSelect");
    if (langSelect) {
      langSelect.addEventListener("change", (e) => this.loadLocalization(e.target.value));
    }

    // Active Regulation Path input
    const activeRegInput = document.getElementById("activeRegInput");
    if (activeRegInput) {
      activeRegInput.addEventListener("change", (e) => {
        this.updateConfig({ active_regulation_path: e.target.value.trim() });
      });
    }

    // Game Directory input
    const gameDirInput = document.getElementById("gameDirInput");
    if (gameDirInput) {
      gameDirInput.addEventListener("change", (e) => {
        this.updateConfig({ game_dir: e.target.value.trim() });
      });
    }

    // Quick toggle: Use Mod Engine Regulation
    const useModRegBtn = document.getElementById("useModRegBtn");
    if (useModRegBtn) {
      useModRegBtn.addEventListener("click", () => {
        const path = "mod/regulation.bin";
        if (activeRegInput) activeRegInput.value = path;
        this.updateConfig({ active_regulation_path: path });
        this.showToast("Selected Mod Engine regulation.bin");
      });
    }

    // Quick toggle: Use Vanilla Fallback Regulation
    const useVanillaRegBtn = document.getElementById("useVanillaRegBtn");
    if (useVanillaRegBtn) {
      useVanillaRegBtn.addEventListener("click", () => {
        const path = "data/regulation.bin";
        if (activeRegInput) activeRegInput.value = path;
        this.updateConfig({ active_regulation_path: path });
        this.showToast("Selected pristine base fallback regulation.bin");
      });
    }

    // Create Backup button
    const createBackupBtn = document.getElementById("createBackupBtn");
    if (createBackupBtn) {
      createBackupBtn.addEventListener("click", () => this.createBackup());
    }

    // Restore Backup button
    const restoreBackupBtn = document.getElementById("restoreBackupBtn");
    if (restoreBackupBtn) {
      restoreBackupBtn.addEventListener("click", () => this.restoreBackup());
    }

    // Rollback to Vanilla Fallback button
    const rollbackVanillaBtn = document.getElementById("rollbackVanillaBtn");
    if (rollbackVanillaBtn) {
      rollbackVanillaBtn.addEventListener("click", () => this.rollbackToVanilla());
    }

    // Uninstall / Rollback button
    const uninstallBtn = document.getElementById("uninstallBtn");
    if (uninstallBtn) {
      uninstallBtn.addEventListener("click", () => this.uninstallEnemies());
    }

    // Generator Controls
    const placementModeSelect = document.getElementById("placementModeSelect");
    if (placementModeSelect) {
      placementModeSelect.addEventListener("change", (e) => {
        this.updateConfig({ placement_mode: e.target.value });
      });
    }

    const dropChanceInput = document.getElementById("dropChanceInput");
    const dropChanceVal = document.getElementById("dropChanceVal");
    if (dropChanceInput) {
      dropChanceInput.addEventListener("input", (e) => {
        if (dropChanceVal) dropChanceVal.textContent = `${e.target.value}%`;
      });
      dropChanceInput.addEventListener("change", (e) => {
        this.updateConfig({ global_drop_chance_percent: parseFloat(e.target.value) });
      });
    }

    const guaranteedLootCheck = document.getElementById("guaranteedLootCheck");
    if (guaranteedLootCheck) {
      guaranteedLootCheck.addEventListener("change", (e) => {
        this.updateConfig({ guaranteed_carried_loot: e.target.checked });
      });
    }

    const invasionAuraCheck = document.getElementById("invasionAuraCheck");
    if (invasionAuraCheck) {
      invasionAuraCheck.addEventListener("change", (e) => {
        this.updateConfig({ enable_invasion_aura: e.target.checked });
        this.renderTable();
      });
    }

    const tierScalingCheck = document.getElementById("tierScalingCheck");
    if (tierScalingCheck) {
      tierScalingCheck.addEventListener("change", (e) => {
        this.updateConfig({ scale_attributes_by_tier: e.target.checked });
      });
    }

    // Scan Presets button
    const scanBtn = document.getElementById("scanPresetsBtn");
    if (scanBtn) {
      scanBtn.addEventListener("click", () => this.scanPresets());
    }

    // Forge Enemies button
    const forgeBtn = document.getElementById("forgeAllBtn");
    if (forgeBtn) {
      forgeBtn.addEventListener("click", () => this.forgeEnemies());
    }

    // Drag and Drop Zone
    const dropzone = document.getElementById("dropzone");
    if (dropzone) {
      ["dragenter", "dragover"].forEach(event => {
        dropzone.addEventListener(event, (e) => {
          e.preventDefault();
          dropzone.classList.add("dragover");
        });
      });
      ["dragleave", "drop"].forEach(event => {
        dropzone.addEventListener(event, (e) => {
          e.preventDefault();
          dropzone.classList.remove("dragover");
        });
      });
      dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        this.scanPresets();
      });
      dropzone.addEventListener("click", () => this.scanPresets());
    }
  }

  async loadLocalization(lang) {
    this.currentLocale = lang;
    try {
      const res = await fetch(`/api/localization?lang=${lang}`);
      if (!res.ok) return;
      this.strings = await res.json();
      this.applyLocalization();
    } catch (err) {
      console.error("Localization loading error:", err);
    }
  }

  applyLocalization() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (this.strings[key]) {
        el.textContent = this.strings[key];
      }
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (this.strings[key]) {
        el.placeholder = this.strings[key];
      }
    });
  }

  t(key, fallback = "") {
    return this.strings[key] || fallback || key;
  }

  async refreshStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) return;
      const status = await res.json();

      const gameDirInput = document.getElementById("gameDirInput");
      if (gameDirInput && status.config.game_dir) {
        gameDirInput.value = status.config.game_dir;
      }

      const activeRegInput = document.getElementById("activeRegInput");
      if (activeRegInput && status.config.active_regulation_path) {
        activeRegInput.value = status.config.active_regulation_path;
      }

      const placementModeSelect = document.getElementById("placementModeSelect");
      if (placementModeSelect && status.config.placement_mode) {
        placementModeSelect.value = status.config.placement_mode;
      }

      const dropChanceInput = document.getElementById("dropChanceInput");
      const dropChanceVal = document.getElementById("dropChanceVal");
      if (dropChanceInput && status.config.global_drop_chance_percent !== undefined) {
        dropChanceInput.value = status.config.global_drop_chance_percent;
        if (dropChanceVal) dropChanceVal.textContent = `${status.config.global_drop_chance_percent}%`;
      }

      const guaranteedLootCheck = document.getElementById("guaranteedLootCheck");
      if (guaranteedLootCheck && status.config.guaranteed_carried_loot !== undefined) {
        guaranteedLootCheck.checked = status.config.guaranteed_carried_loot;
      }

      const invasionAuraCheck = document.getElementById("invasionAuraCheck");
      if (invasionAuraCheck && status.config.enable_invasion_aura !== undefined) {
        invasionAuraCheck.checked = status.config.enable_invasion_aura;
      }

      const tierScalingCheck = document.getElementById("tierScalingCheck");
      if (tierScalingCheck && status.config.scale_attributes_by_tier !== undefined) {
        tierScalingCheck.checked = status.config.scale_attributes_by_tier;
      }

      const backupStatusEl = document.getElementById("backupStatusBadge");
      if (backupStatusEl) {
        if (status.backup_count > 0) {
          backupStatusEl.className = "badge badge-green";
          backupStatusEl.textContent = `Snapshots Ready (${status.backup_count})`;
        } else {
          backupStatusEl.className = "badge badge-gold";
          backupStatusEl.textContent = "No Backups Yet";
        }
      }

      const injectedCountEl = document.getElementById("injectedCountLabel");
      if (injectedCountEl) {
        injectedCountEl.textContent = status.injected_count || 0;
      }
    } catch (err) {
      console.error("Status refresh error:", err);
    }
  }

  async updateConfig(payload) {
    try {
      await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      await this.refreshStatus();
    } catch (err) {
      console.error("Config update error:", err);
    }
  }

  async scanPresets() {
    try {
      const [presetsRes, encountersRes] = await Promise.all([
        fetch("/api/presets"),
        fetch("/api/encounters")
      ]);

      if (presetsRes.ok) {
        const data = await presetsRes.json();
        this.presets = data.presets || [];
        this.selectedPresets = new Set(this.presets.map(p => p.preset_id));
      }

      if (encountersRes.ok) {
        const encData = await encountersRes.json();
        this.encounters = encData.encounters || [];
      }

      this.renderTable();
      this.showToast(`Scanned ${this.presets.length} character presets`);
    } catch (err) {
      console.error("Preset scan error:", err);
    }
  }

  renderTable() {
    const tbody = document.getElementById("enemyTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (this.presets.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 32px; color: var(--text-secondary);">
            No character presets found. Place custom .json presets in <code>input_presets/</code>.
          </td>
        </tr>
      `;
      return;
    }

    const isGlobalAura = document.getElementById("invasionAuraCheck")?.checked ?? false;

    this.presets.forEach(preset => {
      const tr = document.createElement("tr");

      // Weapons chips
      const weaponsHtml = (preset.carried_items || [])
        .filter(item => item.item_type === "weapon")
        .map(w => `<span class="item-chip" title="Slot: ${w.slot}">⚔ ${w.name}</span>`)
        .join("") || `<span style="color: var(--text-muted); font-size: 12px;">Default Fists</span>`;

      // Armor chips
      const armorHtml = (preset.carried_items || [])
        .filter(item => item.item_type === "protector")
        .map(a => `<span class="item-chip" title="Slot: ${a.slot}">🛡 ${a.name}</span>`)
        .join("") || `<span style="color: var(--text-muted); font-size: 12px;">Unarmored</span>`;

      // Appearance badge
      const auraBadge = isGlobalAura
        ? `<span class="badge badge-red">🔴 Red Invader Aura</span>`
        : `<span class="badge badge-blue">👤 Flesh Human Tarnished</span>`;

      // World Encounter Match
      const zoneText = preset.spawn_region
        ? `[${preset.spawn_region}] ${preset.spawn_zone || "Encounter"}`
        : "Dynamic Regional";

      tr.innerHTML = `
        <td>
          <strong style="color: var(--text-primary); font-size: 15px;">${this.escapeHtml(preset.name)}</strong>
          <div style="font-size: 12px; color: var(--gold-primary); margin-top: 2px;">${this.escapeHtml(preset.title || "Wandering Champion")}</div>
        </td>
        <td>
          <span class="badge badge-gold">${this.escapeHtml(preset.archetype || "Duelist")}</span>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Lv. ${preset.level} | ${preset.gender}</div>
        </td>
        <td>
          <div style="max-width: 260px;">${weaponsHtml}</div>
        </td>
        <td>
          <div style="max-width: 260px;">${armorHtml}</div>
        </td>
        <td>
          <span style="font-size: 13px; color: var(--text-primary);">${this.escapeHtml(zoneText)}</span>
          <div style="font-size: 11px; color: #ffd166; margin-top: 2px;">Danger Tier ${preset.danger_tier || 1}</div>
        </td>
        <td>
          ${auraBadge}
          <div style="margin-top: 4px;">
            <span class="badge badge-green">100% Drops On Kill</span>
          </div>
        </td>
        <td style="text-align: center;">
          <input type="checkbox" class="preset-toggle" data-id="${preset.preset_id}" ${this.selectedPresets.has(preset.preset_id) ? "checked" : ""} style="accent-color: var(--gold-primary); width: 18px; height: 18px; cursor: pointer;">
        </td>
      `;

      tbody.appendChild(tr);
    });

    // Checkbox events
    tbody.querySelectorAll(".preset-toggle").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const id = e.target.getAttribute("data-id");
        if (e.target.checked) {
          this.selectedPresets.add(id);
        } else {
          this.selectedPresets.delete(id);
        }
      });
    });
  }

  async forgeEnemies() {
    const forgeBtn = document.getElementById("forgeAllBtn");
    if (forgeBtn) {
      forgeBtn.disabled = true;
      forgeBtn.textContent = "Forging Enemies & Injecting Regulation...";
    }

    try {
      const res = await fetch("/api/forge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected_ids: Array.from(this.selectedPresets) })
      });
      const data = await res.json();

      if (res.ok && data.status === "success") {
        this.showToast(`✦ Successfully forged ${data.total_forged} enemies into regulation.bin!`, "success");
        await this.refreshStatus();
      } else {
        this.showToast(`Forge failed: ${data.message || "Unknown error"}`, "error");
      }
    } catch (err) {
      this.showToast(`Forge request failed: ${err.message}`, "error");
    } finally {
      if (forgeBtn) {
        forgeBtn.disabled = false;
        forgeBtn.textContent = "✦ Forge Enemies & Inject World Encounters";
      }
    }
  }

  async createBackup() {
    try {
      const res = await fetch("/api/backup", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.showToast(`Snapshot created: ${data.backup_file}`, "success");
        await this.refreshStatus();
      } else {
        this.showToast(`Backup failed: ${data.message || "Error"}`, "error");
      }
    } catch (err) {
      this.showToast(`Backup failed: ${err.message}`, "error");
    }
  }

  async restoreBackup() {
    if (!confirm("Restore the regulation.bin file from the most recent safety snapshot?")) return;
    try {
      const res = await fetch("/api/restore", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.showToast("Regulation restored from latest backup!", "success");
        await this.refreshStatus();
      } else {
        this.showToast(`Restore failed: ${data.message || "Error"}`, "error");
      }
    } catch (err) {
      this.showToast(`Restore failed: ${err.message}`, "error");
    }
  }

  async rollbackToVanilla() {
    if (!confirm("Rollback regulation.bin cleanly to the pristine base game vanilla fallback?")) return;
    try {
      const res = await fetch("/api/rollback", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.showToast("Cleanly rolled back to pristine base vanilla state!", "success");
        await this.refreshStatus();
      } else {
        this.showToast(`Rollback failed: ${data.message || "Error"}`, "error");
      }
    } catch (err) {
      this.showToast(`Rollback failed: ${err.message}`, "error");
    }
  }

  async uninstallEnemies() {
    if (!confirm("Uninstall all injected enemies and revert the regulation file?")) return;
    try {
      const res = await fetch("/api/uninstall", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.showToast("Enemies uninstalled and manifest cleared cleanly!", "success");
        await this.refreshStatus();
      } else {
        this.showToast(`Uninstall failed: ${data.message || "Error"}`, "error");
      }
    } catch (err) {
      this.showToast(`Uninstall failed: ${err.message}`, "error");
    }
  }

  showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "toastContainer";
      container.style.cssText = "position: fixed; top: 24px; right: 24px; z-index: 10000; display: flex; flex-direction: column; gap: 10px;";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    const bg = type === "error" ? "rgba(220, 38, 38, 0.95)" : "rgba(18, 20, 28, 0.95)";
    const border = type === "error" ? "#ef4444" : "var(--gold-bright)";

    toast.style.cssText = `
      background: ${bg};
      border: 1px solid ${border};
      color: #ede8df;
      padding: 12px 18px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
      transition: opacity 0.3s ease;
      font-family: var(--font-sans);
    `;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
}

// Auto-instantiate
document.addEventListener("DOMContentLoaded", () => {
  window.enemyForgeApp = new EnemyForgeApp();
});
