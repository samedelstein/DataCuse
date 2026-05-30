# Syracuse Code Violations V2 — Open Violations Profile

Source: `https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Code_Violations_v2/FeatureServer/0`

Query date: 2026-05-29

## Headline

The dataset does show a very large open count, but the count is at the **violation row** level, not at the case, property, or complaint level.

- Total violation rows: 147,114
- Closed violation rows: 128,948
- Open violation rows: 18,166
- Distinct open complaint numbers: 7,279
- Distinct open SBL parcels: 5,246
- Distinct open complaint addresses: 5,247

So the “17k open violations” reading is directionally real, but it should not be interpreted as 17k separate properties or 17k separate active cases.

## Why the count is high

### 1. One complaint/case can contain many violation rows

The open rows collapse to 7,279 complaint numbers. Multi-row complaints account for most open rows:

- 4,330 complaint numbers have 1 open row
- 964 have 2 open rows
- 1,187 have 3–5 open rows
- 601 have 6–10 open rows
- 179 have 11–20 open rows
- 18 have 21+ open rows
- 13,836 of the 18,166 open rows are in multi-row complaints

Example: complaint `2017-16405` has 51 open rows at `3501 James St & Walter Dr & La`.

### 2. Some properties accumulate many open rows across multiple complaints

Top open-row parcel examples:

- SBL `072.-14-02.0`, `141-69 Ballantyne Rd`: 144 open rows across 30 distinct complaints
- SBL `058.-09-22.0`, `420 Jamesville Ave & Smith La`: 66 open rows across 19 distinct complaints
- SBL `018.-10-11.0`, `701 Lodi St & Green St`: 56 open rows across 9 distinct complaints
- SBL `025.-02-01.0`, `3501 James St & Walter Dr & La`: 51 open rows in 1 complaint

### 3. The open population is heavily long-lived

Open rows by `open_date` year:

- 2012: 4
- 2013: 2
- 2014: 5
- 2015: 6
- 2016: 26
- 2017: 206
- 2018: 166
- 2019: 238
- 2020: 462
- 2021: 1,677
- 2022: 1,427
- 2023: 2,835
- 2024: 2,768
- 2025: 4,557
- 2026: 3,787

Open age buckets as of 2026-05-29:

- 0–30 days: 1,149
- 31–90 days: 1,476
- 91–180 days: 1,690
- 181–365 days: 2,448
- 1–2 years: 3,274
- 2–3 years: 2,332
- 3+ years: 5,797

### 4. Most open rows are past their comply-by date

- Past comply_by_date: 17,200
- Due next 30 days: 952
- Due 31–180 days: 5
- Missing/invalid comply_by_date: 9

This may reflect unresolved issues, but it may also reflect stale closure/status workflows or long-running cases where old violation rows remain open.

## Largest open categories

Open rows by complaint type:

- Property Maintenance-Int: 4,678
- Vacant House: 3,882
- Property Maintenance-Ext: 2,663
- Rental Registry: 2,489
- Certificate of Compliance: 2,344
- Smoke Alarm Certification: 343
- Sprinkler System: 275
- Cert of Use - Food Store: 256
- Cert of Use - Restaurant: 248
- Fire Safety: 176

Open share among high-open categories:

- Property Maintenance-Int: 4,678 open / 44,370 closed, 9.5% open
- Vacant House: 3,882 open / 10,594 closed, 26.8% open
- Property Maintenance-Ext: 2,663 open / 23,582 closed, 10.1% open
- Rental Registry: 2,489 open / 14,054 closed, 15.0% open
- Certificate of Compliance: 2,344 open / 15,450 closed, 13.2% open

## Top open violation labels

- SPCC-Sec. 27-133 Registration: 1,529
- SPCC - Section 27-72 (f) - Overgrowth: 826
- 2020 PMCNYS - Section 305.3 - interior surfaces: 740
- SPCC - Section 27-116 (E) - Vacant Property Registry: 689
- SPCC - Section 27-15 (b) Multiple dwelling: 679
- SPCC - Section 27-72 (e) -Trash & Debris: 655
- 2020 PMCNYS - Section 304.13 - Window, skylight, and door frames: 550
- SGOC - Section 54-5(A) - Lead Abatement and Control Deteriorated Paint Violation - Exterior Residential: 487
- SPCC 27-43 (e) (1)(2)(3)(4) Certification: 433
- SPCC SEC. 27-15: 405

