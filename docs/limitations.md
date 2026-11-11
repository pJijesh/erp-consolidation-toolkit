# Limitations

This page states what the toolkit does not do, where its answers are weakest, and how it should and should not be used.

## Scope

- **It works on CSV extracts only.** It does not connect to any ERP, database or API, and it cannot read native system formats. Getting a clean, complete extract is part of the migration work and is not solved here.
- **It never changes data.** It reads files and writes reports. Merging records, loading mappings and correcting source data are done elsewhere, by people with the right authority.
- **It is a set of checks and a decision aid, not a migration tool.** It does not extract, transform in bulk, load or cut over.
- **It is vendor neutral and therefore generic.** It knows nothing about the field names, code tables, tax codes or business rules of any particular product. Column mappings are supplied by the user.

## Matching

- **Fuzzy matching needs human review.** It makes mistakes in both directions: it will propose some merges that are wrong (two different companies with similar names, a parent and a subsidiary) and it will miss some that are right (the same company trading under different names, or with no shared tax number or postcode). The auto band is a proposal, not a decision.
- **The scores are judgement.** The weights and thresholds in [scoring-models.md](scoring-models.md) were chosen to give sensible results on typical data and tested on the synthetic examples. They were not calibrated on real data from any organisation. Run them on a sample of your own data, review the results by hand, and adjust before relying on them.
- **Blocking has consequences.** Party pairs are generated only between records that share a tax number or a postcode. A pair of records with a very similar name and neither shared is not reported. Under the current weights such a pair could not reach the review band anyway, but a change to the weights would need the blocking rules to change too.
- **Text similarity is character based.** It does not understand language. Translations, trading names and abbreviations beyond the built-in lists will score low.
- **Chart of accounts suggestions** rely on account type and name. A chart with poor names, no types, or accounts used differently from their names will get weak suggestions. On the synthetic examples, high-confidence suggestions were right in 73 of 75 cases and low-confidence ones in 41 of 55 (see [scoring-models.md](scoring-models.md)). Real charts will be harder. The manual mapping is the source of truth.

## Format checks

- **Checks test shape, not truth.** A well-formed tax number may belong to no one. A well-formed postcode may not exist.
- **Coverage of countries is narrow.** Postcode and tax number patterns are built in for GB, DE, FR and NL, with US postcodes. Other countries get a loose generic check. Add a `regex` check for others.
- **The patterns are simplified.** They check structure and length. They do not check check digits or live registries. They were compiled from public descriptions of the formats (secondary sources, not the national authorities' technical specifications) and are not a validation service. Use the official validation services for compliance purposes.
- **Dates** are checked against the formats given. A day and month swap in a value that parses under both formats cannot be detected.

## Reconciliation

- **No currency translation.** Balances are compared in the currency of the trial balance. Translation, revaluation and consolidation adjustments are out of scope.
- **Trial balance level only.** The command does not reconcile sub-ledgers, stock, fixed assets or open orders. See [data-migration.md](data-migration.md) for what else to reconcile.
- **Tolerance is a single absolute amount.** It does not scale with the size of the balance. Set it with care.
- **Sign convention** is debit positive and credit negative. A trial balance with a differently signed single balance column needs adjusting before use.

## Readiness scorecard

- **Thresholds are not standards.** They are judgement-based starting points, documented in [readiness-thresholds.md](readiness-thresholds.md) and overridable.
- **It measures data, not readiness of the organisation.** Training, support, interfaces, contracts, change capacity and appetite are outside it.
- **It reports on the files supplied only.** A tidy sample does not show that the whole estate is tidy.

## Decision framework

- **The scores are only as good as the evidence.** Scoring is a conversation among people who know the business. A different panel could score the same facts differently, and the tool can be steered by choosing generous scores. Record the evidence for each score. The tool warns when evidence is missing and shows which single changes would alter the outcome.
- **The thresholds are judgement, not research.** They have not been validated against a set of real programme outcomes.
- **It does not replace a business case.** It organises the questions. See [business-case.md](business-case.md).

## Data protection and confidentiality

- Extracts of customers and suppliers contain personal data (contact names, emails, addresses) and commercial data. Handle them under the organisation's data protection rules. Reports include example values unless `--no-examples` is used.
- The synthetic examples are fictional. Any resemblance to real organisations is accidental.

## Legal and regulatory

Statements about record retention, tax number formats and e-invoicing in this repository are general information, checked against public sources during the build, and are not legal or tax advice. Rules differ by country and change. Take advice for the entities concerned.

## Testing

- Verified on Python 3.13 in the build environment. The test workflow runs the suite on 3.10 to 3.13 in continuous integration. See the Verification status section of the [README](../README.md).
- Not tested against real ERP extracts. Real extracts will contain cases the synthetic data does not.
