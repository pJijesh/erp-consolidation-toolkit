# Chart of accounts mapping: erp_b

- Source accounts: 110; target accounts: 110
- Approved (manual mapping file): 55 (50.0%)
- Suggested, waiting for review: 34 (19 at high confidence)
- Unmapped: 21
- Targets receiving more than one source account: 9
- Exceptions: 21 error, 18 warning
- Accounts with a balance in the trial balance: 110, of which not yet approved: 55

Suggestions are never approved by the tool. Review each one, then copy the accepted rows (source_account, target_account) into the manual mapping file and run again.

## Exceptions needing attention (39)

| Severity | Source account | Issue | Detail |
|---|---|---|---|
| error | 100800 | unmapped | no suggestion at or above 0.65. Closest was 12150 Rent and other deposits (0.51). The account carries a balance. |
| error | 200400 | unmapped | no suggestion at or above 0.65. Closest was 12020 Work in progress inventory (0.63). The account carries a balance. |
| error | 200800 | unmapped | no suggestion at or above 0.65. Closest was 12080 Prepayments (0.59). The account carries a balance. |
| error | 201000 | unmapped | no suggestion at or above 0.65. Closest was 12100 Input VAT recoverable (0.54). The account carries a balance. |
| error | 201200 | manual_target_unknown | manual mapping points to 12999, which is not in the target chart |
| error | 201300 | unmapped | no suggestion at or above 0.65. Closest was 12130 Petty cash (0.45). The account carries a balance. |
| error | 201500 | unmapped | no suggestion at or above 0.65. Closest was 12150 Rent and other deposits (0.54). The account carries a balance. |
| error | 201600 | unmapped | no suggestion at or above 0.65. Closest was 12140 Intercompany receivables (0.43). The account carries a balance. |
| error | 400400 | unmapped | no suggestion at or above 0.65. Closest was 21040 Output VAT (0.52). The account carries a balance. |
| error | 500800 | unmapped | no suggestion at or above 0.65. Closest was 41080 Scrap sales (0.56). The account carries a balance. |
| error | 700200 | unmapped | no suggestion at or above 0.65. Closest was 61020 Salaries (0.52). The account carries a balance. |
| error | 700800 | unmapped | no suggestion at or above 0.65. Closest was 61200 Depreciation, plant and machinery (0.57). The account carries a balance. |
| error | 701300 | unmapped | no suggestion at or above 0.65. Closest was 61070 Utilities, offices (0.50). The account carries a balance. |
| error | 701700 | unmapped | no suggestion at or above 0.65. Closest was 61170 Marketing and advertising (0.60). The account carries a balance. |
| error | 702210 | unmapped | no suggestion at or above 0.65. Closest was 61220 Depreciation, other (0.56). The account carries a balance. |
| error | 702700 | unmapped | no suggestion at or above 0.65. Closest was 61170 Marketing and advertising (0.41). The account carries a balance. |
| error | 702800 | unmapped | no suggestion at or above 0.65. Closest was 61240 Warranty costs (0.55). The account carries a balance. |
| error | 900200 | unmapped | no suggestion at or above 0.85. Closest was 71020 Exchange losses (0.77). The account carries a balance. |
| error | 900300 | unmapped | no suggestion at or above 0.85. Closest was 71030 Corporate income tax expense (0.78). The account carries a balance. |
| error | 910100 | unmapped | no suggestion at or above 0.85. Closest was 21120 Deferred income (0.67). The account carries a balance. |
| error | 910200 | unmapped | no suggestion at or above 0.85. Closest was 72020 Exchange gains (0.76). The account carries a balance. |
| warning | 100300 | many_to_one | 2 source accounts (100300, 100900) map to 11030 Plant and machinery accumulated depreciation: check that the suggestions are not all picking the same nearest name |
| warning | 100900 | ambiguous | 11030 Plant and machinery accumulated depreciation (0.76) and 11070 Fixtures and fittings accumulated depreciation (0.74) are almost equally close |
| warning | 200500 | many_to_one | 3 source accounts (200500, 200510, 200520) map to 12050 Trade receivables: check that the suggestions are not all picking the same nearest name |
| warning | 400100 | many_to_one | 2 source accounts (400100, 400110) map to 21010 Trade payables: check that the suggestions are not all picking the same nearest name |
| warning | 400600 | many_to_one | 2 source accounts (400600, 400610) map to 21060 Payroll taxes and social security payable: check that the suggestions are not all picking the same nearest name |
| warning | 600200 | ambiguous | 51050 Production consumables (0.74) and 51060 Production energy (0.73) are almost equally close |
| warning | 600200 | many_to_one | 2 source accounts (600200, 600500) map to 51050 Production consumables: check that the suggestions are not all picking the same nearest name |
| warning | 701000 | many_to_one | 2 source accounts (701000, 702600) map to 61100 Motor expenses: check that the suggestions are not all picking the same nearest name |
| warning | 702100 | many_to_one | 2 source accounts (702100, 702200) map to 61210 Depreciation, vehicles: check that the suggestions are not all picking the same nearest name |
| warning | 702400 | ambiguous | 61240 Warranty costs (0.67) and 61260 Sundry expenses (0.65) are almost equally close |
| warning | 900100 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 900200 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 900300 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 900310 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 900400 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 910100 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 910200 | type_unknown | source type 'Financial result' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 999999 | manual_source_unknown | manual mapping line 58 names a source account that is not in the source chart |

