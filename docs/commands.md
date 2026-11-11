# Command reference

Run the tool with `python -m erp_consol <command>` from a checkout, or `erp-consol <command>` after `pip install -e .`. Both forms are identical. Paths below are relative to the repository root and use the fictional files in [examples/](../examples/README.md).

Every command writes its reports to `--out` (default `output`, which is ignored by git) and prints the files it wrote. Output is deterministic: rows are sorted, JSON keys are sorted, there are no timestamps, and line endings are LF.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Completed |
| 2 | Input problem: missing file, empty file, missing column, unreadable encoding, bad option. The message names the file and the problem |
| 3 | A gate that was asked for was not met (`--fail-on-unapproved`, `--fail-on-difference`, `--fail-on-no-go`). Use these in a pipeline |

## Common input options

| Option | Meaning |
|---|---|
| `--encoding` | Default `auto`: UTF-8 (with or without a byte order mark), then Windows-1252 with a warning in the output. Name an encoding to force it |
| `--delimiter` | Default: detected from the header row among comma, semicolon, tab and pipe |
| `--out`, `--name` | Output folder and the prefix for output files |

Column names differ in every system, so each command takes a mapping from the tool's names to the file's names, written as `name=column,postcode=zip`. Names are matched without regard to case.

## profile

Data quality profile of one extract.

```
python -m erp_consol profile examples/data/erp_a_customers.csv \
  --config examples/config/erp_a_customers.json --out output/profile
```

Or without a config file:

```
python -m erp_consol profile examples/data/erp_a_customers.csv \
  --key cust_id --required cust_id,cust_name,postcode \
  --check postcode=postcode --check vat_no=tax --check email=email \
  --check "created=date:%Y-%m-%d|%d/%m/%Y" --country-col country
```

Reports row and column counts, missing values per column, repeated keys, and for each format check the number and share of values that fail, with examples (use `--no-examples` for personal data). Placeholders such as "n/a", "tbc" and "-" count as missing.

Check types: `postcode`, `tax`, `email`, `date` (formats separated by `|`), `number`, and `regex:<pattern>`. With `--country-col`, postcode and tax patterns are chosen per row. Patterns are built in for GB, DE, FR and NL (and US postcodes). Other countries get a loose shape check only. See [limitations.md](limitations.md).

Outputs: `<name>.profile-report.md`, `<name>.profile-summary.json`.

## map-coa

Map a source chart of accounts to a target chart.

```
python -m erp_consol map-coa \
  --source examples/data/erp_a_chart.csv --target examples/data/target_chart.csv \
  --manual examples/data/erp_a_manual_mapping.csv --tb examples/data/erp_a_trial_balance.csv \
  --source-map account=acct_no,name=acct_name,type=acct_type \
  --target-map account=account --tb-map account=acct_no \
  --name erp_a --out output/coa
```

The manual file (`source_account`, `target_account`, optional `note`) is applied first and its rows are approved. Everything else gets a suggestion or an exception. With `--tb`, accounts carrying a balance are marked so that unmapped balances are errors. Use `--decimal-comma` when the trial balance uses 1.234,56 amounts. `--fail-on-unapproved` exits with 3 if any account lacks an approved mapping.

Outputs: `<name>.mapping.csv` (all source accounts with target, method, confidence, status and flags), `<name>.exceptions.csv`, `<name>.coa-report.md`, `<name>.coa-summary.json`.

Workflow: run, review suggestions, copy accepted ones to the manual file, run again.

## dedupe

Probable duplicates within and across two systems.

```
python -m erp_consol dedupe --entity party \
  --a examples/data/erp_a_customers.csv --b examples/data/erp_b_customers.csv \
  --a-map id=cust_id,name=cust_name,postcode=postcode,tax=vat_no,country=country,email=email,city=city \
  --b-map id=account_no,name=account_name,postcode=zip,tax=tax_id,country=country_code,email=contact_email,city=town \
  --name customers --out output/dedupe
```

`--entity party` is for customers and suppliers, `--entity part` for parts (mapping names: `part_number`, `description`, `uom`, `drawing`, `category`). `--b` is optional, for a single system. `--auto` and `--review` change the thresholds (defaults 85 and 50). `--legal-suffixes` and `--uom-map` extend the built-in lists. The scoring model is in [scoring-models.md](scoring-models.md).

Outputs: `<name>.matches.csv` (every pair at review or above, with reasons and flags), `<name>.merge-proposal.csv` (groups, suggested survivor, fields to check, proposed action), `<name>.dedupe-report.md`, `<name>.dedupe-summary.json`. No source data is changed.

## reconcile

Trial balances before and after the mapping, by period.

```
python -m erp_consol reconcile \
  --tb examples/data/erp_a_trial_balance.csv --mapping output/coa/erp_a.mapping.csv \
  --source-coa examples/data/erp_a_chart.csv --target-coa examples/data/target_chart.csv \
  --source-map account=acct_no,name=acct_name,type=acct_type --tb-map account=acct_no \
  --target-tb examples/data/erp_a_loaded_target_tb.csv --target-tb-map account=account \
  --tolerance 0.05 --name erp_a --out output/reconcile
```

`--mapping` accepts the `map-coa` output or a plain manual file. Only approved mappings are used, unless `--include-suggested` is given (a preview). `--target-tb` adds a comparison with a trial balance from a trial load. `--allow-reclassification` lists movements between account classes without counting them as differences. `--fail-on-difference` exits with 3 if any period has differences. Amounts are debit positive and credit negative. No currency translation.

Outputs: `<name>.reconcile-by-period.csv`, `<name>.reconcile-differences.csv`, `<name>.reconcile-report.md`, `<name>.reconcile-summary.json`.

## readiness

Scorecard from the JSON summaries.

```
python -m erp_consol readiness output/profile/*.profile-summary.json \
  output/coa/*.coa-summary.json output/dedupe/*.dedupe-summary.json \
  output/reconcile/*.reconcile-summary.json --name group-readiness --out output/readiness
```

`--thresholds` takes a JSON file overriding any limits. `--fail-on-no-go` exits with 3 on NO-GO. See [readiness-thresholds.md](readiness-thresholds.md).

Outputs: `<name>-report.md` and `<name>-summary.json`.

## decide

Scored decision from a CSV of criterion scores and gate answers.

```
python -m erp_consol decide --scores decision/examples/two-manufacturers.csv --out output/decision
```

The scores file has `id`, `value` and `evidence` columns. Criteria are scored 1 to 5 and gates answered yes or no. `--criteria` points at a different criteria file. See [decision/README.md](../decision/README.md).

Outputs: `<name>.decision-report.md`, `<name>.decision-summary.json`.

## Reproducing the committed examples

```
python examples/generate_examples.py   # rewrites examples/data and examples/truth
python examples/run_examples.py        # rewrites examples/reports with the commands above
```

The test suite runs both into a temporary folder and compares the result byte for byte with the committed files, so the examples cannot drift from the code.
