"""
Regulation Manager for PhantomForge.
Orchestrates Elden Ring regulation.bin decryption, phantom injection, and AES-256 re-encryption via RegTool.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from src.backup_manager import BackupManager
from src.manifest_store import ManifestStore
from src.logger import system_logger


class RegulationManager:
    """Manages regulation patching lifecycle and RegTool execution."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir).resolve()
        self.defs_dir = self.base_dir / "tools" / "vendor" / "Paramdex" / "ER" / "Defs"
        self.regtool_exe = self.base_dir / "tools" / "RegTool" / "bin" / "Release" / "net9.0" / "RegTool.exe"
        self.regtool_dll = self.base_dir / "tools" / "RegTool" / "bin" / "Release" / "net9.0" / "RegTool.dll"
        self.backup_mgr = BackupManager(self.base_dir / "backups")
        self.manifest_store = ManifestStore(self.base_dir / "enemyforge_manifest.json")

    def _get_process_env(self) -> Dict[str, str]:
        """Ensures DOTNET_ROOT and PATH are configured for .NET execution."""
        env = os.environ.copy()
        if "DOTNET_ROOT" not in env:
            candidates = [
                Path(r"C:\Program Files\dotnet"),
                Path.home() / "AppData" / "Local" / "Microsoft" / "dotnet"
            ]
            for cand in candidates:
                if cand.exists():
                    env["DOTNET_ROOT"] = str(cand)
                    env["PATH"] = f"{str(cand)};{env.get('PATH', '')}"
                    break
        return env

    def resolve_source_regulation(self, specified_path: Optional[Path] = None) -> Optional[Path]:
        """Resolves source regulation with multi-tier fallback to base game data."""
        if specified_path and Path(specified_path).exists():
            return Path(specified_path).resolve()

        # Tier 1: data/regulation.bin base template
        data_reg = self.base_dir / "data" / "regulation.bin"
        if data_reg.exists():
            return data_reg

        # Tier 2: backups/ regulation.bin.vanilla_fallback
        vanilla = self.backup_mgr.get_vanilla_fallback()
        if vanilla and vanilla.exists():
            return vanilla

        # Tier 3: Most recent timestamped backup
        latest = self.backup_mgr.get_latest_backup()
        if latest and latest.exists():
            return latest

        return None

    def execute_patch(
        self,
        patch_spec: Dict[str, Any],
        source_reg: Optional[Path],
        target_reg: Path,
        msg_dir: Optional[Path] = None
    ) -> bool:
        """Executes the patch process via RegTool with automatic base game fallback."""
        source_path = self.resolve_source_regulation(source_reg)
        target_path = Path(target_reg).resolve()

        if not source_path or not source_path.exists():
            system_logger.error(
                f"Source regulation could not be resolved. Please ensure data/regulation.bin exists.",
                source="RegulationManager"
            )
            return False

        if not self.defs_dir.exists():
            system_logger.error(f"Paramdex defs directory not found: {self.defs_dir}", source="RegulationManager")
            return False

        # Create pre-write snapshot
        backup_path = self.backup_mgr.create_snapshot(target_path if target_path.exists() else source_path)
        backup_name = backup_path.name if backup_path else ""

        # Write temporary spec file
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(patch_spec, tf, indent=2)
            spec_file_path = Path(tf.name)

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if self.regtool_dll.exists():
                cmd = ["dotnet", str(self.regtool_dll)]
            elif self.regtool_exe.exists():
                cmd = [str(self.regtool_exe)]
            else:
                cmd = ["dotnet", "run", "--project", str(self.base_dir / "tools" / "RegTool" / "RegTool.csproj"), "--"]

            cmd.extend([
                "patch",
                "--input", str(source_path),
                "--output", str(target_path),
                "--defs", str(self.defs_dir),
                "--spec", str(spec_file_path)
            ])

            if msg_dir and Path(msg_dir).exists():
                cmd.extend(["--msg", str(msg_dir)])

            system_logger.info(f"Running RegTool command: {' '.join(cmd)}", source="RegulationManager")
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.base_dir),
                env=self._get_process_env(),
                check=False
            )

            if res.returncode == 0:
                system_logger.info("RegTool patch completed successfully!", source="RegulationManager")
                self.manifest_store.save(
                    backup_file=backup_name,
                    enemies_spec=patch_spec.get("enemies") or patch_spec.get("phantoms", [])
                )
                return True
            else:
                err_msg = res.stderr or res.stdout
                system_logger.error(f"RegTool failed (code {res.returncode}): {err_msg}", source="RegulationManager")
                raise RuntimeError(f"RegTool failed: {err_msg}")

        finally:
            if spec_file_path.exists():
                spec_file_path.unlink()

    def restore_regulation(self, target_reg: Path) -> bool:
        """Restores target regulation from latest snapshot and clears manifest."""
        success = self.backup_mgr.restore_backup(target_reg)
        if success:
            self.manifest_store.clear()
        return success

    def rollback_to_vanilla(self, target_reg: Path) -> bool:
        """Rolls back target regulation to the pristine base game vanilla fallback."""
        success = self.backup_mgr.restore_vanilla_fallback(target_reg)
        if success:
            self.manifest_store.clear()
        return success

    def inspect_gear(self, source_reg: Optional[Path], output_path: Path) -> Optional[Dict[str, Any]]:
        """Invokes RegTool inspect-gear to read installed and modded gear from regulation.bin."""
        source_path = self.resolve_source_regulation(source_reg)
        if not source_path or not source_path.exists():
            return None

        if self.regtool_dll.exists():
            cmd = ["dotnet", str(self.regtool_dll)]
        elif self.regtool_exe.exists():
            cmd = [str(self.regtool_exe)]
        else:
            cmd = ["dotnet", "run", "--project", str(self.base_dir / "tools" / "RegTool" / "RegTool.csproj"), "--"]

        cmd.extend([
            "inspect-gear",
            "--input", str(source_path),
            "--defs", str(self.defs_dir),
            "--output", str(output_path)
        ])

        system_logger.info(f"Inspecting regulation gear via RegTool: {' '.join(cmd)}", source="RegulationManager")
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.base_dir),
            env=self._get_process_env(),
            check=False
        )
        if res.returncode == 0 and output_path.exists():
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