## Suggestions, lowest confidence first (34)

| Source | Source name | Suggested target | Target name | Confidence | Flags |
|---|---|---|---|---:|---|
| 200600 | Bad debt allowance | 12060 | Allowance for doubtful debts | 0.67 | low_confidence |
| 702400 | Warranty expense | 61240 | Warranty costs | 0.67 | ambiguous;low_confidence |
| 702200 | Depreciation office equipment | 61210 | Depreciation, vehicles | 0.68 | low_confidence;many_to_one |
| 702600 | Other operating expenses | 61100 | Motor expenses | 0.68 | low_confidence;many_to_one |
| 201400 | Receivables from affiliated companies | 12140 | Intercompany receivables | 0.69 | low_confidence |
| 300100 | Subscribed capital | 31010 | Share capital | 0.71 | low_confidence |
| 701310 | Software subscriptions | 61130 | IT costs and subscriptions | 0.73 | low_confidence |
| 100400 | Vehicles cost | 11040 | Motor vehicles at cost | 0.74 | low_confidence |
| 600200 | Production wages | 51050 | Production consumables | 0.74 | ambiguous;low_confidence;many_to_one |
| 100900 | IT hardware accumulated depreciation | 11030 | Plant and machinery accumulated depreciation | 0.76 | ambiguous;low_confidence;many_to_one |
| 400100 | Trade payables domestic | 21010 | Trade payables | 0.76 | low_confidence;many_to_one |
| 400610 | Social security payable | 21060 | Payroll taxes and social security payable | 0.77 | low_confidence;many_to_one |
| 500100 | Revenue domestic | 41010 | Revenue, castings domestic | 0.78 | low_confidence |
| 601000 | Scrap and rework costs | 51100 | Scrap and rework | 0.80 | low_confidence |
| 400700 | Pension fund payable | 21070 | Pensions payable | 0.83 | low_confidence |
| 600700 | Tools expensed | 51070 | Tooling expensed | 0.87 |  |
| 100700 | Office equipment accumulated depreciation | 11090 | Computer equipment accumulated depreciation | 0.88 |  |
| 200510 | Trade receivables EU | 12050 | Trade receivables | 0.92 | many_to_one |
| 200100 | Inventory raw materials | 12010 | Raw materials inventory | 1.00 |  |
| 200200 | Inventory work in progress | 12020 | Work in progress inventory | 1.00 |  |
| 200300 | Inventory finished goods | 12030 | Finished goods inventory | 1.00 |  |
| 200900 | Accrued income | 12090 | Accrued income | 1.00 |  |
| 400800 | Corporate income tax payable | 21080 | Corporate income tax payable | 1.00 |  |
| 401000 | Finance lease liabilities current | 21100 | Finance lease liabilities, current | 1.00 |  |
| 401400 | Warranty provision | 21140 | Warranty provision | 1.00 |  |
| 450100 | Long-term loans | 22010 | Long term loans | 1.00 |  |
| 450200 | Finance lease liabilities non-current | 22020 | Finance lease liabilities, non-current | 1.00 |  |
| 500700 | Other operating income | 41070 | Other operating income | 1.00 |  |
| 600600 | Energy production | 51060 | Production energy | 1.00 |  |
| 601100 | Inventory write-offs | 51110 | Inventory write-offs | 1.00 |  |
| 700300 | Employer social security | 61030 | Employer social security | 1.00 |  |
| 700500 | Rent | 61050 | Rent | 1.00 |  |
| 702100 | Depreciation vehicles | 61210 | Depreciation, vehicles | 1.00 | many_to_one |
| 702300 | Bad debt expense | 61230 | Bad debt expense | 1.00 |  |
