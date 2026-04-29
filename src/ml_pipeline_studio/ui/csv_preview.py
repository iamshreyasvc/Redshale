"""CSV header and row preview (pandas only; no Qt)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd


def read_csv_raw_rows(path: Path, *, max_lines: int = 50) -> list[list[str]]:
    """First ``max_lines`` logical rows as cell lists (csv.reader; no header assumption)."""
    out: list[list[str]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= max_lines:
                break
            out.append([str(c) for c in row])
    return out


def _read_csv_df(path: Path, *, header_row: int, nrows: int | None) -> Any:
    kw: dict[str, Any] = {
        "header": header_row,
        "encoding": "utf-8",
        "encoding_errors": "replace",
    }
    if nrows is not None:
        kw["nrows"] = nrows
    try:
        return pd.read_csv(path, **kw)
    except TypeError:
        kw.pop("encoding_errors", None)
        return pd.read_csv(path, **kw)


def read_csv_preview(
    path: Path, *, nrows: int = 5, header_row: int = 0
) -> tuple[list[str], list[list[Any]]]:
    """Return column names and data rows for preview (raises on failure)."""
    df = _read_csv_df(path, header_row=header_row, nrows=nrows)
    cols = [str(c) for c in df.columns.tolist()]
    rows: list[list[Any]] = []
    for _, row in df.iterrows():
        rows.append([row[c] for c in df.columns])
    return cols, rows


def read_csv_column_names(path: Path, *, header_row: int = 0) -> list[str]:
    """Return column names for the given header row index (0 = first line of file)."""
    df = _read_csv_df(path, header_row=header_row, nrows=0)
    return [str(c) for c in df.columns.tolist()]
