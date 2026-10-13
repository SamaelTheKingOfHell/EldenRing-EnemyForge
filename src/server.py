"""
Cross-platform HTTP server and API provider for EnemyForge.
Adheres to [CS-MODULAR], [CS-DEBUG], and [CS-GRANULARITY].
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List

from src.models import EnemyForgeConfig, PlacementMode, EnemyForgeManifest
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.id_allocator import IdAllocator
from src.enemy_builder import EnemyBuilder
from src.regulation_manager import RegulationManager
from src.logger import system_logger


class EnemyForgeRequestHandler(SimpleHTTPRequestHandler):
    """Processes UI static assets and REST API endpoints."""

    base_dir: Path
    config: EnemyForgeConfig
    preset_loader: PresetLoader
    world_placer: WorldPlacer
    reg_manager: RegulationManager

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/"):
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if path == "/api/status":
                self._handle_get_status()
            elif path == "/api/presets":
                self._handle_get_presets()
            elif path == "/api/encounters":
                self._handle_get_encounters()
            elif path == "/api/config":
                self._handle_get_config()
            elif path == "/api/manifest":
                self._handle_get_manifest()
            elif path == "/api/logs":
                self._handle_get_logs()
            elif path == "/api/localization" or path.startswith("/api/localization/"):
                lang = query_params.get("lang", [None])[0]
                if not lang and path.startswith("/api/localization/"):
                    lang = path.split("/")[-1]
                self._handle_get_localization(lang or "en")
            else:
                self.send_error(404, "API Endpoint Not Found")
        else:
            self._serve_static(path)

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/config":
            self._handle_post_config(payload)
        elif path == "/api/forge":
            self._handle_post_forge(payload)
        elif path == "/api/backup":
            self._handle_post_backup()
        elif path == "/api/restore":
            self._handle_post_restore()
        elif path == "/api/rollback":
            self._handle_post_rollback()
        elif path == "/api/uninstall":
            self._handle_post_uninstall()
        else:
            self.send_error(404, "Endpoint Not Found")

    def _serve_static(self, path: str) -> None:
        """Serves UI HTML, CSS, and JS assets."""
        ui_dir = self.base_dir / "ui"
        if path in ("/", "", "/index.html"):
            target_file = ui_dir / "index.html"
        else:
            clean_path = path.lstrip("/")
            target_file = ui_dir / clean_path

        if not target_file.exists() or target_file.is_dir():
            self.send_error(404, f"File Not Found: {path}")
            return

        ext = target_file.suffix.lower()
        mime_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".svg": "image/svg+xml"
        }
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(target_file, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as ex:
            self.send_error(500, f"Error reading file: {ex}")

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(raw)

    def _handle_get_status(self) -> None:
        manifest = self.reg_manager.manifest_store.load()
        backups = self.reg_manager.backup_mgr.list_backups()
        self._send_json({
            "status": "online",
            "app": "EnemyForge",
            "config": {
                "game_dir": self.config.game_dir,
                "active_regulation_path": self.config.active_regulation_path,
                "target_mod_dir": self.config.target_mod_dir,
                "placement_mode": self.config.placement_mode.value,
                "guaranteed_carried_loot": self.config.guaranteed_carried_loot,
                "global_drop_chance_percent": self.config.global_drop_chance_percent,
                "enable_invasion_aura": self.config.enable_invasion_aura,
                "scale_attributes_by_tier": self.config.scale_attributes_by_tier,
                "ui_language": self.config.ui_language
            },
            "backup_count": len(backups),
            "injected_count": len(manifest.forged_enemies)
        })

    def _handle_get_presets(self) -> None:
        presets = self.preset_loader.discover_and_load()
        out = []
        for p in presets:
            out.append({
                "preset_id": p.preset_id,
                "name": p.name,
                "title": p.title,
                "archetype": p.archetype,
                "gender": "Female" if p.gender == 1 else "Male",
                "level": p.level,
                "hp": p.hp_max,
                "runes": p.runes,
                "carried_items": p.equipment.get_all_carried_items(),
                "spawn_region": p.spawn_region,
                "spawn_zone": p.spawn_zone,
                "danger_tier": p.danger_tier,
                "aura_id": p.sp_effect_aura_id
            })
        self._send_json({"presets": out, "count": len(out)})

    def _handle_get_encounters(self) -> None:
        encounters = [e.__dict__ for e in self.world_placer.all_encounters]
        self._send_json({"encounters": encounters, "count": len(encounters)})

    def _handle_get_config(self) -> None:
        self._send_json({
            "game_dir": self.config.game_dir,
            "active_regulation_path": self.config.active_regulation_path,
            "target_mod_dir": self.config.target_mod_dir,
            "placement_mode": self.config.placement_mode.value,
            "guaranteed_carried_loot": self.config.guaranteed_carried_loot,
            "global_drop_chance_percent": self.config.global_drop_chance_percent,
            "enable_invasion_aura": self.config.enable_invasion_aura,
            "scale_attributes_by_tier": self.config.scale_attributes_by_tier,
            "mystery_mode": self.config.mystery_mode,
            "ui_language": self.config.ui_language
        })

    def _handle_post_config(self, payload: Dict[str, Any]) -> None:
        if "placement_mode" in payload:
            self.config.placement_mode = PlacementMode(payload["placement_mode"])
        if "guaranteed_carried_loot" in payload:
            self.config.guaranteed_carried_loot = bool(payload["guaranteed_carried_loot"])
        if "global_drop_chance_percent" in payload:
            self.config.global_drop_chance_percent = float(payload["global_drop_chance_percent"])
        if "enable_invasion_aura" in payload:
            self.config.enable_invasion_aura = bool(payload["enable_invasion_aura"])
        if "scale_attributes_by_tier" in payload:
            self.config.scale_attributes_by_tier = bool(payload["scale_attributes_by_tier"])
        if "mystery_mode" in payload:
            self.config.mystery_mode = bool(payload["mystery_mode"])
        if "ui_language" in payload:
            self.config.ui_language = str(payload["ui_language"])
        if "active_regulation_path" in payload:
            self.config.active_regulation_path = str(payload["active_regulation_path"])
        if "game_dir" in payload:
            self.config.game_dir = str(payload["game_dir"])

        self._send_json({"status": "success", "message": "Config updated"})

    def _handle_post_backup(self) -> None:
        source_reg = self.reg_manager.resolve_source_regulation(
            Path(self.config.active_regulation_path) if self.config.active_regulation_path else None
        )
        if not source_reg or not source_reg.exists():
            self._send_json({"status": "error", "message": "Source regulation file not found to backup"}, status=400)
            return
        snapshot = self.reg_manager.backup_mgr.create_snapshot(source_reg)
        if snapshot:
            self._send_json({"status": "success", "backup_file": snapshot.name})
        else:
            self._send_json({"status": "error", "message": "Failed to create backup snapshot"}, status=500)

    def _handle_post_forge(self, payload: Dict[str, Any]) -> None:
        system_logger.info("Forge requested from Web UI.", source="EnemyForgeServer")
        presets = self.preset_loader.discover_and_load()
        if not presets:
            self._send_json({"status": "error", "message": "No presets found"}, status=400)
            return

        # 1. World placement
        assignments = self.world_placer.assign_encounters(presets, mode=self.config.placement_mode)

        # 2. Build patch spec
        builder = EnemyBuilder()
        patch_spec = builder.build_patch_spec(assignments, self.config)

        # 3. Resolve regulations with fallback
        source_reg = Path(self.config.active_regulation_path) if self.config.active_regulation_path else None
        target_reg = self.base_dir / self.config.target_mod_dir / "regulation.bin"
        msg_dir = self.base_dir / "data"

        try:
            success = self.reg_manager.execute_patch(
                patch_spec=patch_spec,
                source_reg=source_reg,
                target_reg=target_reg,
                msg_dir=msg_dir
            )
            if success:
                self._send_json({
                    "status": "success",
                    "total_forged": len(assignments),
                    "target_regulation": str(target_reg)
                })
            else:
                self._send_json({"status": "error", "message": "Patch execution failed"}, status=500)
        except Exception as ex:
            self._send_json({"status": "error", "message": str(ex)}, status=500)

    def _handle_post_restore(self) -> None:
        target_reg = self.base_dir / self.config.target_mod_dir / "regulation.bin"
        success = self.reg_manager.restore_regulation(target_reg)
        if success:
            self._send_json({"status": "success", "message": "Regulation restored from latest backup"})
        else:
            self._send_json({"status": "error", "message": "Restore failed"}, status=500)

    def _handle_post_rollback(self) -> None:
        target_reg = self.base_dir / self.config.target_mod_dir / "regulation.bin"
        success = self.reg_manager.rollback_to_vanilla(target_reg)
        if success:
            self._send_json({"status": "success", "message": "Regulation cleanly rolled back to pristine base vanilla state"})
        else:
            self._send_json({"status": "error", "message": "Rollback to vanilla failed"}, status=500)

    def _handle_post_uninstall(self) -> None:
        target_reg = self.base_dir / self.config.target_mod_dir / "regulation.bin"
        success = self.reg_manager.rollback_to_vanilla(target_reg)
        self.reg_manager.manifest_store.clear()
        self._send_json({"status": "success", "message": "Enemies cleanly uninstalled and regulation rolled back"})

    def _handle_get_manifest(self) -> None:
        manifest = self.reg_manager.manifest_store.load()
        self._send_json(manifest.__dict__)

    def _handle_get_logs(self) -> None:
        logs = system_logger.get_buffered_logs()
        self._send_json({"logs": logs})

    def _handle_get_localization(self, lang: str) -> None:
        loc_file = self.base_dir / "data" / "localization" / f"{lang}.json"
        if not loc_file.exists():
            loc_file = self.base_dir / "data" / "localization" / "en.json"

        with open(loc_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._send_json(data)


# Backward-compatible alias
PhantomForgeRequestHandler = EnemyForgeRequestHandler


def start_server(base_dir: Path, port: int = 8484) -> HTTPServer:
    """Initializes and runs the EnemyForge HTTP server."""
    EnemyForgeRequestHandler.base_dir = Path(base_dir).resolve()
    EnemyForgeRequestHandler.config = EnemyForgeConfig()
    EnemyForgeRequestHandler.preset_loader = PresetLoader(
        data_presets_dir=base_dir / "data" / "presets",
        input_presets_dir=base_dir / "input_presets"
    )
    EnemyForgeRequestHandler.world_placer = WorldPlacer(
        encounters_file=base_dir / "data" / "world_encounters.json"
    )
    EnemyForgeRequestHandler.reg_manager = RegulationManager(base_dir)

    server = HTTPServer(("127.0.0.1", port), EnemyForgeRequestHandler)
    system_logger.info(f"EnemyForge server listening at http://127.0.0.1:{port}", source="Server")
    return server
