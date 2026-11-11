# Data profile: erp_b_customers.csv

- Rows: 42
- Columns: 9
- Encoding read as: cp1252
- Key column `account_no`: 2 duplicated value(s) covering 4 row(s) (9.5%), 0 blank key(s)
- Fully identical rows beyond the first: 0
- Highest missing rate among required columns: 2.4%
- Format checks: 10 invalid of 154 checked values (6.5%)
- Warning: The file is not valid UTF-8, so it was read as Windows-1252. Check that accented characters look right, or re-export as UTF-8.

## Columns

| Column | Required | Missing | Missing rate | Distinct | Stray spaces |
|---|---|---:|---:|---:|---:|
| account_no | yes | 0 | 0.0% | 40 | 0 |
| account_name | yes | 0 | 0.0% | 42 | 4 |
| street |  | 0 | 0.0% | 38 | 0 |
| town |  | 1 | 2.4% | 20 | 0 |
| zip | yes | 1 | 2.4% | 38 | 0 |
| country_code |  | 0 | 0.0% | 4 | 0 |
| tax_id |  | 8 | 19.1% | 33 | 0 |
| contact_email |  | 5 | 11.9% | 33 | 3 |
| date_created |  | 0 | 0.0% | 42 | 0 |

## Format checks

| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |
|---|---|---:|---:|---:|---|
| zip | postcode | 41 | 3 | 7.3% | `0194`; `3043`; `4715` |
| tax_id | tax | 34 | 3 | 8.8% | `088948167`; `614211964`; `641433961` |
| contact_email | email | 37 | 4 | 10.8% | `accounts@garshaw-manufacturing.example `; `accounts@harnham-bearings.example `; `accounts@tavdale-logistics.example `; `accountsbrelthorn-metals.example` |
| date_created | date:%d.%m.%Y | 42 | 0 | 0.0% |  |

## Duplicate key values

- `K400104`
- `K400112`

Missing means blank or a placeholder such as TBC, N/A or a lone dash. Format checks test the shape of a value only. They do not prove that a postcode, tax number or address exists.
