# Examples

Everything in this folder is fictional. The group, its two companies, customers, suppliers, parts, people, addresses, tax numbers and balances are invented by a seeded script. Tax numbers are random digits and are not checked against any register. Any resemblance to a real organisation is accidental.

## The fictional group

| | ERP A | ERP B |
|---|---|---|
| Company | Marrowdale Castings Limited | Norvane Dichtungen GmbH |
| Country | United Kingdom | Germany |
| Currency | GBP | EUR |
| Business | Cast and sealing components, made to order | The same family of products |
| Chart of accounts | 81 accounts, four digit codes | 110 accounts, six digit codes, different grouping and labels |

A third file, `target_chart.csv`, is the fictional group chart of accounts both entities would map to (110 accounts).

## Files

### data/ (inputs)

| File | Content | Deliberate problems |
|---|---|---|
| `erp_a_chart.csv`, `erp_b_chart.csv` | Charts of accounts | Different numbering schemes, type labels and names. Some accounts have no counterpart in the target. ERP A has two accounts with an unrecognised type label |
| `target_chart.csv` | Group chart | Header accounts that are not postable |
| `erp_a_manual_mapping.csv`, `erp_b_manual_mapping.csv` | Manual mappings agreed by the fictional group finance team | ERP A covers most accounts. ERP B covers about half, and includes planted mistakes (a mapping to a target account that does not exist and a row naming a source account that is not in the chart) that the tool should catch. ERP A maps one expense account to an asset account, which the tool flags as a type mismatch |
| `erp_a_trial_balance.csv`, `erp_b_trial_balance.csv` | Three monthly trial balances (2026-01 to 2026-03), debit and credit columns | Each balances to zero. ERP B uses semicolons and decimal commas |
| `erp_a_loaded_target_tb.csv` | A trial balance as if loaded into the target in a trial migration | Two planted differences from the mapped source |
| `erp_a_customers.csv`, `erp_b_customers.csv` | Customer masters | Duplicates within and across systems with name variants (case, punctuation, legal form, a GmbH & Co. KG spelling, single letter typos), missing and malformed postcodes, tax numbers and emails, placeholder values, a repeated key in each file, mixed date formats |
| `erp_a_suppliers.csv`, `erp_b_suppliers.csv` | Supplier masters | The same kinds of problem |
| `erp_a_parts.csv`, `erp_b_parts.csv` | Part masters | Different part numbering styles, revision suffixes, abbreviations in descriptions, different units of measure (for example ERP A boxes and ERP B pieces, or CTN and BOX) |

Format of the ERP B files, chosen to look like a European export: semicolon delimiters and decimal commas in the trial balance. The ERP B customer and supplier masters are Windows-1252 encoded, so the tool reads them with a warning that the encoding was detected. A UTF-8 reader would show corrupted characters in the German street names.

### truth/ (expected answers)

The generator writes what it planted, so the tests and the documentation can say what the tools should find.

| File | Content |
|---|---|
| `expected_pairs_customers.csv`, `expected_pairs_suppliers.csv`, `expected_pairs_parts.csv` | Planted duplicate pairs with the expected band and the bands that are acceptable. Includes near misses that should not match (a parent and subsidiary at one address, similar names with different tax numbers) |
| `coa_truth_erp_a.csv`, `coa_truth_erp_b.csv` | The intended target account for each source account |

### config/

Profile settings per file: key, required columns, country column and format checks. The profile commands read these with `--config`.

### reports/ (committed outputs)

Every report in `reports/` was produced by running the commands in `run_examples.py`. A test regenerates them in a temporary folder and compares them byte for byte, so a change in the code that changes the output fails the test until the reports are regenerated and reviewed.

| Folder | Content |
|---|---|
| `reports/profile/` | A profile report and summary for each of the six master data files |
| `reports/coa/` | Mapping, exceptions, report and summary for each chart |
| `reports/dedupe/` | Matches, merge proposal, report and summary for customers, suppliers and parts |
| `reports/reconcile/` | Reconciliation for ERP A (with the loaded target trial balance), ERP B (approved mappings only) and an ERP B preview that includes suggestions |
| `reports/readiness/` | The group scorecard |
| `reports/decision/` | The three decision examples (see [../decision/README.md](../decision/README.md)) |

## Reproducing

From the repository root:

```
python examples/generate_examples.py   # rewrites data/ and truth/
python examples/run_examples.py        # rewrites reports/
```

Both are deterministic. Running them twice gives identical files.

## What the results show

- ERP A: 78 of 81 accounts have an approved mapping (96.3 percent). The mapping preview moves some balances between account classes because source and target types differ, and the reconciliation shows it.
- ERP B: 55 of 110 accounts are approved, 34 have suggestions waiting for review and 21 have none. The reconciliation, using only approved mappings, leaves 55 balances unmapped and fails in every period. The preview, which adds the suggestions, leaves 21 unmapped.
- Customers: 94 records, 16 proposed merge groups (9 of them spanning both systems) and 10 pairs for review.
- Readiness: NO-GO, with 20 red, 8 amber and 6 green checks. That is the intended result for a first pass over messy data. See [../docs/readiness-thresholds.md](../docs/readiness-thresholds.md).

None of this is a benchmark. The data was built to contain problems of the kinds described, in quantities that make the reports readable.
