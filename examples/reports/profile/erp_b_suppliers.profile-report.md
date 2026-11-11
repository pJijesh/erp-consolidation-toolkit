# Data profile: erp_b_suppliers.csv

- Rows: 28
- Columns: 9
- Encoding read as: cp1252
- Key column `account_no`: 2 duplicated value(s) covering 4 row(s) (14.3%), 0 blank key(s)
- Fully identical rows beyond the first: 0
- Highest missing rate among required columns: 3.6%
- Format checks: 4 invalid of 98 checked values (4.1%)
- Warning: The file is not valid UTF-8, so it was read as Windows-1252. Check that accented characters look right, or re-export as UTF-8.

## Columns

| Column | Required | Missing | Missing rate | Distinct | Stray spaces |
|---|---|---:|---:|---:|---:|
| account_no | yes | 0 | 0.0% | 26 | 0 |
| account_name | yes | 0 | 0.0% | 28 | 2 |
| street |  | 0 | 0.0% | 23 | 0 |
| town |  | 1 | 3.6% | 15 | 0 |
| zip | yes | 1 | 3.6% | 25 | 0 |
| country_code |  | 0 | 0.0% | 4 | 0 |
| tax_id |  | 6 | 21.4% | 21 | 0 |
| contact_email |  | 7 | 25.0% | 19 | 0 |
| date_created |  | 0 | 0.0% | 28 | 0 |

## Format checks

| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |
|---|---|---:|---:|---:|---|
| zip | postcode | 27 | 1 | 3.7% | `4657` |
| tax_id | tax | 22 | 2 | 9.1% | `188475785`; `405570360` |
| contact_email | email | 21 | 1 | 4.8% | `accountsmonmoor-steelstockholders.exa...` |
| date_created | date:%d.%m.%Y | 28 | 0 | 0.0% |  |

## Duplicate key values

- `L700105`
- `L700121`

Missing means blank or a placeholder such as TBC, N/A or a lone dash. Format checks test the shape of a value only. They do not prove that a postcode, tax number or address exists.
