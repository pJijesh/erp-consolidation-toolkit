# Data profile: erp_a_customers.csv

- Rows: 52
- Columns: 9
- Encoding read as: utf-8
- Key column `cust_id`: 2 duplicated value(s) covering 4 row(s) (7.7%), 0 blank key(s)
- Fully identical rows beyond the first: 0
- Highest missing rate among required columns: 3.9%
- Format checks: 3 invalid of 189 checked values (1.6%)

## Columns

| Column | Required | Missing | Missing rate | Distinct | Stray spaces |
|---|---|---:|---:|---:|---:|
| cust_id | yes | 0 | 0.0% | 50 | 0 |
| cust_name | yes | 0 | 0.0% | 52 | 2 |
| address_1 |  | 0 | 0.0% | 43 | 0 |
| city |  | 0 | 0.0% | 20 | 0 |
| postcode | yes | 2 | 3.9% | 44 | 0 |
| country |  | 0 | 0.0% | 5 | 0 |
| vat_no |  | 5 | 9.6% | 45 | 0 |
| email |  | 12 | 23.1% | 33 | 1 |
| created |  | 0 | 0.0% | 52 | 0 |

## Format checks

| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |
|---|---|---:|---:|---:|---|
| postcode | postcode | 50 | 0 | 0.0% |  |
| vat_no | tax | 47 | 2 | 4.3% | `GB37277534`; `GB68118734` |
| email | email | 40 | 1 | 2.5% | `accounts@lorden-testingservices.example ` |
| created | date:%Y-%m-%d\|%d/%m/%Y | 52 | 0 | 0.0% |  |
| | mixed date formats | | | | `%Y-%m-%d` x 47, `%d/%m/%Y` x 5 |

## Duplicate key values

- `C10002`
- `C10007`

Missing means blank or a placeholder such as TBC, N/A or a lone dash. Format checks test the shape of a value only. They do not prove that a postcode, tax number or address exists.
