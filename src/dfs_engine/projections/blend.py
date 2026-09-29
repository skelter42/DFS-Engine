"""Books drive. Savant is the fallback.

A book number is used only when the scoring prices for that player were posted.
A missing market is not filled. A Savant zero stays zero.
"""

from __future__ import annotations


def blend_row(book_points, savant, book_complete: bool) -> tuple[float, str]:
    if savant == 0:
        return 0.0, "zero"
    if book_complete and book_points is not None:
        return float(book_points), "books"
    return float(savant), "savant"


def blend_frame(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        proj, source = blend_row(row.get("books"), row["savant"], row.get("book_complete", False))
        out.append(
            {
                "Name": row["name"],
                "DFS ID": row.get("dfs_id"),
                "Proj": round(proj, 2),
                "Own": row.get("own"),
                "source": source,
                "savant": row["savant"],
                "books": row.get("books"),
            }
        )
    return out
