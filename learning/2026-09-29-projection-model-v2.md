# 2026-09-29 — Projection model v2, site median blended with the prop

- Sport: all Market Inputs / Savant Prep
- Status: validated (user direction)
- Evidence: User wants a blend of DFS-site projections backed by Vegas odds and props, not a band that leaves the site median unchanged unless it sits outside a fence.
- Durable lesson: When both exist, Proj = 0.50 × DFS-site median + 0.50 × de-vigged Vegas prop. Sites are blended by median first. Vegas is the other half, one number, not one vote per book. Savant is not in the blend. No prop: site median stands.
- Engine impact: `core/PROJECTION_MODEL.md` is now v2. v1 band rule is retired.
- Revisit condition: change the split only after three logged slates if a new split beats v2 on absolute error.
