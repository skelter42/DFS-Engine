# Projection Model v3

Search Vegas odds and props. Convert them into site points. That is the projection source.

No prop: DFS-site median. No site number: Savant, unchanged. Savant 0 stays 0. Own stays unchanged.

Plus price: `100 / (odds + 100)`. Minus price: `odds / (odds + 100)`. Do not flip a plus price.

Details of the conversion are in `core/VEGAS_CONSENSUS.md`.
