# Data profile: erp_a_parts.csv

- Rows: 54
- Columns: 6
- Encoding read as: utf-8
- Key column `part_no`: 0 duplicated value(s) covering 0 row(s) (0.0%), 0 blank key(s)
- Fully identical rows beyond the first: 0
- Highest missing rate among required columns: 0.0%
- Format checks: 3 invalid of 54 checked values (5.6%)

## Columns

| Column | Required | Missing | Missing rate | Distinct | Stray spaces |
|---|---|---:|---:|---:|---:|
| part_no | yes | 0 | 0.0% | 54 | 0 |
| description | yes | 0 | 0.0% | 53 | 0 |
| uom | yes | 0 | 0.0% | 3 | 0 |
| drawing_no |  | 0 | 0.0% | 51 | 0 |
| category |  | 0 | 0.0% | 4 | 0 |
| status |  | 0 | 0.0% | 2 | 0 |

## Format checks

| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |
|---|---|---:|---:|---:|---|
| part_no | regex:^[A-Z]{2}-[0-9]{5}(-[A-Z])?$ | 54 | 3 | 5.6% | `FX 10939 C`; `MC 10795 C`; `TL 10669 C` |

Missing means blank or a placeholder such as TBC, N/A or a lone dash. Format checks test the shape of a value only. They do not prove that a postcode, tax number or address exists.
