# Worked example: two fictional manufacturers

This walks through the scoring of the fictional group used across the toolkit examples: a UK entity on ERP A and a German entity on ERP B, both making cast and sealing components to order. Everything here is invented. The input is [examples/two-manufacturers.csv](examples/two-manufacturers.csv) and the full report is [../examples/reports/decision/two-manufacturers.decision-report.md](../examples/reports/decision/two-manufacturers.decision-report.md).

## The question

The group finance director asks whether to move both entities to a single platform. ERP A support ends in nine months. ERP B has a contract with 30 months left and a termination fee.

## The scores in short

| Criterion | Score | Why |
|---|---:|---|
| C01 Process similarity | 4 | Similar routings and make-to-order flow. Quoting differs (per tonne against per unit) |
| C02 Commercial case | 3 | Saving on licences and a finance post is estimated, but one-off cost is not yet costed. Payback range is two to five years |
| C03 Shared customers, suppliers and parts | 3 | The duplicate analysis found nine customer groups with records in both systems |
| C04 Group reporting and control pain | 4 | Nine working days to consolidate, in spreadsheets, with an audit point on intercompany |
| C05 Contract and licence timing | 2 | One system's support ends soon, the other has 30 months and a fee: no common window |
| C06 Strategic stability | 4 | No disposals planned |
| C07 Customisation depth | 2 | About forty bespoke reports and four custom interfaces in ERP B, partly documented |
| C08 Regulatory and statutory differences | 2 | UK and German statutory and e-invoicing requirements to be confirmed against the target |
| C09 Currency and legal entity complexity | 2 | GBP and EUR, different year ends, regular intercompany |
| C10 Change capacity | 2 | Finance is stretched by the audit cycle and a treasury project |
| C11 Data quality and master data readiness | 2 | The readiness scorecard is NO-GO |
| C12 Sponsor and governance strength | 3 | Finance director sponsors, but the German managing director has not agreed the scope |
| C13 Integration footprint | 3 | Twelve integrations, eight documented |
| G04 Target platform unproven | yes | No pilot of the costing process |

The other gates (G01 to G03) are answered no.

## The result

- Case for consolidation: **57.7** out of 100.
- Ability to deliver: **29.7** out of 100.
- Outcome: **partially integrate**.

The case is a genuine one, on reporting pain, shared master data and similar processes. It is not strong enough to clear 65, mostly because the commercial case is not yet costed and contract timing does not line up. The ability to deliver is far below 60: customisation, regulatory differences, currency, change capacity and data quality all scored 2. Gate G04 (the target is unproven for the costing process) would also cap the outcome at partial integration even if the scores were higher.

No single criterion changed by one point alters the outcome. That is informative: the answer is not fragile, and the gap to a consolidation decision is large and spread across many criteria, not a single missing point.

## What partial integration could mean here

The framework does not prescribe the partial option. For this group, a sensible reading is:

1. Agree a group chart of accounts and map both entities to it. The toolkit's `map-coa` and `reconcile` commands do this work. In the example, ERP B has 50 percent of its accounts mapped and a reconciliation that fails in all three periods, so there is plenty to do.
2. Build a monthly group reporting layer from the mapped trial balances. This addresses C04 directly and does not depend on the migration.
3. Clean and match customer and supplier master data across both systems. The example finds 16 proposed customer merge groups, of which 9 span both systems. This is useful whatever happens next.
4. Decide what to do about ERP A's support end date as a separate, smaller decision: extend, upgrade or move that entity first.
5. Pilot the target platform's costing process with one entity, to close G04.
6. Score again at the next stage gate.

## What would change the outcome

A what-if run with the same tool shows how far the group is from consolidation. The scores for customisation depth, regulatory differences and change capacity were raised from 2 to 4, data quality from 2 to 4 and currency complexity from 2 to 3, the commercial case from 3 to 4 once costed and validated, and G04 was answered no after a successful pilot. The result was case 63.5 and ability 67.2, still partial integration because the case is just below 65. The sensitivity list then showed that a further point on several case criteria (for example C01, C02, C04 or C05) would give consolidate.

The reading is that improving ability to deliver is necessary but not enough. A stronger, evidenced commercial case and a closer match of contract timing are also needed. This is a prompt for the group to decide which of those it can actually change, not a forecast.

To reproduce the what-if, copy the scores file, change the values named above, and run `decide` on the copy.

## The other two examples

- [two-uk-distributors.csv](examples/two-uk-distributors.csv): same country, same products, shared customers, validated case and funded capacity. Result: consolidate (case 80.8, ability 76.6). This is the situation the framework should say yes to.
- [different-regulated-businesses.csv](examples/different-regulated-businesses.csv): a manufacturer and a regulated service business with no shared customers, a regulator-required system and an unproven target. Result: keep separate (case 17.3, ability 34.4), with gates G01 and G04 answered yes. This is the case for which consolidating would be the costly mistake.

## Notes on using the framework

- Writing the evidence for each score exposes where the group is guessing. If the evidence column is hard to fill, that is a finding.
- The toolkit's data evidence (the readiness scorecard, the duplicate analysis, the mapping coverage) informs C03 and C11. The other criteria need people.
- A common outcome for groups in this position is neither consolidate nor keep separate, but a staged path.
