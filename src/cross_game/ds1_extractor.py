"""
Dark Souls 1 PTDE Asset Extractor for EnemyForge.
Zero-dependency reader for dvdbnd0/1 BHD5 headers and BDT payloads.
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-NO-MOCK].
Enforces legal compliance: extracts directly from the user's licensed game installation.
"""

import struct
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from src.logger import system_logger



COMMON_STEAM_PATHS = [
    Path(r"D:\SteamLibrary\steamapps\common\Dark Souls Prepare to Die Edition\DATA"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA"),
    Path(r"C:\SteamLibrary\steamapps\common\Dark Souls Prepare to Die Edition\DATA"),
    Path(r"E:\SteamLibrary\steamapps\common\Dark Souls Prepare to Die Edition\DATA"),
]


def from_path_hash(path: str) -> int:
    """Computes FromSoftware's 32-bit prime string hash for BHD5 file lookups."""
    normalized = path.lower().replace('\\', '/')
    if not normalized.startswith('/'):
        normalized = '/' + normalized
    res = 0
    for char in normalized:
        res = ((res * 37) + ord(char)) & 0xFFFFFFFF
    return res


class DS1Extractor:
    """Extracts raw entity models, animations, and textures from a local DS1 PTDE installation."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = self._resolve_data_dir(data_dir)
        self.dvdbnd0_bhd = self.data_dir / "dvdbnd0.bhd5" if self.data_dir else None
        self.dvdbnd0_bdt = self.data_dir / "dvdbnd0.bdt" if self.data_dir else None
        self.dvdbnd1_bhd = self.data_dir / "dvdbnd1.bhd5" if self.data_dir else None
        self.dvdbnd1_bdt = self.data_dir / "dvdbnd1.bdt" if self.data_dir else None

    @classmethod
    def detect_ptde_data_dir(cls) -> Optional[Path]:
        """Detects default steam installation directory for DS1 PTDE."""
        for candidate in COMMON_STEAM_PATHS:
            if candidate.exists() and (candidate / "DARKSOULS.exe").exists():
                return candidate
        return None

    def _resolve_data_dir(self, explicit_path: Optional[Path]) -> Optional[Path]:
        if explicit_path and explicit_path.exists():
            return explicit_path
        return self.detect_ptde_data_dir()


    def is_installed(self) -> bool:
        """Verifies that a valid licensed DS1 PTDE installation is detected."""
        if not self.data_dir or not self.data_dir.exists():
            return False
        return (self.data_dir / "DARKSOULS.exe").exists() and (self.data_dir / "dvdbnd0.bhd5").exists()

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns structured diagnostic status of the target DS1 PTDE installation."""
        data_dir_exists = bool(self.data_dir and self.data_dir.exists())
        has_exe = bool(data_dir_exists and (self.data_dir / "DARKSOULS.exe").exists())
        bhd0 = bool(self.dvdbnd0_bhd and self.dvdbnd0_bhd.exists())
        bdt0 = bool(self.dvdbnd0_bdt and self.dvdbnd0_bdt.exists())
        bdt0_size = self.dvdbnd0_bdt.stat().st_size if bdt0 else 0
        bhd1 = bool(self.dvdbnd1_bhd and self.dvdbnd1_bhd.exists())
        bdt1 = bool(self.dvdbnd1_bdt and self.dvdbnd1_bdt.exists())
        bdt1_size = self.dvdbnd1_bdt.stat().st_size if bdt1 else 0

        return {
            "data_dir": str(self.data_dir) if self.data_dir else "",
            "is_valid": self.is_installed(),
            "has_exe": has_exe,
            "dvdbnd0_valid": bhd0 and bdt0,
            "dvdbnd0_size": bdt0_size,
            "dvdbnd1_valid": bhd1 and bdt1,
            "dvdbnd1_size": bdt1_size,
        }


    def _read_bhd5_index(self, bhd_path: Path) -> Dict[int, Tuple[int, int]]:
        """Parses a BHD5 header file and returns a mapping: {hash: (padded_size, file_offset)}."""
        with open(bhd_path, "rb") as f:
            header_bytes = f.read()

        magic = header_bytes[0:4]
        if magic != b"BHD5":
            raise ValueError(f"Invalid BHD5 header in {bhd_path}")

        bucket_count, buckets_offset = struct.unpack_from("<II", header_bytes, 16)
        hash_map: Dict[int, Tuple[int, int]] = {}

        pos = buckets_offset
        for _ in range(bucket_count):
            count, offset = struct.unpack_from("<II", header_bytes, pos)
            pos += 8
            curr_header = offset
            for _ in range(count):
                fhash, psize, foffset = struct.unpack_from("<IIQ", header_bytes, curr_header)
                hash_map[fhash] = (psize, foffset)
                curr_header += 16

        return hash_map

    def extract_raw_file(self, relative_asset_path: str, use_archive: int = 0) -> bytes:
        """Extracts the raw (possibly DCX-compressed) bytes of a file from dvdbnd0 or dvdbnd1."""
        if not self.is_installed():
            raise FileNotFoundError(f"Dark Souls Prepare to Die Edition not detected. Please verify installation.")

        bhd_path = self.dvdbnd0_bhd if use_archive == 0 else self.dvdbnd1_bhd
        bdt_path = self.dvdbnd0_bdt if use_archive == 0 else self.dvdbnd1_bdt

        if not bhd_path or not bhd_path.exists() or not bdt_path or not bdt_path.exists():
            raise FileNotFoundError(f"Missing archive files: {bhd_path} / {bdt_path}")

        index = self._read_bhd5_index(bhd_path)
        target_hash = from_path_hash(relative_asset_path)

        if target_hash not in index:
            raise KeyError(f"Asset '{relative_asset_path}' not found in archive dvdbnd{use_archive}.")

        psize, foffset = index[target_hash]

        with open(bdt_path, "rb") as f:
            f.seek(foffset)
            return f.read(psize)

    def decompress_dcx(self, dcx_bytes: bytes) -> bytes:
        """Decompresses FromSoftware DCX container into inner payload."""
        if not dcx_bytes.startswith(b"DCX\x00"):
            return dcx_bytes

        # Locate zlib magic header (0x78 0xDA / 0x9C / 0x01)
        zlib_start = dcx_bytes.find(b"\x78\xda")
        if zlib_start == -1:
            zlib_start = dcx_bytes.find(b"\x78\x9c")
        if zlib_start == -1:
            zlib_start = dcx_bytes.find(b"\x78\x01")
        if zlib_start == -1:
            raise ValueError("Unable to find standard zlib stream in DCX payload.")

        return zlib.decompress(dcx_bytes[zlib_start:])

    def unpack_bnd3(self, bnd_bytes: bytes) -> Dict[str, bytes]:
        """Parses a decompressed BND3 archive and extracts constituent files."""
        if not bnd_bytes.startswith(b"BND3"):
            raise ValueError("Data is not a valid BND3 container.")

        _, _, file_count, _ = struct.unpack_from("<8sIII", bnd_bytes, 4)
        files: Dict[str, bytes] = {}

        pos = 32
        for _ in range(file_count):
            _, size, offset, _, name_offset = struct.unpack_from("<B3xIIII", bnd_bytes, pos)
            name_end = bnd_bytes.find(b"\x00", name_offset)
            filename = bnd_bytes[name_offset:name_end].decode("ascii", errors="ignore").replace("\\", "/")
            basename = filename.split("/")[-1]
            files[basename] = bnd_bytes[offset:offset + size]
            pos += 24

        return files

    def extract_priscilla_assets(self, destination_dir: Path) -> Dict[str, Path]:
        """
        Extracts Crossbreed Priscilla's assets directly from user's installed game:
        - chr/c2730.chrbnd.dcx (Priscilla Model, FLVER, Textures)
        - chr/c2730.anibnd.dcx (Animations and TAE Timelines)
        - chr/c2731.chrbnd.dcx (Fluffy Tail Model)
        - parts/wp_a_0400.partsbnd.dcx (Lifehunt Scythe)
        """
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        results: Dict[str, Path] = {}

        system_logger.info("Extracting Crossbreed Priscilla (c2730) from Dark Souls PTDE...", source="DS1Extractor")

        targets = [
            ("c2730.chrbnd.dcx", "chr/c2730.chrbnd.dcx", 0),
            ("c2730.anibnd.dcx", "chr/c2730.anibnd.dcx", 0),
            ("c2731.chrbnd.dcx", "chr/c2731.chrbnd.dcx", 0),
            ("wp_a_0400.partsbnd.dcx", "parts/wp_a_0400.partsbnd.dcx", 1),
        ]

        for out_name, asset_path, archive_idx in targets:
            out_file = destination_dir / out_name
            raw_bytes = self.extract_raw_file(asset_path, use_archive=archive_idx)
            with open(out_file, "wb") as f:
                f.write(raw_bytes)
            results[out_name] = out_file
            system_logger.info(f"Extracted {out_name} ({len(raw_bytes):,} bytes)", source="DS1Extractor")

            # Extract internal files for inspectability
            try:
                decompressed = self.decompress_dcx(raw_bytes)
                if decompressed.startswith(b"BND3"):
                    unpacked = self.unpack_bnd3(decompressed)
                    sub_dir = destination_dir / out_name.replace(".dcx", "").replace(".", "_")
                    sub_dir.mkdir(exist_ok=True)
                    for sub_name, sub_bytes in unpacked.items():
                        sub_path = sub_dir / sub_name
                        with open(sub_path, "wb") as sf:
                            sf.write(sub_bytes)
                        results[f"{out_name}/{sub_name}"] = sub_path
            except Exception as e:
                system_logger.warning(f"Could not unpack subfiles for {out_name}: {e}", source="DS1Extractor")

        system_logger.info(f"Extraction complete! {len(results)} files stored in {destination_dir}", source="DS1Extractor")
        return results


# Backward compatibility and descriptive alias
DS1PTDEExtractor = DS1Extractor

