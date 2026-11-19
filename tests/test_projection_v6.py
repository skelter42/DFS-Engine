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


def test_blend_frame_preserves_all_original_csv_columns():
    rows = [
        {
            "Name": "First",
            "DFS ID": "1",
            "Proj": 10.0,
            "Own": 12.0,
            "Team": "BOS",
            "Salary": 5000,
            "Roster Position": "OF",
            "name": "First",
            "dfs_id": "1",
            "savant": 10.0,
            "own": 12.0,
            "books": 11.25,
            "book_complete": True,
        },
        {
            "Name": "Second",
            "DFS ID": "2",
            "Proj": 8.0,
            "Own": 7.0,
            "Team": "NYY",
            "Salary": 4500,
            "Roster Position": "OF",
            "name": "Second",
            "dfs_id": "2",
            "savant": 8.0,
            "own": 7.0,
            "books": None,
            "book_complete": False,
        },
    ]

    out = blend_frame(rows)

    assert [row["Name"] for row in out] == ["First", "Second"]
    assert [row["DFS ID"] for row in out] == ["1", "2"]
    assert [row["Own"] for row in out] == [12.0, 7.0]
    assert [row["Proj"] for row in out] == [11.25, 8.0]
    assert [(row["Team"], row["Salary"], row["Roster Position"]) for row in out] == [
        ("BOS", 5000, "OF"),
        ("NYY", 4500, "OF"),
    ]


def test_flattened_board_is_rejected_by_line_variation_check():
    assert not lines_vary([{"line": 2.5}, {"line": 2.5}])
    assert lines_vary([{"line": 2.5}, {"line": 3.5}])
