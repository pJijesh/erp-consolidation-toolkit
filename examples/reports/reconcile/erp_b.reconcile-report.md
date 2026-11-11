# Trial balance reconciliation: erp_b

- Periods: 3; clean: 0; with differences: 3
- Tolerance: 0.01 (absolute, per account and per class)
- Source accounts with a balance but no approved mapping: 55
- Largest absolute difference found: 1875766.58
- Warning: 55 unmapped or unapproved row(s) in erp_b.mapping.csv were not used.

Amounts are debit positive and credit negative, in the currency of the trial balance. No currency translation is done.

## By period

| Period | Source debit | Source credit | Source net | Mapped net | Unmapped net | Unmapped accounts | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-01 | 10602771.46 | 10602771.46 | 0.00 | -76227.54 | 76227.54 | 55 | DIFFERENCES |
| 2026-02 | 13195313.79 | 13195313.79 | 0.00 | -503036.27 | 503036.27 | 55 | DIFFERENCES |
| 2026-03 | 15685259.48 | 15685259.48 | 0.00 | -585536.22 | 585536.22 | 55 | DIFFERENCES |

## Balances by account class, latest period (2026-03)

| Class | Before (source type) | Unmapped | After (target type) | Reclassified |
|---|---:|---:|---:|---:|
| asset | 5235029.47 | 2623627.07 | 2611402.40 | 0.00 |
| liability | -4377427.46 | -2568666.27 | -1808761.19 | 0.00 |
| equity | -4797046.53 | -183861.46 | -4613185.07 | 0.00 |
| revenue | -3429118.97 | -1945035.24 | -1484083.73 | 0.00 |
| expense | 7361093.67 | 2723032.54 | 4709091.37 | 71030.24 |
| unclassified | 7469.82 | -63560.42 | 0.00 | -71030.24 |

Reclassified is the movement between classes that the mapping itself causes, separate from balances left out because they are unmapped.

## Differences beyond tolerance (171)

| Type | Period | Account or class | Expected or before | Actual or after | Difference | Note |
|---|---|---|---:|---:|---:|---|
| unmapped_balance | 2026-01 | 100400 | 1781096.64 | 0.00 | -1781096.64 | Vehicles cost: balance has no approved mapping |
| unmapped_balance | 2026-01 | 100700 | -824580.09 | 0.00 | 824580.09 | Office equipment accumulated depreciation: balance has no approved mapping |
| unmapped_balance | 2026-01 | 100800 | 531597.37 | 0.00 | -531597.37 | IT hardware cost: balance has no approved mapping |
| unmapped_balance | 2026-01 | 100900 | -600500.51 | 0.00 | 600500.51 | IT hardware accumulated depreciation: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200100 | 542081.50 | 0.00 | -542081.50 | Inventory raw materials: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200200 | 458403.55 | 0.00 | -458403.55 | Inventory work in progress: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200300 | 379016.37 | 0.00 | -379016.37 | Inventory finished goods: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200400 | -487443.12 | 0.00 | 487443.12 | Inventory write-down reserve: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200510 | 541241.64 | 0.00 | -541241.64 | Trade receivables EU: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200600 | -117742.55 | 0.00 | 117742.55 | Bad debt allowance: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200800 | 94419.89 | 0.00 | -94419.89 | Prepaid expenses: balance has no approved mapping |
| unmapped_balance | 2026-01 | 200900 | 9631.43 | 0.00 | -9631.43 | Accrued income: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201000 | 51281.25 | 0.00 | -51281.25 | Input tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201200 | 67762.86 | 0.00 | -67762.86 | Bank USD account: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201300 | 1414.71 | 0.00 | -1414.71 | Cash on hand: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201400 | 83040.83 | 0.00 | -83040.83 | Receivables from affiliated companies: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201500 | 46204.55 | 0.00 | -46204.55 | Security deposits paid: balance has no approved mapping |
| unmapped_balance | 2026-01 | 201600 | 64181.00 | 0.00 | -64181.00 | Emissions certificates: balance has no approved mapping |
| unmapped_balance | 2026-01 | 300100 | -185127.11 | 0.00 | 185127.11 | Subscribed capital: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400100 | -120127.22 | 0.00 | 120127.22 | Trade payables domestic: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400400 | -69083.27 | 0.00 | 69083.27 | Output tax 19 percent: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400610 | -105246.20 | 0.00 | 105246.20 | Social security payable: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400700 | -181123.77 | 0.00 | 181123.77 | Pension fund payable: balance has no approved mapping |
| unmapped_balance | 2026-01 | 400800 | -125688.05 | 0.00 | 125688.05 | Corporate income tax payable: balance has no approved mapping |
| unmapped_balance | 2026-01 | 401000 | -253919.36 | 0.00 | 253919.36 | Finance lease liabilities current: balance has no approved mapping |
| unmapped_balance | 2026-01 | 401400 | -91359.31 | 0.00 | 91359.31 | Warranty provision: balance has no approved mapping |
| unmapped_balance | 2026-01 | 450100 | -533892.85 | 0.00 | 533892.85 | Long-term loans: balance has no approved mapping |
| unmapped_balance | 2026-01 | 450200 | -1095705.78 | 0.00 | 1095705.78 | Finance lease liabilities non-current: balance has no approved mapping |
| unmapped_balance | 2026-01 | 500100 | -612802.99 | 0.00 | 612802.99 | Revenue domestic: balance has no approved mapping |
| unmapped_balance | 2026-01 | 500700 | -33251.64 | 0.00 | 33251.64 | Other operating income: balance has no approved mapping |
| unmapped_balance | 2026-01 | 500800 | -28532.46 | 0.00 | 28532.46 | Proceeds from scrap: balance has no approved mapping |
| unmapped_balance | 2026-01 | 600200 | 177360.86 | 0.00 | -177360.86 | Production wages: balance has no approved mapping |
| unmapped_balance | 2026-01 | 600600 | 45602.22 | 0.00 | -45602.22 | Energy production: balance has no approved mapping |
| unmapped_balance | 2026-01 | 600700 | 41652.45 | 0.00 | -41652.45 | Tools expensed: balance has no approved mapping |
| unmapped_balance | 2026-01 | 601000 | 56750.38 | 0.00 | -56750.38 | Scrap and rework costs: balance has no approved mapping |
| unmapped_balance | 2026-01 | 601100 | 30817.77 | 0.00 | -30817.77 | Inventory write-offs: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700200 | 28643.87 | 0.00 | -28643.87 | Salaries administration: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700300 | 57860.65 | 0.00 | -57860.65 | Employer social security: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700500 | 42976.63 | 0.00 | -42976.63 | Rent: balance has no approved mapping |
| unmapped_balance | 2026-01 | 700800 | 66495.47 | 0.00 | -66495.47 | Maintenance machinery: balance has no approved mapping |

The first 40 are shown. The full list is in the differences CSV.
