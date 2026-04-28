"""Ensure Qt can load platform plugins even when QFile cannot list site-packages (sandbox/FS quirks)."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

# macOS user-flag that Finder/Qt treat as "hidden". PySide6 macOS wheels (>=6.10.x)
# ship plugin dylibs with this set, which makes Qt's QDir layer (and thus the
# platform plugin loader) skip them under the default filter.
_UF_HIDDEN = getattr(stat, "UF_HIDDEN", 0x8000)


def _pyside_plugin_root() -> Path | None:
    try:
        import PySide6
    except ImportError:
        return None
    base = Path(PySide6.__file__).resolve().parent
    p = base / "Qt" / "plugins"
    return p if p.is_dir() else None


def _plugins_cache_destination(plugin_root: Path) -> Path:
    """Flat temp path for mirrored ``Qt/plugins`` (platforms/styles/imageformats).

    Use ``/tmp/mlpqt-…`` (macOS ``realpath``), not nested ``…/ml-pipeline-studio/qt-plugins-…``.
    On some setups Qt's ``QDir`` refuses to enumerate the latter paths even though
    POSIX ``listdir`` succeeds; a short single-level dirname under ``/tmp`` behaves correctly.
    """

    try:
        import PySide6
    except ImportError:
        ver = "unknown"
    else:
        ver = PySide6.__version__

    slug = "".join(c if (c.isalnum() or c in "._-+") else "_" for c in ver)[:24].strip("_") or "pyside6"
    suffix = hashlib.sha256(os.fspath(plugin_root).encode()).hexdigest()[:14]

    if sys.platform == "darwin":
        base = Path(os.path.realpath("/tmp"))
    else:
        base = Path(tempfile.gettempdir()).resolve()

    return base / f"mlpqt-{slug}-{suffix}"


# Subset of `Qt/plugins` needed for widgets + cocoa; avoids huge trees (>20 bundles) that QFile
# sometimes refuses to enumerate in sandboxed IDE sessions.
_ESSENTIAL_PLUGIN_SUBDIRS = ("platforms", "styles", "imageformats")


def _qdir_any_entries(subdir: Path) -> bool:
    from PySide6.QtCore import QDir

    if not subdir.is_dir():
        return False
    dq = QDir(os.fspath(subdir))
    for ei in dq.entryInfoList():
        if ei.fileName() not in (".", ".."):
            return True
    return False


def _qdir_dylibs_visible(subdir: Path) -> bool:
    from PySide6.QtCore import QDir

    if not subdir.is_dir():
        return False
    dq = QDir(os.fspath(subdir))
    for glob in ("*.dylib", "*.dll", "*.so"):
        if dq.entryInfoList([glob]):
            return True
    return False


def _clear_hidden_flag_tree(root: Path) -> int:
    """Clear macOS ``UF_HIDDEN`` from every file/dir under ``root``.

    Returns the number of paths whose flags we successfully changed. Best-effort:
    silently ignores paths we can't chflags (e.g. read-only system installs).
    """

    if not hasattr(os, "chflags"):
        return 0
    cleared = 0
    for current_dir, dirnames, filenames in os.walk(root):
        for name in list(dirnames) + list(filenames):
            p = os.path.join(current_dir, name)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            flags = getattr(st, "st_flags", 0) or 0
            if flags & _UF_HIDDEN:
                try:
                    os.chflags(p, flags & ~_UF_HIDDEN)
                    cleared += 1
                except OSError:
                    pass
    return cleared


def _copy_minimal_plugin_tree(plugin_root: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=False)
    for name in _ESSENTIAL_PLUGIN_SUBDIRS:
        src_sub = plugin_root / name
        if src_sub.is_dir():
            shutil.copytree(src_sub, dest / name, symlinks=False)
    # ``shutil.copytree`` preserves ``st_flags`` (UF_HIDDEN) via ``copystat``; clear it
    # on the mirror so Qt's QDir default filter can enumerate the plugins.
    _clear_hidden_flag_tree(dest)


def _posix_platform_libs(platforms_dir: Path) -> list[Path]:
    if not platforms_dir.is_dir():
        return []
    return (
        sorted(platforms_dir.glob("*.dylib"))
        + sorted(platforms_dir.glob("*.so"))
        + sorted(platforms_dir.glob("*.dll"))
    )


def _cache_must_refresh(cache: Path, platform_src_dir: Path) -> bool:
    """POSIX-based checks avoid relying on QFile for the mirrored cache."""

    cq = cache / "platforms"
    dst_libs = _posix_platform_libs(cq)
    src_libs = _posix_platform_libs(platform_src_dir)
    if not dst_libs:
        return True
    markers = ("libqcocoa.dylib", "libqxcb.so", "qwindows.dll")
    marker_dst = None
    for name in markers:
        p = cq / name
        if p.is_file():
            marker_dst = p
            break
    if marker_dst is None:
        marker_dst = dst_libs[0]
    marker_src = None
    for name in markers:
        p = platform_src_dir / name
        if p.is_file():
            marker_src = p
            break
    if marker_src is None:
        marker_src = src_libs[0] if src_libs else platform_src_dir / marker_dst.name
    if not marker_src.exists():
        return True
    if not marker_dst.exists():
        return True
    return marker_src.stat().st_mtime_ns > marker_dst.stat().st_mtime_ns


def _effective_plugin_root(plugin_root: Path, platforms_dir: Path) -> Path:
    """If Qt can't see platform binaries or the plugins root via QFile, mirror a minimal subtree."""

    platforms_ok = _qdir_dylibs_visible(platforms_dir)
    root_readable = _qdir_any_entries(plugin_root) and _qdir_any_entries(platforms_dir)
    if platforms_ok and root_readable:
        return plugin_root

    # PySide6 macOS wheels ship plugin dylibs with ``UF_HIDDEN`` set, which makes
    # Qt's QDir default filter skip them. Try to clear it in-place first so we
    # don't have to mirror to a temp dir; fall back to the mirror if chflags
    # fails (read-only fs) or QDir still can't enumerate.
    if _clear_hidden_flag_tree(plugin_root):
        if _qdir_dylibs_visible(platforms_dir) and _qdir_any_entries(plugin_root):
            return plugin_root

    cache = _plugins_cache_destination(plugin_root)

    if _cache_must_refresh(cache, platforms_dir):
        if cache.exists():
            shutil.rmtree(cache)
        cache.parent.mkdir(parents=True, exist_ok=True)
        _copy_minimal_plugin_tree(plugin_root, cache)
    else:
        # Existing cache could have been mirrored before we knew about UF_HIDDEN.
        _clear_hidden_flag_tree(cache)

    return cache


def apply_qt_plugin_environment() -> None:
    """Set QT_PLUGIN_PATH to a folder Qt's QFile layer can enumerate; strip empty placeholders."""

    plugin_root = _pyside_plugin_root()
    if plugin_root is None:
        return

    for key in ("QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        raw = os.environ.get(key)
        if raw is not None and not str(raw).strip():
            os.environ.pop(key, None)

    platforms_dir = plugin_root / "platforms"
    effective = _effective_plugin_root(plugin_root, platforms_dir)

    os.environ["QT_PLUGIN_PATH"] = os.fspath(effective)
