# Trial balance reconciliation: erp_b_preview

- Periods: 3; clean: 0; with differences: 3
- Tolerance: 0.01 (absolute, per account and per class)
- Source accounts with a balance but no approved mapping: 21
- Largest absolute difference found: 531597.37
- Warning: 21 unmapped or unapproved row(s) in erp_b.mapping.csv were not used.

Amounts are debit positive and credit negative, in the currency of the trial balance. No currency translation is done.

## By period

| Period | Source debit | Source credit | Source net | Mapped net | Unmapped net | Unmapped accounts | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-01 | 10602771.46 | 10602771.46 | 0.00 | -476391.45 | 476391.45 | 21 | DIFFERENCES |
| 2026-02 | 13195313.79 | 13195313.79 | 0.00 | -665083.98 | 665083.98 | 21 | DIFFERENCES |
| 2026-03 | 15685259.48 | 15685259.48 | 0.00 | -770361.66 | 770361.66 | 21 | DIFFERENCES |

## Balances by account class, latest period (2026-03)

| Class | Before (source type) | Unmapped | After (target type) | Reclassified |
|---|---:|---:|---:|---:|
| asset | 5235029.47 | 339657.14 | 4895372.33 | 0.00 |
| liability | -4377427.46 | -69165.33 | -4308262.13 | 0.00 |
| equity | -4797046.53 | 0.00 | -4797046.53 | 0.00 |
| revenue | -3429118.97 | -91461.02 | -3337657.95 | 0.00 |
| expense | 7361093.67 | 654891.29 | 6777232.62 | 71030.24 |
| unclassified | 7469.82 | -63560.42 | 0.00 | -71030.24 |

Reclassified is the movement between classes that the mapping itself causes, separate from balances left out because they are unmapped.

## Differences beyond tolerance (69)

| Type | Period | Account or class | Expected or before | Actual or after | Difference | Note |
|---|---|---|---:|---:|---:|---|
| unmapped_balance | 2026-01 | 100800 | 531597.37 | 0.00 | -531597.37 | IT hardware cost: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200400 | -487443.12 | 0.00 | 487443.12 | Inventory write-down reserve: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200800 | 94419.89 | 0.00 | -94419.89 | Prepaid expenses: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201000 | 51281.25 | 0.00 | -51281.25 | Input tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201200 | 67762.86 | 0.00 | -67762.86 | Bank USD account: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201300 | 1414.71 | 0.00 | -1414.71 | Cash on hand: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201500 | 46204.55 | 0.00 | -46204.55 | Security deposits paid: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201600 | 64181.00 | 0.00 | -64181.00 | Emissions certificates: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400400 | -69083.27 | 0.00 | 69083.27 | Output tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-01 | 500800 | -28532.46 | 0.00 | 28532.46 | Proceeds from scrap: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700200 | 28643.87 | 0.00 | -28643.87 | Salaries administration: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700800 | 66495.47 | 0.00 | -66495.47 | Maintenance machinery: balance has no approved mapping |
| unmapped_balance | 2026-01 | 701300 | 42388.25 | 0.00 | -42388.25 | IT services: balance has no approved mapping |
| unmapped_balance | 2026-01 | 701700 | 24996.20 | 0.00 | -24996.20 | Marketing: balance has no approved mapping |
| unmapped_balance | 2026-01 | 702210 | 28161.97 | 0.00 | -28161.97 | Amortisation software: balance has no approved mapping |
| unmapped_balance | 2026-01 | 702700 | 18716.70 | 0.00 | -18716.70 | Packaging disposal levy: balance has no approved mapping |
| unmapped_balance | 2026-01 | 702800 | 16085.31 | 0.00 | -16085.31 | Works council costs: balance has no approved mapping |
| unmapped_balance | 2026-01 | 900200 | 1834.97 | 0.00 | -1834.97 | Realised exchange losses: balance has no approved mapping |
| unmapped_balance | 2026-01 | 900300 | 1512.04 | 0.00 | -1512.04 | Income tax expense: balance has no approved mapping |
| unmapped_balance | 2026-01 | 910100 | -21008.70 | 0.00 | 21008.70 | Interest income: balance has no approved mapping |
| unmapped_balance | 2026-01 | 910200 | -3237.41 | 0.00 | 3237.41 | Realised exchange gains: balance has no approved mapping |
| reclassification | 2026-01 | expense | 2248200.67 | 2271710.12 | 23509.45 | balances moved between classes because source and target account types differ |
| reclassification | 2026-01 | unclassified | 23509.45 | 0.00 | -23509.45 | balances moved between classes because source and target account types differ |
| unmapped_balance | 2026-02 | 100800 | 530205.82 | 0.00 | -530205.82 | IT hardware cost: balance has no approved mapping |
| unmapped_balance | 2026-02 | 200400 | -465152.75 | 0.00 | 465152.75 | Inventory write-down reserve: balance has no approved mapping |
| unmapped_balance | 2026-02 | 200800 | 95299.72 | 0.00 | -95299.72 | Prepaid expenses: balance has no approved mapping |
| unmapped_balance | 2026-02 | 201000 | 52208.44 | 0.00 | -52208.44 | Input tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-02 | 201200 | 67671.16 | 0.00 | -67671.16 | Bank USD account: balance has no approved mapping |
| unmapped_balance | 2026-02 | 201300 | 1410.23 | 0.00 | -1410.23 | Cash on hand: balance has no approved mapping |
| unmapped_balance | 2026-02 | 201500 | 44614.03 | 0.00 | -44614.03 | Security deposits paid: balance has no approved mapping |
| unmapped_balance | 2026-02 | 201600 | 64665.55 | 0.00 | -64665.55 | Emissions certificates: balance has no approved mapping |
| unmapped_balance | 2026-02 | 400400 | -69923.63 | 0.00 | 69923.63 | Output tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-02 | 500800 | -58600.59 | 0.00 | 58600.59 | Proceeds from scrap: balance has no approved mapping |
| unmapped_balance | 2026-02 | 700200 | 56200.34 | 0.00 | -56200.34 | Salaries administration: balance has no approved mapping |
| unmapped_balance | 2026-02 | 700800 | 132432.80 | 0.00 | -132432.80 | Maintenance machinery: balance has no approved mapping |
| unmapped_balance | 2026-02 | 701300 | 84377.89 | 0.00 | -84377.89 | IT services: balance has no approved mapping |
| unmapped_balance | 2026-02 | 701700 | 50679.69 | 0.00 | -50679.69 | Marketing: balance has no approved mapping |
| unmapped_balance | 2026-02 | 702210 | 53735.80 | 0.00 | -53735.80 | Amortisation software: balance has no approved mapping |
| unmapped_balance | 2026-02 | 702700 | 36698.74 | 0.00 | -36698.74 | Packaging disposal levy: balance has no approved mapping |
| unmapped_balance | 2026-02 | 702800 | 30299.71 | 0.00 | -30299.71 | Works council costs: balance has no approved mapping |

The first 40 are shown. The full list is in the differences CSV.
