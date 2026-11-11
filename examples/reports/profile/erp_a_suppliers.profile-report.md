# Data profile: erp_a_suppliers.csv

- Rows: 36
- Columns: 9
- Encoding read as: utf-8
- Key column `supplier_id`: 2 duplicated value(s) covering 4 row(s) (11.1%), 0 blank key(s)
- Fully identical rows beyond the first: 0
- Highest missing rate among required columns: 2.8%
- Format checks: 3 invalid of 134 checked values (2.2%)

## Columns

| Column | Required | Missing | Missing rate | Distinct | Stray spaces |
|---|---|---:|---:|---:|---:|
| supplier_id | yes | 0 | 0.0% | 34 | 0 |
| supplier_name | yes | 0 | 0.0% | 36 | 1 |
| address_1 |  | 0 | 0.0% | 30 | 0 |
| city |  | 0 | 0.0% | 20 | 0 |
| postcode | yes | 1 | 2.8% | 30 | 0 |
| country |  | 0 | 0.0% | 5 | 0 |
| vat_no |  | 3 | 8.3% | 32 | 0 |
| email |  | 6 | 16.7% | 25 | 1 |
| created |  | 0 | 0.0% | 36 | 0 |

## Format checks

| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |
|---|---|---:|---:|---:|---|
| postcode | postcode | 35 | 1 | 2.9% | `B6 5D` |
| vat_no | tax | 33 | 1 | 3.0% | `GB03921661` |
| email | email | 30 | 1 | 3.3% | `accounts@alddale-bearings.example ` |
| created | date:%Y-%m-%d\|%d/%m/%Y | 36 | 0 | 0.0% |  |
| | mixed date formats | | | | `%Y-%m-%d` x 27, `%d/%m/%Y` x 9 |

## Duplicate key values

- `S20002`
- `S20015`

Missing means blank or a placeholder such as TBC, N/A or a lone dash. Format checks test the shape of a value only. They do not prove that a postcode, tax number or address exists.
