# Readiness thresholds

The `readiness` command combines the JSON summaries written by `profile`, `map-coa`, `dedupe` and (optionally) `reconcile` into one scorecard. This page lists every measure, its limits and the reasoning.

The limits are judgement-based starting points. They are not industry standards and no standard body publishes them. Each group should set its own limits before the first assessment, record why, and not change them after seeing the results. Override them with a JSON file (`--thresholds`).

## Verdict rule

| Verdict | Rule |
|---|---|
| NO-GO | Any red check, or any required evidence missing (no profile, no mapping summary or no duplicate analysis supplied) |
| CONDITIONAL GO | No red checks, at least one amber. Each amber check is a condition to close before cutover |
| GO | All checks green |

Missing evidence gives NO-GO on purpose: an absent measurement is not a pass. Measures that cannot be calculated from the files supplied (for example no key column was named in a profile) are listed under "Not assessed" and do not change the verdict, so read that list.

A GO verdict means the data checks passed. It does not mean the programme is ready. Training, interfaces, contracts, support, people and many other things are outside the tool.

## Measures

Direction "lower" means the value should be no greater than the limit. "Higher" means no less.

| Measure | Direction | Green | Amber | Why |
|---|---|---:|---:|---|
| Highest missing rate among required columns | lower | 2% | 5% | A required field that is blank for more than a few percent of rows will need a rule or a decision at load |
| Share of rows whose key value appears more than once | lower | 0% | 0.5% | A key that should be unique and is not breaks loads and merges. A small tolerance for known cases is allowed for amber |
| Share of checked values that fail a format check | lower | 1% | 5% | Format failures mean cleansing work or load rejects. Note that format checks test shape, not truth: a well-formed tax number may still be wrong |
| Share of source accounts with an approved mapping | higher | 98% | 90% | Unmapped accounts with no balance may be retired. The next measure covers accounts that matter |
| Accounts carrying a balance without an approved mapping | lower | 0 | 0 | There is no amber: an unmapped balance cannot be loaded or reported |
| Mapping exceptions at error severity | lower | 0 | 0 | Errors are conflicts, unknown targets and unmapped accounts with balances. No amber |
| Share of one system's records that would be merged into another record of the same system | lower | 1% | 3% | Within-system duplicates are the clearest sign of weak master data control |
| Pairs needing human review per 100 records | lower | 3 | 8 | A workload measure. Each review takes a person's time. Set the limit from the capacity of the data council |
| Periods where the mapped trial balance differs beyond tolerance | lower | 0 | 0 | No amber: a reconciliation either holds or it does not. Tolerance is set in `reconcile` |

## Reading the example scorecard

The committed scorecard for the fictional group ([examples/reports/readiness/group-readiness-report.md](../examples/reports/readiness/group-readiness-report.md)) is NO-GO: 20 red, 8 amber, 6 green. That is the intended result for a first pass over messy data. The ways it improves are the ways a real programme does: approve more mappings, resolve duplicate keys at source, merge duplicates, and rerun.

Two points in the example are worth noting:

- The mapped trial balances differ in all three periods for both entities. For ERP A, the differences come from the mapping moving balances between account classes and from two loaded balances that differ from the mapped source. For ERP B, they come mostly from 55 accounts with balances and no approved mapping.
- The review workload is above the amber limit for all three record types, mostly because the example data is dense with deliberate near duplicates.

## Changing the thresholds

A thresholds file lists only the measures to change:

```json
{
  "dedupe.review_pairs_per_100_records": {"green": 5, "amber": 12},
  "coa.approved_coverage": {"green": 0.99, "amber": 0.95}
}
```

The tool checks the file: unknown measure names are rejected, both limits are required, and green must be at least as strict as amber. Record any change and the reason with the assessment, so that readers know the scorecard was not tuned to pass.
