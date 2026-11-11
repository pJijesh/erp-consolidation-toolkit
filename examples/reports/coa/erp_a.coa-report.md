# Chart of accounts mapping: erp_a

- Source accounts: 81; target accounts: 110
- Approved (manual mapping file): 78 (96.3%)
- Suggested, waiting for review: 0 (0 at high confidence)
- Unmapped: 3
- Targets receiving more than one source account: 1
- Exceptions: 0 error, 6 warning
- Accounts with a balance in the trial balance: 78, of which not yet approved: 0

Suggestions are never approved by the tool. Review each one, then copy the accepted rows (source_account, target_account) into the manual mapping file and run again.

## Exceptions needing attention (6)

| Severity | Source account | Issue | Detail |
|---|---|---|---|
| warning | 1300 | unmapped | no suggestion at or above 0.65. Closest was 12150 Rent and other deposits (0.59). |
| warning | 2060 | type_unknown | source type 'Taxation' is not recognised, so type checks and type-limited suggestions cannot be applied |
| warning | 5040 | type_mismatch | source is expense but target 12010 is asset |
| warning | 5100 | unmapped | no suggestion at or above 0.65. Closest was 61210 Depreciation, vehicles (0.49). |
| warning | 7210 | unmapped | no suggestion at or above 0.65. Closest was 61040 Pension costs (0.51). |
| warning | 8030 | type_unknown | source type 'Taxation' is not recognised, so type checks and type-limited suggestions cannot be applied |

## Suggestions, lowest confidence first (0)

None.
