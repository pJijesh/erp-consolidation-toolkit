# Trial balance reconciliation: erp_a

- Periods: 3; clean: 0; with differences: 3
- Tolerance: 0.05 (absolute, per account and per class)
- Source accounts with a balance but no approved mapping: 0
- Largest absolute difference found: 328056.09
- Loaded target trial balance compared: 2 account and period difference(s) beyond tolerance
- Warning: 3 unmapped or unapproved row(s) in erp_a.mapping.csv were not used.

Amounts are debit positive and credit negative, in the currency of the trial balance. No currency translation is done.

## By period

| Period | Source debit | Source credit | Source net | Mapped net | Unmapped net | Unmapped accounts | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-01 | 14792015.14 | 14792015.14 | 0.00 | 0.00 | 0.00 | 0 | DIFFERENCES |
| 2026-02 | 16672945.18 | 16672945.18 | 0.00 | 0.00 | 0.00 | 0 | DIFFERENCES |
| 2026-03 | 19057370.40 | 19057370.40 | 0.00 | 0.00 | 0.00 | 0 | DIFFERENCES |

## Balances by account class, latest period (2026-03)

| Class | Before (source type) | Unmapped | After (target type) | Reclassified |
|---|---:|---:|---:|---:|
| asset | 10139606.52 | 0.00 | 10337456.22 | 197849.70 |
| liability | -4566453.47 | 0.00 | -4653025.60 | -86572.13 |
| equity | -7139721.35 | 0.00 | -7139721.35 | 0.00 |
| revenue | -4252388.43 | 0.00 | -4252388.43 | 0.00 |
| expense | 5830061.25 | 0.00 | 5707679.16 | -122382.09 |
| unclassified | -11104.52 | 0.00 | 0.00 | 11104.52 |

Reclassified is the movement between classes that the mapping itself causes, separate from balances left out because they are unmapped.

## Differences beyond tolerance (14)

| Type | Period | Account or class | Expected or before | Actual or after | Difference | Note |
|---|---|---|---:|---:|---:|---|
| reclassification | 2026-01 | asset | 9796232.54 | 9865211.06 | 68978.52 | balances moved between classes because source and target account types differ |
| reclassification | 2026-01 | liability | -4500107.10 | -4589328.61 | -89221.51 | balances moved between classes because source and target account types differ |
| reclassification | 2026-01 | expense | 1932830.13 | 1888429.27 | -44400.86 | balances moved between classes because source and target account types differ |
| reclassification | 2026-01 | unclassified | -64643.85 | 0.00 | 64643.85 | balances moved between classes because source and target account types differ |
| reclassification | 2026-02 | asset | 9772218.05 | 9905597.82 | 133379.77 | balances moved between classes because source and target account types differ |
| reclassification | 2026-02 | liability | -4541147.12 | -4637888.28 | -96741.16 | balances moved between classes because source and target account types differ |
| reclassification | 2026-02 | expense | 3861241.63 | 3778963.75 | -82277.88 | balances moved between classes because source and target account types differ |
| reclassification | 2026-02 | unclassified | -45639.27 | 0.00 | 45639.27 | balances moved between classes because source and target account types differ |
| target_tb_difference | 2026-02 | 12050 | 1911487.08 | 1912737.08 | 1250.00 | Trade receivables: loaded balance differs from the mapped source |
| reclassification | 2026-03 | asset | 10139606.52 | 10337456.22 | 197849.70 | balances moved between classes because source and target account types differ |
| reclassification | 2026-03 | liability | -4566453.47 | -4653025.60 | -86572.13 | balances moved between classes because source and target account types differ |
| reclassification | 2026-03 | expense | 5830061.25 | 5707679.16 | -122382.09 | balances moved between classes because source and target account types differ |
| reclassification | 2026-03 | unclassified | -11104.52 | 0.00 | 11104.52 | balances moved between classes because source and target account types differ |
| target_tb_difference | 2026-03 | 61120 | 328056.09 | 0.00 | -328056.09 | Telephone and internet: loaded balance differs from the mapped source |
