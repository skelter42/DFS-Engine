from dfs_engine.projections.blend import blend_frame, blend_row
from dfs_engine.projections.pull import lines_vary


def test_books_replace_positive_savant_only_when_complete():
    assert blend_row(18.25, 20.0, True) == (18.25, "books")
    assert blend_row(18.25, 20.0, False) == (20.0, "savant")
    assert blend_row(None, 20.0, False) == (20.0, "savant")


def test_savant_zero_always_stays_zero():
    assert blend_row(18.25, 0, True) == (0.0, "zero")


def test_import_identity_order_and_own_are_preserved():
    rows = [
        {"name": "First", "dfs_id": "1", "savant": 10.0, "own": 12.0,
         "books": 11.25, "book_complete": True},
        {"name": "Second", "dfs_id": "2", "savant": 8.0, "own": 7.0,
         "books": None, "book_complete": False},
    ]
    out = blend_frame(rows)
    assert [(r["Name"], r["DFS ID"], r["Own"]) for r in out] == [
        ("First", "1", 12.0),
        ("Second", "2", 7.0),
    ]
    assert [r["Proj"] for r in out] == [11.25, 8.0]


def test_flattened_board_is_rejected_by_line_variation_check():
    assert not lines_vary([{"line": 2.5}, {"line": 2.5}])
    assert lines_vary([{"line": 2.5}, {"line": 3.5}])
