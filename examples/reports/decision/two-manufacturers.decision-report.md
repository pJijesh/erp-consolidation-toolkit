# Consolidation decision: two-manufacturers

**Outcome: PARTIALLY INTEGRATE**

- Case for consolidation: 57.7 out of 100 (consolidate needs 65 or more)
- Ability to deliver: 29.7 out of 100 (consolidate needs 60 or more)
- Case 57.7 is between 40 and 65: some shared benefit, not enough to justify a full migration.
- Gate(s) answered yes, which would cap the outcome at partial integration: G04.

This is a structured prompt for a decision meeting. The scores are only as good as the evidence behind them, and a different panel could score differently.

## Case for consolidation

| Id | Criterion | Weight | Score | Evidence |
|---|---|---:|---:|---|
| C01 | Process similarity | 3 | 4 | Both make cast and sealing components to order, with similar routings. Quoting differs: ERP A prices per tonne, ERP B per unit. |
| C02 | Commercial case | 3 | 3 | Finance estimates a saving on licences and one finance post, but one-off cost is not yet costed. Payback range is two to five years. |
| C03 | Shared customers, suppliers and parts | 2 | 3 | Nine proposed customer merge groups include records from both systems (see examples/reports/dedupe/customers.dedupe-report.md). |
| C04 | Group reporting and control pain | 2 | 4 | Month end consolidation takes nine working days and relies on spreadsheets. One audit point on intercompany balances last year. |
| C05 | Contract and licence timing | 2 | 2 | ERP A support ends in nine months. ERP B has a contract with 30 months left and a termination fee. |
| C06 | Strategic stability | 1 | 4 | No disposals planned. Both entities are expected to stay in the group. |

## Ability to deliver

| Id | Criterion | Weight | Score | Evidence |
|---|---|---:|---:|---|
| C07 | Customisation depth | 3 | 2 | ERP B has about forty bespoke reports and four custom interfaces, only partly documented. |
| C08 | Regulatory and statutory differences | 3 | 2 | UK and German entities. Local statutory reporting and German e-invoicing rules need to be confirmed against the target. |
| C09 | Currency and legal entity complexity | 2 | 2 | GBP and EUR, different year ends, regular intercompany trading. |
| C10 | Change capacity | 3 | 2 | Finance is stretched by the audit cycle and a separate treasury project runs to the end of the year. |
| C11 | Data quality and master data readiness | 2 | 2 | Readiness scorecard is NO-GO: duplicate keys, mapping coverage of 50 percent for ERP B. |
| C12 | Sponsor and governance strength | 2 | 3 | Group finance director sponsors it, but the German managing director has not yet agreed to the scope. |
| C13 | Integration and interface footprint | 1 | 3 | Twelve integrations in total, eight documented. |

## Gates

| Id | Gate | Answer | Evidence |
|---|---|---|---|
| G01 | Local system or statutory books required | no | Statutory books can be produced in the target, subject to confirmation (see C08). |
| G02 | No accountable executive sponsor | no | Group finance director is accountable for both entities. |
| G03 | Sale or restructure expected | no | No sale or restructure planned. |
| G04 | Target platform unproven | yes | The target platform has not yet been piloted with either entity's costing process. |

## Weakest criteria (scored 1 or 2)

- C07 Customisation depth (ability): 2
- C08 Regulatory and statutory differences (ability): 2
- C10 Change capacity (ability): 2
- C05 Contract and licence timing (case): 2
- C09 Currency and legal entity complexity (ability): 2
- C11 Data quality and master data readiness (ability): 2

## Sensitivity: one point can change the outcome

No single criterion moved by one point changes the outcome.
