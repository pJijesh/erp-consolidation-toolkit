# Readiness scorecard

**Verdict: NO-GO**

- Red: 20; amber: 8; green: 6

Rule: any red check, or missing evidence, gives NO-GO. Otherwise any amber check gives CONDITIONAL GO, and each amber check is a condition to close before cutover. Otherwise GO. The scorecard reports on the files supplied only. It is an input to a human decision, not the decision.

## Checks

| Status | Area | Subject | Measure | Value | Green | Amber |
|---|---|---|---|---:|---:|---:|
| RED | Chart of accounts | erp_b | Share of source accounts with an approved mapping | 50.0% | at least 98.0% | at least 90.0% |
| RED | Chart of accounts | erp_b | Accounts carrying a balance without an approved mapping | 55 | at most 0 | at most 0 |
| RED | Chart of accounts | erp_b | Mapping exceptions at error severity | 21 | at most 0 | at most 0 |
| RED | Data quality | erp_a_customers | Share of rows whose key value appears more than once | 7.7% | at most 0.0% | at most 0.5% |
| RED | Data quality | erp_a_parts | Share of checked values that fail a format check | 5.6% | at most 1.0% | at most 5.0% |
| RED | Data quality | erp_a_suppliers | Share of rows whose key value appears more than once | 11.1% | at most 0.0% | at most 0.5% |
| RED | Data quality | erp_b_customers | Share of checked values that fail a format check | 6.5% | at most 1.0% | at most 5.0% |
| RED | Data quality | erp_b_customers | Share of rows whose key value appears more than once | 9.5% | at most 0.0% | at most 0.5% |
| RED | Data quality | erp_b_suppliers | Share of rows whose key value appears more than once | 14.3% | at most 0.0% | at most 0.5% |
| RED | Duplicates | customers | Pairs needing human review per 100 records (workload) | 10.64 | at most 3 | at most 8 |
| RED | Duplicates | customers, ERP A | Share of one system's records that would be merged into another record of the same system | 7.7% | at most 1.0% | at most 3.0% |
| RED | Duplicates | customers, ERP B | Share of one system's records that would be merged into another record of the same system | 7.1% | at most 1.0% | at most 3.0% |
| RED | Duplicates | parts | Pairs needing human review per 100 records (workload) | 9.43 | at most 3 | at most 8 |
| RED | Duplicates | parts, ERP A | Share of one system's records that would be merged into another record of the same system | 5.6% | at most 1.0% | at most 3.0% |
| RED | Duplicates | parts, ERP B | Share of one system's records that would be merged into another record of the same system | 3.9% | at most 1.0% | at most 3.0% |
| RED | Duplicates | suppliers | Pairs needing human review per 100 records (workload) | 10.94 | at most 3 | at most 8 |
| RED | Duplicates | suppliers, ERP A | Share of one system's records that would be merged into another record of the same system | 8.3% | at most 1.0% | at most 3.0% |
| RED | Duplicates | suppliers, ERP B | Share of one system's records that would be merged into another record of the same system | 7.1% | at most 1.0% | at most 3.0% |
| RED | Reconciliation | erp_a | Periods where the mapped trial balance differs beyond tolerance | 3 | at most 0 | at most 0 |
| RED | Reconciliation | erp_b | Periods where the mapped trial balance differs beyond tolerance | 3 | at most 0 | at most 0 |
| AMBER | Chart of accounts | erp_a | Share of source accounts with an approved mapping | 96.3% | at least 98.0% | at least 90.0% |
| AMBER | Data quality | erp_a_customers | Share of checked values that fail a format check | 1.6% | at most 1.0% | at most 5.0% |
| AMBER | Data quality | erp_a_customers | Highest missing rate among required columns | 3.9% | at most 2.0% | at most 5.0% |
| AMBER | Data quality | erp_a_suppliers | Share of checked values that fail a format check | 2.2% | at most 1.0% | at most 5.0% |
| AMBER | Data quality | erp_a_suppliers | Highest missing rate among required columns | 2.8% | at most 2.0% | at most 5.0% |
| AMBER | Data quality | erp_b_customers | Highest missing rate among required columns | 2.4% | at most 2.0% | at most 5.0% |
| AMBER | Data quality | erp_b_suppliers | Share of checked values that fail a format check | 4.1% | at most 1.0% | at most 5.0% |
| AMBER | Data quality | erp_b_suppliers | Highest missing rate among required columns | 3.6% | at most 2.0% | at most 5.0% |
| GREEN | Chart of accounts | erp_a | Accounts carrying a balance without an approved mapping | 0 | at most 0 | at most 0 |
| GREEN | Chart of accounts | erp_a | Mapping exceptions at error severity | 0 | at most 0 | at most 0 |
| GREEN | Data quality | erp_a_parts | Share of rows whose key value appears more than once | 0.0% | at most 0.0% | at most 0.5% |
| GREEN | Data quality | erp_a_parts | Highest missing rate among required columns | 0.0% | at most 2.0% | at most 5.0% |
| GREEN | Data quality | erp_b_parts | Share of rows whose key value appears more than once | 0.0% | at most 0.0% | at most 0.5% |
| GREEN | Data quality | erp_b_parts | Highest missing rate among required columns | 0.0% | at most 2.0% | at most 5.0% |

## Not assessed

These measures were not available in the files supplied, for example because no key column was given:

- erp_b_parts: Share of checked values that fail a format check