## Neighborhood concentration

Top neighborhoods by open violation rows:

- Northside: 3,053
- Near Westside: 1,376
- Brighton: 1,352
- Washington Square: 1,105
- Eastwood: 874
- Southside: 767
- Park Ave: 739
- Elmwood: 705
- Southwest: 689
- Skunk City: 624

## Vacant-property signal

Open rows by `Vacant` field:

- blank/null: 12,665
- Residential: 4,985
- Commercial: 516

Vacant-related rows are a large part of the backlog, especially because vacant houses can remain in an open status for years and accumulate repeated/property-condition rows.

## Interpretation

The best interpretation is:

> “There are 18,166 open violation records in the Code Violations V2 layer, representing about 7,279 complaint/case numbers and about 5,246 parcels. The count is inflated relative to cases/properties because each complaint can contain multiple violation rows, some properties accumulate repeated complaints, vacant/registry/certificate workflows generate long-lived rows, and many older rows appear to remain open for years.”

## Exterior violation follow-up / reinspection signal

For `complaint_type_name = 'Property Maintenance-Ext'`, the layer has 26,245 violation rows:

- Closed: 23,582
- Open: 2,663

The dataset does **not** expose a reinspection history table, visit log, workflow events, or notes. It only exposes one `status_date` per violation row. So it cannot directly prove that an inspector physically went back to the property.

However, closed exterior violations do show a strong indirect follow-up signal:

- 16,205 of 23,582 closed exterior rows have `status_date` after `comply_by_date`.
- 3,936 closed exterior rows have `status_date` equal to `comply_by_date`.
- 3,441 closed exterior rows have `status_date` before `comply_by_date`.
- Median closed exterior row: `status_date` is 12 days after `comply_by_date`.
- Median closed exterior row: `status_date` is 23 days after `violation_date`.

Interpretation: for closed exterior rows, the status-change pattern is consistent with some kind of post-deadline review/reinspection/administrative follow-up. But the public layer does not identify whether that follow-up was a field revisit, staff review, phone/photo verification, contractor abatement update, or batch/administrative closure.

The open exterior rows tell a different story:

- 2,337 of 2,663 open exterior rows are already past their `comply_by_date` as of 2026-05-29.
- Of those past-due open exterior rows, only 22 have a `status_date` after `comply_by_date`.
- 44 have `status_date` equal to `comply_by_date`.
- 2,271 still have `status_date` before `comply_by_date`, often the original violation/opening date.

Interpretation: the public layer provides little evidence of post-deadline follow-up for most still-open exterior rows. That could mean no recheck has been recorded, the recheck is recorded in another internal table not published here, or the violation remains open even after some follow-up activity.

## Seasonal overgrowth closure signal

For rows whose `violation` text contains overgrowth/overgrown/lawn language, the layer has 15,942 rows:

- Closed: 15,105 (94.7%)
- Open: 837 (5.3%)

This category behaves differently from the broad open-violation backlog. Most overgrowth/lawn rows eventually get closed, and older seasons have very high closure rates:

- 2017: 561 closed / 7 open, 98.8% closed
- 2018: 680 closed / 7 open, 99.0% closed
- 2019: 935 closed / 5 open, 99.5% closed
- 2020: 1,402 closed / 15 open, 98.9% closed
- 2021: 2,289 closed / 33 open, 98.6% closed
- 2022: 2,249 closed / 23 open, 99.0% closed
- 2023: 1,983 closed / 42 open, 97.9% closed
- 2024: 1,902 closed / 63 open, 96.8% closed
- 2025: 2,564 closed / 133 open, 95.1% closed
- 2026: 540 closed / 509 open, 51.5% closed as of 2026-05-29

Closed overgrowth/lawn rows are usually closed quickly:

- Median `status_date - violation_date`: 12 days
- Median `status_date - comply_by_date`: 3 days
- 90th percentile `status_date - violation_date`: 189 days

Interpretation: overgrowth appears to be a seasonal/high-turnover violation type. Most rows close, presumably because the property is brought into compliance, the City cuts/abates it, winter makes the condition moot, or staff administratively closes the seasonal complaint.

But the open remnants are still worth caveating:

- 837 overgrowth/lawn rows remain open.
- 595 of those are already past their `comply_by_date`.
- 328 open overgrowth/lawn rows are from pre-2026 violation years.
- There are still a handful of open overgrowth rows dating back to 2017–2020, which are likely stale records or unresolved property workflows rather than literal grass that remained continuously overgrown for years.

