# Canada Central: Design Language

A reference for the visual language used across all dashboards, the scorecard, and the landing page. Every vertical has a consistent color, icon, and style so users can instantly recognize which category they're browsing.

---

## Foundation Palette

These are the base colors used across the entire site:

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-cream` | `#F0ECE3` | Page background |
| `--color-cream-dark` | `#E8E2D5` | Card visual backgrounds |
| `--color-beige` | `#D8D1C2` | Borders, dividers |
| `--color-white` | `#FEFEFE` | Card backgrounds |
| `--color-text-primary` | `#2D2D2D` | Headings, primary text |
| `--color-text-secondary` | `#5A5A5A` | Body text, descriptions |
| `--color-text-tertiary` | `#8A8A8A` | Subtitles, labels |

---

## Vertical Colors & Icons

Each of the 10 dashboard verticals has a unique **accent color** and **emoji icon**. The accent color is used for:
- The category tag/pill on index cards
- The chart's default bar/line color when viewing the national view
- The vertical's section header background tint
- Hover states and active indicators

| # | Vertical | Icon | Accent Color | Hex | CSS Variable |
|---|----------|------|-------------|-----|--------------|
| 1 | Fiscal: Deficit / Surplus | `📊` | Slate Blue | `#4A6FA5` | `--vertical-fiscal` |
| 2 | Fiscal: Net Debt | `📉` | Slate Blue | `#4A6FA5` | `--vertical-fiscal` |
| 3 | Fiscal: Revenue & Spending | `💰` | Slate Blue | `#4A6FA5` | `--vertical-fiscal` |
| 4 | Economy: GDP & Productivity | `🏭` | Forest Green | `#3D7A4A` | `--vertical-economy` |
| 5 | Economy: Employment | `👷` | Forest Green | `#3D7A4A` | `--vertical-economy` |
| 6 | Housing & Real Estate | `🏠` | Warm Orange | `#C4763C` | `--vertical-housing` |
| 7 | Crime & Public Safety | `🔴` | Crimson Red | `#A63D40` | `--vertical-crime` |
| 8 | Healthcare | `🏥` | Teal | `#3A7D8C` | `--vertical-health` |
| 9 | Demographics: Population & Immigration | `👥` | Purple | `#7C5A9D` | `--vertical-demographics` |
| 10 | Cost of Living & Inflation | `🛒` | Amber | `#B8860B` | `--vertical-cost` |
| 11 | Energy & Environment | `⚡` | Leaf Green | `#5A8F3D` | `--vertical-energy` |
| 12 | Education & Workforce | `🎓` | Navy Blue | `#2C5282` | `--vertical-education` |

### Grouping Logic

Verticals are organized into **categories** that share a color family:

- **Fiscal** (Slate Blue `#4A6FA5`): Deficit, Net Debt, Revenue & Spending — all share the same blue tone. Distinguished by different icons.
- **Economy** (Forest Green `#3D7A4A`): GDP, Employment — productive capacity of the economy.
- **Housing** (Warm Orange `#C4763C`): Housing starts, prices — the affordability crisis.
- **Crime** (Crimson Red `#A63D40`): Crime severity, public safety — urgency and danger.
- **Healthcare** (Teal `#3A7D8C`): Wait times, spending — medical/clinical association.
- **Demographics** (Purple `#7C5A9D`): Population growth, immigration — people and movement.
- **Cost of Living** (Amber `#B8860B`): CPI, inflation — financial/money association.
- **Energy** (Leaf Green `#5A8F3D`): Emissions, electricity — environmental association.
- **Education** (Navy Blue `#2C5282`): Schools, workforce — institutional/academic feel.

---

## Province Colors

When displaying multiple provinces on the same chart (or when a province is selected via entity chip), each province uses a consistent color:

| Province | Abbreviation | Color | Hex |
|----------|-------------|-------|-----|
| Canada (National) | CAN | Dark Grey | `#3D3D3D` |
| Alberta | AB | Deep Blue | `#1C4587` |
| British Columbia | BC | Dark Green | `#1B5E20` |
| Ontario | ON | Burgundy Red | `#8B1A1A` |
| Quebec | QC | Royal Blue | `#1565C0` |
| Saskatchewan | SK | Forest Green | `#2E7D32` |
| Manitoba | MB | Gold | `#B8860B` |
| New Brunswick | NB | Amber Orange | `#E65100` |
| Nova Scotia | NS | Deep Teal | `#00695C` |
| Newfoundland & Labrador | NL | Navy | `#0D47A1` |
| Prince Edward Island | PE | Terracotta | `#A0522D` |

These colors should be distinguishable when viewed side-by-side and remain readable on both light (cream) and white backgrounds.

---

## Entity Chip Styles

Entity chips follow this pattern:

```css
/* National chip */
.chip-national {
  background: #3D3D3D;
  color: white;
}

/* Province chips use their province color */
.chip-ab { background: #1C4587; color: white; }
.chip-bc { background: #1B5E20; color: white; }
/* etc. */

/* Selected state */
.chip.selected {
  box-shadow: 0 0 0 2px var(--province-color);
  font-weight: 700;
}

/* Unselected state */
.chip:not(.selected) {
  opacity: 0.6;
}
```

---

## Chart Conventions

### Bar Charts (default)
- Single entity: Use the entity's province color (or vertical accent color for national)
- Positive/negative split: Green `rgba(60, 140, 80, 0.7)` for positive, Red `rgba(180, 60, 60, 0.7)` for negative
- National average reference: Dashed line `rgba(0,0,0,0.35)`, 2px width

### Line Charts (overlays/trends)
- National average as dashed line when viewing individual provinces
- Province trend lines use province colors

### Data Tables
- Alternating row backgrounds: white / cream
- "vs National" column shows percentage or absolute difference
- Copy button: copies tab-separated values
- Download CSV button: generates downloadable file

---

## Index Page Card Categories

On the index page, cards are grouped by vertical category. Each category has:

1. A **section header** with the category icon and name
2. A subtle **left border** or **top accent** in the vertical color
3. Cards within the section follow the existing card layout

### Card Layout
```
[Icon] CATEGORY NAME (colored accent)
├── Dashboard Card 1
├── Dashboard Card 2
└── Dashboard Card 3
```

### Category Tag on Cards
Each card shows a small colored pill/tag with the vertical icon and category name:
```html
<span class="card-category" style="color: var(--vertical-fiscal)">
  📊 Fiscal
</span>
```

---

## Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page title | 2rem / 2.75rem | 800 | `--text-primary` |
| Section header | 1.25rem | 700 | `--text-primary` |
| Card title | 1.25rem / 1.5rem | 700 | `--text-primary` |
| Card subtitle | 0.6875rem | 600 | `--text-tertiary` |
| Card description | 0.875rem | 400 | `--text-secondary` |
| Category pill | 0.6875rem | 600 | Vertical accent color |
| Stat value | 2.5rem / 3rem | 800 | `--text-primary` |
| Stat label | 0.6875rem | 600 | `--text-tertiary` |

---

## Data Source Attribution

Every dashboard must include a source attribution line below the chart:

```
Source: [Organization] — Table [ID] | Last updated: [Date]
```

Formatted in `--text-tertiary` color, 0.75rem size. Links to the original StatCan/CMHC/Finance Canada page.

---

## Responsive Behavior

- **Desktop (768px+)**: Cards in horizontal layout (content + visual side by side)
- **Mobile (<768px)**: Cards stack vertically (visual below content)
- **Charts**: Full width with horizontal scroll for data tables on mobile
- **Entity chips**: Wrap to multiple lines on mobile, scrollable row on desktop
