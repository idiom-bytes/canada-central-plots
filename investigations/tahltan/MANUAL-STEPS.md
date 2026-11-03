# Manual steps to unblock deeper Tahltan research

These are real, working tools that this investigation could not finish querying because
they require a browser (JavaScript execution) or were blocked to automated requests.
Nothing here requires filing a new FOI/FOIPPA/ATIA request — these are all read-only
lookups against tools that already exist. Each entry: what to do, how long it takes,
and exactly what it would resolve.

## 1. Check if the Tahltan Foundation Agreement FOI response is already public (~1 min)

**Do this:** Open [BC's completed FOI requests search](https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/completed-foi-requests), then use its "Search the catalogue" tool. Search `Tahltan` and separately `Foundation Agreement`. Also try the ministry filter for "Indigenous Relations and Reconciliation."

**Why I couldn't do it:** The search results are rendered client-side by JavaScript; my fetch tool only sees the empty page shell, not results.

**What it would resolve:** Whether Public Land Use Society's (or anyone else's) completed FOI request for the Foundation Agreement records is already catalogued for reuse — if so, we could request a copy of that exact already-processed release, which is faster/cheaper than a fresh request and doesn't require re-doing the disclosure review.

## 2. Search Elections BC for individual donations (~5 min)

**Do this:** Go to the [Financial Reports and Political Contributions System](https://contributions.electionsbc.gov.bc.ca/pcs/Welcome.aspx), click through to Options.aspx, select "Political Contributions," and search the contributor-name field for: `Bennett` (Bill Bennett), `Edwards` (N. Murray Edwards), `Keevil` (Teck's controlling family), and if you have time, the names of any of the six mining companies (contributions were banned from corporations post-2017, so this mainly matters for the pre-2017 window and for individual executives).

**Why I couldn't do it:** I found the exact tool and its form field names (`txtContributor` etc.) and scripted the submission, but every attempt returned a server-side "FRPC Exception" — likely a client-side value the form needs that a script doesn't reproduce. This is a documented, reproducible gap, not a dead end — a real browser session should just work.

**What it would resolve:** Whether Bill Bennett (the investigation's one documented revolving-door case) or any mining-company executive personally donated to BC political parties, and whether that connects to any Tahltan-specific decision. Right now the only known fact is general (Teck was the BC Liberals' largest donor pre-2017), with no source tying it to Bennett specifically.

## 3. Search the federal lobbyist registry (~5 min)

**Do this:** Go to [lobbycanada.gc.ca](https://lobbycanada.gc.ca/en/) and search the registry for: Teck Resources, Newmont Canada Corporation, Seabridge Gold, Skeena Resources / Skeena Gold & Silver. Look for any registration mentioning Tahltan, Red Chris, Galore Creek, Schaft Creek, Eskay Creek, or KSM specifically.

**Why I couldn't do it:** The site sits behind a Cloudflare bot-challenge that blocks non-browser requests — confirmed two independent ways (WebFetch and a direct scripted request), including on the bulk-data download files. A real browser should pass this without issue.

**What it would resolve:** Whether these companies' federal-level lobbying (as opposed to the BC-level lobbying already documented for AME and MABC) specifically targeted Tahltan-related federal decisions — federal Impact Assessment Act approvals, the Major Projects Office listing for Red Chris, etc.

## 4. Check for recent Klabona Keepers activity (~5 min, optional)

**Do this:** If you have access to social media search or local northwestern-BC news sources beyond what I could reach (The Narwhal, Tahltan Central Government's own site — both checked directly, nothing found), a quick check of Facebook/Instagram (Klabona Keepers has historically organized partly through social media, per older reporting) or a call to a Terrace/Iskut-area contact could establish whether the group is still active.

**Why I couldn't do it:** No social media access in this session; both the most likely web sources were checked directly and came back empty for 2023–2026.

**What it would resolve:** Whether the group's apparent quiet since September 2022 reflects reduced activity or just reduced press coverage — currently an open, unresolved gap either way.

## Not on this list: actually filing a new FOI/FOIPPA request

You told me you're not ready to file requests yet — noted, nothing here requires that.
If that changes, the next document to write would be a draft FOIPPA request to the
Ministry of Indigenous Relations and Reconciliation for the Foundation Agreement text,
built directly on what PLUS's reporting already establishes exists. I can draft that text
whenever you want it, but actually submitting it needs your identity/contact info and a
web form, which I can't do for you in this session.
