# Datacuse editorial playbook

Saved September 18, 2026 from Sam Edelstein’s Datacuse brainstorming conversation.

## The direction

Datacuse as a collection of things that make people say, **“Wait, really? In Syracuse?”** Blend numbers, local memory, and affectionate curiosity about Syracuse. Write for curious residents, including people who would never seek out a dataset.

Sam’s inspirations were [I Quant NY](https://iquantny.tumblr.com/) and his friend’s [Ghosts of DC](https://ghostsofdc.org/). I Quant NY offers the model of asking ordinary questions of public data. Ghosts of DC offers little discoveries and forgotten history that make familiar places interesting. [Datacuse](https://www.datacuse.com/) can bring those approaches together.

Existing Datacuse work around properties, snow, libraries, and city services can supply smaller stories. One interesting observation can deserve its own post. The humor can come from the question and the observations; it does not need a punchline.

## The saved collection

- [Idea bank](datacuse-idea-bank.md): the original 365 pitches, numbered and grouped by topic.
- [Story tracker](datacuse-story-tracker.csv): one row per pitch, with permanent IDs and editable progress fields.
- This playbook: editorial approach, reusable templates, and tracking instructions.

The pitches are questions to investigate, not established findings. Data availability still needs checking. A headline should become a factual claim only once the evidence supports it. The collection is a bank to draw from, not a daily publishing obligation.

## Recurring formats and writing lengths

| Format | Shape |
| --- | --- |
| One weird thing | 100–200 words and one picture or chart. |
| Syracuse superlatives | Shortest, oldest, steepest, farthest, or most unusually shaped; define the comparison and verify the outlier. |
| This used to be… | An old map or photograph paired with present-day evidence. |
| I wondered… | A reader’s question, the investigation, and whatever answer survives checking. |

Allow three sizes: a 100-word curiosity, a roughly 300-word finding, or a longer story when the question warrants it. Most short posts could fit in 250–400 words.

Use the working constraint **one question, one visual, one finding, one source note**. An occasional field photograph can connect the spreadsheet to an actual street and give the story personality.

## A sustainable exploration habit

Set aside a weekly hour of exploring with no obligation to publish. Keep a running “huh, that’s odd” list. Publish when one of those observations becomes a small, defensible story. Follow whichever question catches your attention; an unexpected or unexciting answer is still a valid research outcome.

Use this sequence when it helps: pick a question, define what counts, find a source, do the smallest useful analysis, check the result against reality, make one visual, and write the short story. Add promising follow-up questions back to the bank.

## Investigation card

Copy this card into your research notes for an idea. Put its location in the tracker’s Draft Location field, or keep short notes directly in Research Notes.

| Field | What goes here |
| --- | --- |
| ID | The permanent tracker ID, such as DC001. |
| Question | One sentence in ordinary language. |
| Why I care | The observation, argument, memory, or joke that prompted it. |
| What counts? | The boundary and key terms: city or county, public trees or all trees, walking distance or straight-line distance. |
| First place to look | One primary dataset, map, archive, or field visit. |
| Smallest useful analysis | The simplest calculation or comparison that could answer the question. |
| Reality check | Check an outlier, inspect a map, compare another source, or visit the location. |
| The finding | What the evidence actually says, including an unexciting or unexpected answer. |
| The visual | One chart, map, photograph, or before-and-after pair. |
| The wrinkle | The limitation that could materially change how someone interprets it. |
| Next question | Anything interesting enough to add back to the idea bank. |

```text
ID:
Question:
Why I care:
What counts?:
First place to look:
Smallest useful analysis:
Reality check:
The finding:
The visual:
The wrinkle:
Next question:
```

## Reader-facing story template

**Headline:** Ask the question, or state the verified surprise.

**Opening:** “I was walking down ___ and wondered ___.” Use a real observation or motivation rather than inventing an experience.

**Answer:** Give readers the finding early.

**Evidence:** Show one visual and explain what to notice.

**Local detail:** Add the photograph, history, or observation that makes it feel like an actual place.

**Source note:** Link the data, give its date, and explain the important limitation.

```text
Working headline:
Opening:
Answer:
Visual and explanation:
Local detail:
Source note and limitation:
```

## Starting stories discussed

The initial favorite trio was Oak Street’s oaks (DC001), Syracuse’s shortest street (DC002), and Syracuse’s competing centers (DC005–DC007). These are specific, visual questions that are easy to explain to someone who does not care about data.

To pilot the template across different kinds of research, the later recommendation was:

- **DC001 — Oak Street’s trees:** compare tree-themed street names with a street-tree inventory and check what is actually there.
- **DC002 — The shortest street:** find the shortest named street, check that it is not a mapping artifact, and photograph it. A tiny biography of a tiny street.
- **DC100 — A vanished street’s surviving parcel lines:** compare historical maps with current parcels and locate a trace of the former city.

Together these try the template with data analysis, field observation, and historical research. These are recommendations only; no tracker priorities have been prefilled.

## Original pitch notes

The first brainstorming response included these additional angles. They are preserved here because the short titles in the 365-item bank do not capture every detail.

| Initial pitch | Investigation angle | Related IDs |
| --- | --- | --- |
| Does anyone on Oak Street actually have an oak tree? | Compare tree-themed street names with a street-tree inventory; make a map. | DC001, DC041 |
| Where is Syracuse’s middle, exactly? | Compare geographic center, population center, and residents’ idea of the center; visit the resulting spots. | DC005–DC007 |
| What’s Syracuse’s shortest street? | Check the shortest named street against mapping artifacts, then photograph it. | DC002 |
| How far can you get from a Dunkin’? | Find the farthest point within the city; repeat for libraries, parks, or pizza, using walking distance where it matters. | DC211, DC212, DC155, DC182 |
| Is your block older than your great-grandparents? | Map recorded building ages, find unusually intact blocks, and compare records with historical sources. | DC101–DC108 |
| When does Syracuse officially give up on winter? | Explore snowfall and relevant service requests for a seasonal turning point, without treating “collective optimism” as an observed measure. | DC073, DC081, DC086–DC088 |
| The street that disappeared but left its property lines behind | Compare an old map with current parcels. | DC100 |
| How much of downtown is a place to put a car? | Map surface parking and translate its area into familiar local places. | DC326, DC327 |
| The tree with no relatives nearby | Find an unusual recorded species, verify it, and tell the story of one tree. | DC032, DC033 |
| Was this really a normal Syracuse winter? | Test the neighborhood argument against weather records and what “normal” meant when different generations were children. | DC061, DC062 |

## Using the tracker

Open the CSV in Excel or import it into Google Sheets. It is UTF-8 with a byte-order mark for reliable punctuation handling in Excel. The first row contains headers. Freeze that row and turn on filters if useful. Always sort whole rows, so notes stay with their IDs.

CSV stores values only. It does not preserve dropdowns, formatting, multiple tabs, or a live progress dashboard. The formulas below are instructions for a spreadsheet you create from the CSV; they are not embedded in the CSV.

| Column | Use |
| --- | --- |
| A — ID | Permanent ID, initially DC001–DC365. Never reuse or renumber. |
| B — Category | Topic group from the idea bank. |
| C — Idea | Original pitch wording. Put working or final headlines in Research Notes. |
| D — Status | One of the seven statuses below. Initially Idea. |
| E — Priority | Optional High, Medium, or Low. Initially blank. |
| F — Research Notes | Investigation details, findings, limitations, or reason for parking/retiring. |
| G — Sources | Source links or citations, including data dates when known. Separate multiple references with semicolons. |
| H — Draft Location | File path or URL for the research card or draft. |
| I — Published URL | Link to the published story. |
| J — Date Completed | Publication date, entered as YYYY-MM-DD for portable CSV storage. |
| K — Related IDs | Related pitches, separated by semicolons, such as DC005; DC006. |

| Status | Meaning |
| --- | --- |
| Idea | Captured, but research has not started. |
| Researching | Looking for sources, analyzing, or verifying. |
| Drafting | Preparing the story and visual. |
| Ready | Finished and checked, awaiting publication. |
| Published | Published; counts as completed. Add the URL and publication date. |
| Parked | Paused for a source, season, time, or another dependency. Record why. |
| Retired | No longer pursuing this pitch. Keep its ID and record why. |

All 365 initial rows start as Idea. Progress fields other than Status are blank. These defaults do not assert whether any similar story has been published elsewhere.

### Counting progress in Excel or Google Sheets

After opening/importing the CSV, name its worksheet **Tracker**. Create a separate **Progress** worksheet. In Excel, save this working copy as an XLSX if you want to retain the extra sheet and formulas; in Google Sheets, keep them in the native spreadsheet.

On Progress, put these labels in column A and the matching formulas in column B:

| Cell | Label in column A | Formula in column B |
| --- | --- | --- |
| B2 | Total ideas, including additions | `=COUNTA(Tracker!A:A)-1` |
| B3 | Published ideas, including additions | `=COUNTIFS(Tracker!D:D,"Published")` |
| B4 | Completion, including additions | `=IF(B2=0,0,B3/B2)` |
| B5 | Published from original 365 | `=COUNTIFS(Tracker!D:D,"Published",Tracker!A:A,"DC???",Tracker!A:A,">=DC001",Tracker!A:A,"<=DC365")` |
| B6 | Completion of original 365 | `=B5/365` |

Format B4 and B6 as percentages. Initially the results are 365 total ideas, 0 published, and 0% completion. Retired and parked ideas stay in the denominator, so the original goal does not change silently. The original-365 formula matches the original three-digit IDs only, so later additions do not change that count.

For counts by status, put status labels in A9:A15 and enter `=COUNTIFS(Tracker!D:D,A9)` in B9, then fill down. These instructions work with the documented column order. If you rearrange columns, update the references.

These counts measure completed idea rows. If one story answers multiple pitches, mark a pitch Published only if the article actually answers it, and give the rows the same URL. The count may then be higher than the number of distinct articles.

## Expansion and upkeep

- Start new ideas at DC366 and use the next unused number. Keep IDs zero-padded to at least three digits and never renumber after sorting.
- Add each new pitch to the idea bank’s Future additions section with its ID, date added, and category. Add the same ID, category, and wording to the tracker with Status set to Idea.
- Preserve the original 365 pitches. Record refined questions or headlines in Research Notes, or create a linked new idea for a substantially different question.
- Use Related IDs to connect follow-ups, overlapping pitches, and multi-part stories. Retain retired rows so their history stays available.
- The Markdown bank is the readable pitch collection. The CSV is the source of truth for progress. Update progress in the CSV rather than maintaining separate checkboxes in Markdown.
- If you work primarily in Excel or Google Sheets, export the current Tracker sheet as UTF-8 CSV to replace this CSV after updates. Keep one working spreadsheet, rather than competing copies. Preserve the eleven columns and their order.
- Before replacing the CSV after a substantial update, keep a dated backup. Confirm that IDs, notes, punctuation, and row counts survive the export.

The next step can be picking a small starter batch, expanding selected pitches into investigation cards, or adapting the template after the three pilot stories.

## Current authoring location

The working collection now lives in `DataCuse/content/`. Each post uses a numbered folder such as `1_oak_street_trees`, containing `analysis/`, `images/`, and `story/index.md`. Create the next folder from the repo root with `npm run story:new -- 2_next_post_name`. The site build reads these folders directly; no import step is needed. Keep a post’s slug stable after publication and use its separate ideaId to connect it to the tracker. See the [publishing guide](../docs/story-publishing.md).
