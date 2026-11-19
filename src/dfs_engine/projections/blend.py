"""Books drive. Savant is the fallback.

A book number is used only when the scoring prices for that player were posted.
A missing market is not filled. A Savant zero stays zero.
"""

from __future__ import annotations


_INTERNAL_FIELDS = {"name", "dfs_id", "savant", "own", "books", "book_complete"}


def blend_row(book_points, savant, book_complete: bool) -> tuple[float, str]:
    if savant == 0:
        return 0.0, "zero"
    if book_complete and book_points is not None:
        return float(book_points), "books"
    return float(savant), "savant"


def blend_frame(rows: list[dict]) -> list[dict]:
    """Return blended rows without dropping source CSV columns.

    Lower-case keys are the normalized helper inputs used by the projection
    step. All other keys are treated as original source columns and retained.
    The original Proj is replaced; Name, DFS ID, Own, row order, and every
    other source value remain unchanged. Audit metadata is retained separately
    from the source columns for the reconciliation writer.
    """
    out = []
    for row in rows:
        savant = row["savant"]
        proj, source = blend_row(
            row.get("books"), savant, row.get("book_complete", False)
        )

        # Preserve the original CSV fields. The normalized lower-case keys
        # below are internal inputs, not output columns.
        result = {
            key: value
            for key, value in row.items()
            if key not in _INTERNAL_FIELDS
        }
        result.setdefault("Name", row.get("name", row.get("Name")))
        dfs_id = row.get("dfs_id", row.get("DFS ID", row.get("DFS_ID")))
        if dfs_id is not None:
            result.setdefault("DFS ID", dfs_id)
        result["Proj"] = round(proj, 2)
        own = row.get("own", row.get("Own"))
        if "Own" not in result and own is not None:
            result["Own"] = own

        # Reconciliation metadata; original source columns above are untouched.
        result["source"] = source
        result["savant"] = savant
        result["books"] = row.get("books")
        out.append(result)
    return out
