/**
 * Floating Developer Console Controller [CS-DEBUG]
 * Intercepts, color-codes, and prints all real-time logs and system events.
 */

class DevConsole {
  constructor() {
    this.drawer = document.getElementById("devConsoleDrawer");
    this.toggleBtn = document.getElementById("floatingDevBtn");
    this.body = document.getElementById("consoleBody");
    this.clearBtn = document.getElementById("consoleClearBtn");
    this.copyBtn = document.getElementById("consoleCopyBtn");
    this.debugToggle = document.getElementById("debugModeToggle");
    this.isOpen = false;
    this.pollInterval = null;
    this.lastLogCount = 0;

    this.init();
  }

  init() {
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener("click", () => this.toggle());
    }
    if (this.clearBtn) {
      this.clearBtn.addEventListener("click", () => this.clear());
    }
    if (this.copyBtn) {
      this.copyBtn.addEventListener("click", () => this.copyToClipboard());
    }
    if (this.debugToggle) {
      this.debugToggle.addEventListener("change", (e) => this.setDebugMode(e.target.checked));
    }

    // Start background log polling
    this.startPolling();
  }

  toggle() {
    this.isOpen = !this.isOpen;
    if (this.drawer) {
      this.drawer.classList.toggle("active", this.isOpen);
      if (this.isOpen) {
        this.scrollToBottom();
      }
    }
  }

  startPolling() {
    this.fetchLogs();
    this.pollInterval = setInterval(() => this.fetchLogs(), 1500);
  }

  async fetchLogs() {
    try {
      const res = await fetch("/api/logs");
      if (!res.ok) return;
      const data = await res.json();
      const logs = data.logs || [];

      if (logs.length !== this.lastLogCount) {
        this.renderLogs(logs);
        this.lastLogCount = logs.length;
      }
    } catch (err) {
      // Quietly ignore network polling hiccups
    }
  }

  renderLogs(logs) {
    if (!this.body) return;
    this.body.innerHTML = "";

    const isDebugEnabled = this.debugToggle ? this.debugToggle.checked : true;

    logs.forEach(log => {
      const level = (log.level || "INFO").toUpperCase();
      if (!isDebugEnabled && level === "DEBUG") {
        return;
      }

      const el = document.createElement("div");
      el.className = `log-entry ${level}`;
      el.innerHTML = `
        <span class="log-time">[${log.timestamp || ""}]</span>
        <span class="log-level">[${level}]</span>
        <span class="log-source">[${log.source || "System"}]</span>
        <span class="log-msg">${this.escapeHtml(log.message || "")}</span>
      `;
      this.body.appendChild(el);
    });

    this.scrollToBottom();
  }

  clear() {
    if (this.body) {
      this.body.innerHTML = "";
      this.lastLogCount = 0;
    }
  }

  copyToClipboard() {
    if (!this.body) return;
    const text = this.body.innerText;
    navigator.clipboard.writeText(text).then(() => {
      if (this.copyBtn) {
        const orig = this.copyBtn.textContent;
        this.copyBtn.textContent = "Copied!";
        setTimeout(() => { this.copyBtn.textContent = orig; }, 1200);
      }
    });
  }

  setDebugMode(enabled) {
    this.lastLogCount = -1; // Force re-render on next poll
    this.fetchLogs();
  }

  scrollToBottom() {
    if (this.body) {
      this.body.scrollTop = this.body.scrollHeight;
    }
  }

  escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
}

// Auto-instantiate
document.addEventListener("DOMContentLoaded", () => {
  window.devConsole = new DevConsole();
});
