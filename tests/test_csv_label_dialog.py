"""CSV label picker helpers (no GUI)."""

from __future__ import annotations

from pathlib import Path

from ml_pipeline_studio.ui.csv_preview import (
    read_csv_column_names,
    read_csv_preview,
    read_csv_raw_rows,
)


def test_read_csv_preview(tmp_path: Path) -> None:
    p = tmp_path / "t.csv"
    p.write_text("feat_a,feat_b,target\n1,2,0\n3,4,1\n5,6,0\n", encoding="utf-8")
    cols, rows = read_csv_preview(p)
    assert cols == ["feat_a", "feat_b", "target"]
    assert len(rows) == 3
    assert rows[0] == [1, 2, 0]


def test_read_csv_preview_skips_metadata_header(tmp_path: Path) -> None:
    p = tmp_path / "meta.csv"
    p.write_text("junk line\na,b,c\n1,2,3\n", encoding="utf-8")
    cols, rows = read_csv_preview(p, header_row=1, nrows=5)
    assert cols == ["a", "b", "c"]
    assert len(rows) == 1
    assert rows[0] == [1, 2, 3]


def test_read_csv_column_names(tmp_path: Path) -> None:
    p = tmp_path / "wide.csv"
    p.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
    assert read_csv_column_names(p) == ["a", "b", "c"]


def test_read_csv_raw_rows(tmp_path: Path) -> None:
    p = tmp_path / "raw.csv"
    p.write_text("x,y\n1,2\n", encoding="utf-8")
    assert read_csv_raw_rows(p, max_lines=10) == [["x", "y"], ["1", "2"]]
