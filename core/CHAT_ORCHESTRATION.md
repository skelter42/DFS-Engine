# Chat-First Orchestration

The user operates the DFS Engine primarily through ChatGPT conversations. GitHub is the durable memory, rules, and process layer; it is not intended to become a manual interface the user must operate.

## Primary Principle

99% of interaction happens in chat.

The user should be able to send natural-language instructions and slate artifacts such as projections, contest CSVs, entry files, results, screenshots, or links. The assistant is responsible for determining which engine components to invoke, reading the relevant GitHub brain files, executing the slate workflow, returning the finished decision package, and persisting only durable improvements back to GitHub.

## Invocation Model

The user does not need to name agents or functions. Infer the workflow from intent.

Examples:

- "Run the DFS Engine" -> invoke slate ingestion, validation, market/context cross-check, sport logic, contest logic, portfolio construction, exposure audit, and final output.
- "Build MLB lineups" -> load core rules + MLB brain + contest profile + current slate files.
- "Do the full industry compare" -> invoke projection/ownership/context cross-check before portfolio construction.
- "Send exposures side by side" -> produce source projected ownership vs DFS Engine final exposure with percentage-point difference.
- "What did we learn?" -> invoke post-slate review and durable-learning filter.
- "Update the engine" -> persist validated durable process improvements to GitHub.
- "Run a what-if" -> preserve the original build, alter only the requested assumption, and compare outputs.

## Automatic Routing

At the start of a slate task, infer:

1. sport
2. site
3. slate
4. contest type and entry count when available
5. available projection/ownership sources
6. required market/context checks
7. sport-specific correlation and stack rules
8. portfolio size and uniqueness requirements
9. whether this is pre-lock, late-swap, what-if, or post-slate analysis

Then load only the relevant brain files and execute the workflow.

## GitHub Responsibilities

GitHub stores:

- canonical engine rules
- sport-specific brains
- contest profiles
- schemas/output contracts
- agent responsibilities
- validated durable learnings
- version history
- future executable helpers when useful

GitHub should NOT become a dump of every slate-specific thought, raw chat, or noisy outcome. Persist only reusable knowledge, rules, tested hypotheses, and process changes.

## Chat Responsibilities

Chat handles:

- current slate data
- current web/industry research
- user intent
- live lineup decisions
- portfolio generation
- explanations
- what-if analysis
- post-slate diagnosis
- deciding what deserves promotion into durable engine memory

## Default Behavior

When the user supplies DFS files or asks to run the engine, do not require them to explain the workflow again. Read the relevant GitHub brain first, apply it, then return the finished slate package.

When a new durable lesson is found, update the GitHub brain as part of the workflow when appropriate. Do not overwrite established logic based on one noisy slate; record hypotheses separately until supported.

## User Experience Target

The ideal interaction is:

1. User uploads files or says what slate to run.
2. Assistant recognizes the task automatically.
3. Assistant retrieves the correct stored process.
4. Assistant performs research and analysis.
5. Assistant constructs the portfolio.
6. Assistant returns lineups plus required diagnostics.
7. Assistant reviews results later.
8. Assistant stores only durable improvements.

The user should not need to manage the internal agent system, code paths, repository structure, or configuration files to use the DFS Engine.
