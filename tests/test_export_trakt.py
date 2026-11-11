"""Offline tests for export_trakt.write_csv (no Trakt API needed)."""

import csv
from types import SimpleNamespace

import export_trakt


def _options(tmp_path, **kwargs):
    params = {
        "verbose": False,
        "sortorder": "asc",
        "time": "watched_at",
        "output": str(tmp_path / "out.csv"),
    }
    params.update(kwargs)
    return SimpleNamespace(**params)


def test_write_csv_empty_results(tmp_path, capsys):
    """Exporting an empty list must not crash with IndexError."""
    options = _options(tmp_path)
    export_trakt.write_csv(options, [])
    out = capsys.readouterr().out
    assert "No results found" in out


def test_write_csv_rows_sorted(tmp_path):
    """Rows are sorted by the time key and round-trip through CSV."""
    options = _options(tmp_path)
    results = [
        {"title": "B", "watched_at": "2024-02-01"},
        {"title": "A", "watched_at": "2024-01-01"},
    ]
    export_trakt.write_csv(options, results)
    with open(options.output, newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    assert [row["title"] for row in rows] == ["A", "B"]