A good public-facing interpretation is: overgrowth complaints mostly do close, but the remaining open overgrowth records should not be read literally as current standing grass conditions, especially for older years. For current-season monitoring, filter to recent `violation_date`/`status_date` and treat old open overgrowth rows as probable backlog/stale-status artifacts unless independently verified.

## Past-due open rows and more-recent status dates

Across all open violation rows:

- Total open rows: 18,166
- Past `comply_by_date`: 17,200 (94.7% of open rows)
- Future/not-yet-due: 957
- Missing/placeholder comply date: 9

For those 17,200 past-due open rows, `status_date` is usually **not** more recent than `comply_by_date`:

- `status_date` after `comply_by_date`: 263 (1.5%)
- `status_date` equal to `comply_by_date`: 330 (1.9%)
- `status_date` before `comply_by_date`: 16,607 (96.6%)

Interpretation: most past-due open rows do not show a public status update after the compliance deadline. Where `status_date` is newer than the compliance deadline, that is an indirect signal that the row was touched after it became past-due, but it is not proof of field reinspection.

Past-due open rows by complaint type:

| Complaint type | Past-due open rows | Status after comply | Status same/after comply | Status before comply |
|---|---:|---:|---:|---:|
| Property Maintenance-Int | 4,493 | 59 (1.3%) | 110 (2.4%) | 4,383 (97.6%) |
| Vacant House | 3,837 | 91 (2.4%) | 125 (3.3%) | 3,712 (96.7%) |
| Rental Registry | 2,393 | 26 (1.1%) | 57 (2.4%) | 2,336 (97.6%) |
| Property Maintenance-Ext | 2,337 | 22 (0.9%) | 66 (2.8%) | 2,271 (97.2%) |
| Certificate of Compliance | 2,145 | 18 (0.8%) | 54 (2.5%) | 2,091 (97.5%) |
| Smoke Alarm Certification | 330 | 3 (0.9%) | 4 (1.2%) | 326 (98.8%) |
| Sprinkler System | 268 | 11 (4.1%) | 29 (10.8%) | 239 (89.2%) |
| Cert of Use - Restaurant | 241 | 2 (0.8%) | 9 (3.7%) | 232 (96.3%) |
| Cert of Use - Food Store | 240 | 11 (4.6%) | 14 (5.8%) | 226 (94.2%) |
| Fire Safety | 166 | 13 (7.8%) | 59 (35.5%) | 107 (64.5%) |

The categories with the most visible post-deadline status activity are fire/safety/certification-related workflows, especially Fire Safety, Sprinkler System, and Cert of Use - Food Store. The highest-volume property-maintenance and registry categories have very low shares of post-deadline status updates.

Top past-due open violation labels include:

- SPCC-Sec. 27-133 Registration: 1,486 rows; 20 status-after-comply rows
- Interior surfaces: 738 rows; 7 status-after-comply rows
- Vacant Property Registry: 676 rows; 23 status-after-comply rows
- Multiple dwelling: 624 rows; 7 status-after-comply rows
- Trash & Debris: 610 rows; 8 status-after-comply rows
- Overgrowth: 584 rows; 8 status-after-comply rows
- Window/skylight/door frames: 547 rows; 11 status-after-comply rows
- Exterior residential deteriorated paint/lead: 469 rows; 7 status-after-comply rows

Good public-facing interpretation: the public layer shows many open rows past their compliance deadline, but very few have a status date later than that deadline. This suggests either limited visible follow-up in the public layer, follow-up recorded in unpublished internal tables, or open records whose status is not consistently refreshed after compliance deadlines pass.

## Recommended caveats for DataCuse use

- Do not call the open count “open cases” unless deduplicated by complaint number.
- Do not call the open count “properties with violations” unless deduplicated by SBL or address.
- Use three separate measures:
  - Open violation rows
  - Open complaints/cases
  - Parcels with open violation rows
- For public-facing analysis, add an “open status may include long-running or stale administrative records” caveat.
- Consider an “active recent open” measure, e.g. open rows with `status_date` or `violation_date` in the last 12–24 months.
- Separate administrative/registry/certificate violations from physical property-condition violations.
- For exterior violations, treat `status_date` as an indirect follow-up signal, not proof of a physical reinspection. Closed rows often have post-deadline status dates; still-open rows usually do not.
