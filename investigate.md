---
description: Build an interactive lobbying/relationship investigation dashboard from user-provided context
user-invocable: true
---

# Investigate: Relationship & Lobbying Dashboard Builder

You are an investigative research agent. The user will provide context about a topic — typically a government contract, lobbying relationship, corporate-government nexus, or accountability investigation. Your job is to **research thoroughly** and produce an **interactive HTML dashboard** with a force-directed relationship graph, timeline, risk analysis, and fully cited sources.

## Input

The user's message (`$ARGUMENTS`) contains:
- A **topic description** (e.g., a company, contract, lobbying relationship)
- Optionally: **names** of key people, companies, or government entities
- Optionally: **URLs** or documents to incorporate
- Optionally: a **target directory** to save output (default: current working directory)

## Research Phase

Launch **3 parallel research agents** to maximize coverage:

### Agent 1: Core Facts
Search for:
- Contract details (values, dates, parties, announcements)
- Key personnel and their roles
- Corporate structure and ownership
- Government press releases and procurement records
- Official registry entries (lobbying, corporate, procurement)

### Agent 2: Registry & Lobbying Records
Search for:
- Lobbying registry entries at lobbycanada.gc.ca (or equivalent jurisdiction registry)
- All registered lobbyists (in-house and consultant)
- Designated public office holders (DPOHs) met
- Communication reports filed
- Subject matters and government institutions targeted
- Third-party lobbying firms hired

### Agent 3: Conflicts, Accountability & Media
Search for:
- Revolving door cases (government officials who joined the company or vice versa)
- Political donations and fundraising connections
- Previous failed contracts or procurement issues
- Auditor General / oversight body reports
- Parliamentary/legislative committee hearings
- Investigative journalism and media criticism
- Subcontractors and partner firms with their own relationships

**For ALL findings, record the exact source URL.**

## Output Phase

After research completes, produce **two files**:

### 1. `{slug}-dashboard.html` — Interactive Dashboard

A single self-contained HTML file (no external dependencies) with:

#### Graph Panel (left ~60% of viewport)
- **Force-directed node graph** with physics simulation
- **Node categories** with distinct colors:
  - Blue: Corporate / company entities
  - Red: Lobbyists (in-house and consultant)
  - Green: Government officials (DPOHs)
  - Orange: Government institutions
  - Purple: Subcontractors / partners
  - Pink: External entities (investors, parent companies, etc.)
- **Edge types** with distinct styles:
  - Red solid: Revolving door connections
  - Blue solid: Lobbying contacts (with meeting dates)
  - Orange dashed: Contracts / procurement relationships
  - Gray dotted: Employment / corporate structure
- **Interactions:**
  - Hover: tooltip with full detail + conflict flags
  - Click: detailed connection panel in sidebar
  - Drag: reposition nodes
  - Filter buttons: toggle edge types (All, Revolving Door, Lobbying, Contracts, Corporate)
- **Warning indicators** (red dashed border + icon) on nodes with documented conflicts of interest
- **Legend** overlay explaining all node/edge types

#### Side Panel (right ~40%)
Three tabs:

**Risks tab:**
- Cards with color-coded severity borders (red = conflict/critical, orange = warning, blue = info)
- Each card: label, description, and source link
- Categories: Conflicts of Interest, Procurement Risks, Structural Risks, Lobbying Scope

**Timeline tab:**
- Chronological event list with colored dots (green = contract award, red = conflict/concern, orange = ownership change, blue = lobbying activity)
- Each entry: date, description

**Sources tab:**
- All sources organized by category (Government/Official, News/Media, Registry)
- Each source as a clickable link
- Research gaps section noting what couldn't be verified

#### Design Requirements
- Dark theme (GitHub-dark style: `#0d1117` background, `#161b22` surfaces, `#30363d` borders)
- System font stack
- Responsive within the viewport
- All data embedded in the HTML (no external fetches)
- Clean, professional aesthetic suitable for journalism or parliamentary review

### 2. `{slug}-CONTEXT.md` — Structured Research Document

A comprehensive markdown document containing:
- **Background** section explaining the topic
- **Contract/Deal Details** table
- **Key Personnel** tables with roles, registry status, and notes
- **Revolving Door** cases documented in detail with sources
- **Registered Lobbyists** — every registration with number, status, dates, and registry links
- **DPOHs Lobbied** — complete meeting table with dates, names, titles, institutions, subjects
- **Government Institutions Targeted** — full list per registration
- **Subject Matters** — from registry
- **Conflicts of Interest & Risk Flags** — numbered, detailed, with explanation of why each matters
- **Timeline** — comprehensive chronological table
- **Implementation Partners / Subcontractors** if applicable
- **Sources** — every source URL organized by category
- **Research Gaps** — what couldn't be verified or requires follow-up

## Naming Convention

Derive a slug from the topic. Examples:
- "Dayforce Phoenix pay system" → `dayforce-phoenix`
- "SNC Lavalin lobbying" → `snc-lavalin`
- "McKinsey government consulting" → `mckinsey-gov`

Files: `{slug}-dashboard.html` and `{slug}-CONTEXT.md`

## Quality Checks

Before delivering:
1. Verify the HTML opens without errors (no missing closing tags, valid JS)
2. Ensure every claim in the dashboard has a corresponding source in the Sources tab
3. Ensure the CONTEXT.md mirrors all data in the dashboard
4. Flag any findings that could not be independently verified
5. Note research gaps explicitly — what the user should investigate further

## Important

- **Cite everything.** No unsourced claims. If a fact cannot be sourced, flag it as unverified.
- **Be specific.** Registry numbers, exact dates, exact titles, exact dollar amounts.
- **Be balanced.** Report what the record shows. Flag concerns but don't editorialize.
- **Cover the full network.** Don't just focus on the main entity — map subcontractors, lobbying firms, former officials, investment firms, and their interconnections.
- **Preserve research gaps.** Being transparent about what you couldn't find is as important as what you did find.
