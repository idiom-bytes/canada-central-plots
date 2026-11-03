# Treaty/Resource-Land Investigations — Index

Per-Nation investigative dossiers (relationship graph + sourced research document)
mapping financial stakeholders, officials, and advocacy/NGO networks around specific
First Nations treaty or resource-land agreements. Distinct from the public-facing
`reports/` Story/Chapter pages built by `report_architect` — these are the underlying
network-mapping dossiers, not polished public pages (though they can link to/from one).

**The full process — schema, phases, quality bar, known tooling gotchas — now lives in
the skill: `.claude/skills/investigate_treaty_land/SKILL.md`.** Read that before
starting a new investigation or continuing an existing one; it supersedes any schema
detail that used to live in this file. This file is now just the index of what's done.

```
investigations/{slug}/{slug}-dashboard.html   — interactive relationship graph
investigations/{slug}/{slug}-CONTEXT.md       — full sourced research document
investigations/{slug}/research-*.md           — working research files (audit trail)
investigations/{slug}/MANUAL-STEPS.md         — human-actionable unblock checklist
```

## Completed / in-progress investigations

- **Tahltan** (`investigations/tahltan/`, built 2026-08-12, three follow-on passes same
  day) — 44 nodes / 63 edges. Central finding: the viral "$1.28T in minerals / Tahltan
  land transfer" claim conflates a 2022 BC Geological Survey regional
  mineral-endowment estimate (never mentions Tahltan) with an unsigned, undisclosed
  "Foundation Agreement" (revealed only via FOI). Documented conflict-adjacent finding:
  former Minister of Energy and Mines Bill Bennett moved to mining-company boards after
  leaving office, including one operating inside Tahltan territory — and separately
  holds that company's seat on the Mining Association of BC's board, whose 48 seats
  otherwise include every one of the six mapped companies (normal trade-association
  structure, not itself a conflict). AME and PLUS share a director (Jonas Rigaux) — the
  clearest documented personnel link between the industry-lobbying and
  FOI-transparency sides. The environmental NGO cluster (Northern Confluence/
  SkeenaWild/Salmon Beyond Borders/MiningWatch) shows a real documented advocacy
  network but no financial ties to the mining side. SkeenaWild's own funding is
  verified (via CRA bulk open data, not a summary site) at ~86% federal government in
  FY2024. A newer, distinct opposition voice — the K'adesibe Collective, anonymous by
  stated necessity — raised free/prior/informed-consent concerns about the Eskay Creek
  vote alongside a former interim TCG president; reported factually, not conflated with
  Klabona Keepers, not treated as invalidating the official vote record. No evidence
  found of foreign government interference specific to this territory. Several gaps
  remain genuinely open (Elections BC donations, federal lobbyist registry, Klabona
  Keepers' 2023–2026 status) — see `investigations/tahltan/MANUAL-STEPS.md` for exactly
  what a human with a browser could resolve next.
- **Songhees / Te'mexw** — not yet built as a standalone investigation of this type.
  Significant background already exists in `reports/bc-treaty-victoria.html` (the Story
  chapter) and `docs/research-songhees-victoria.md` — reuse as a starting point rather
  than re-researching from scratch, but still run the skill's Phase 2 research angles
  (financial stakeholders, officials/conflicts, NGO/advocacy) since the Story chapter
  didn't cover those.
