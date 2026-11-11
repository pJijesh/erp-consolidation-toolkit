# Scoring models

This page documents exactly how the toolkit scores chart of accounts suggestions, duplicate pairs and consolidation decisions. The numbers are judgement-based starting points chosen to give sensible results on typical data. They are not industry standards. Every weight can be inspected in the code (`erp_consol/dedupe.py`, `erp_consol/coa.py`, `erp_consol/decision.py`) and tested against your own data before use.

## Name normalisation

Used for customers, suppliers and account names.

1. Fold to lower case without accents. German style umlauts and the sharp s are transliterated (for example the u umlaut becomes "ue").
2. Replace punctuation and repeated spaces with single spaces. An ampersand is read as "and". A leading "The" is dropped.
3. Expand a short list of common abbreviations (for example eng, intl, mfg, svcs, grp).
4. For parties, remove legal form words from the end of the name only: Ltd, Limited, PLC, LLP, Inc, GmbH, AG, KG, BV, SARL and similar, plus a trailing "and" or "co" left behind by forms such as "GmbH & Co. KG". A name is never reduced to nothing. Extra suffixes can be added with `--legal-suffixes`.
5. For account names, expand a short list of abbreviations and map UK wording to common wording (debtors to receivables, stock to inventory, depn to depreciation, and so on).

## Text similarity

Similarity is a number from 0 to 1 using the standard library `difflib.SequenceMatcher`. The function takes the better of the ratio on the text as written and the ratio with the words sorted, so "Pump Systems Brelden" scores well against "Brelden Pump Systems". Arguments are ordered before comparison so the result is the same whichever record is on the left.

This is a character-level measure. It handles typos, case, punctuation and reordering. It does not know that two different words mean the same thing, and it can give a high score to two different companies with similar names. That is why every automatic proposal is reviewed by a person.

## Party matching (customers and suppliers)

Evidence is additive, with guard rails. The score is clipped to 0 to 100.

| Evidence | Points |
|---|---:|
| Same tax number after normalisation | +50 |
| Name similarity, scaled linearly from 0 points at 0.50 to 40 points at 1.00 | 0 to +40 |
| Same postcode after normalisation | +15 |
| Same email domain | +5 |
| Both tax numbers present and different | -20, flag `tax_differs` |
| Both countries present and different | -10, flag `country_differs` |

Bands:

| Band | Rule | Meaning |
|---|---|---|
| Auto match | Score 85 or more and no flags | Proposed merge. A person still approves it |
| Review | Score 50 or more, or 85 or more with a flag | A person decides |
| No match | Below 50 | Not reported |

Reasoning:
- A matching tax number is the strongest evidence, but a group of companies can share one (branches), and tax numbers are mistyped, so it does not reach the automatic threshold alone. Tax number plus a close name does.
- A name alone can reach at most 40 and with an email domain 45. Pairs with no shared tax number or postcode therefore cannot reach review. This is deliberate: similar names alone are weak evidence.
- Conflicting evidence costs points and also stops an automatic match. A pair with the same name and different tax numbers goes to review, not to merge.
- Missing values give no evidence either way. A blank tax number does not match another blank one.

Because of the arithmetic above, pairs are generated only between records that share a tax number or a postcode. This is called blocking. It keeps the comparison cost low and loses no pair that could reach the review band under this model. If the weights are changed, the blocking rules in `party_block_keys` must be revisited. The unit tests check that the blocked result equals the full comparison on the fixtures.

## Part matching

| Evidence | Points |
|---|---:|
| Same part number after normalisation (case, separators and leading zeros inside digit runs are ignored) | +60 |
| Part numbers equal except for a one or two letter suffix after a digit (a revision style suffix) | +35, flag `revision_differs` |
| Same drawing number | +45 |
| Description similarity, scaled linearly from 0 at 0.50 to 30 at 1.00 | 0 to +30 |
| Same unit of measure after alias mapping | +10 |
| Units differ | flag `uom_differs` |
| Same part number but different drawing numbers | flag `drawing_differs` |

Bands are the same as for parties: auto match at 85 or more with no flags, review at 50 or more.

Notes:
- A unit of measure difference does not reduce the score, because the same part is often stocked in different units. It does stop an automatic match, because a merge would need a conversion factor. The flag makes this visible.
- Unit aliases (for example EA, EACH, PC, PCS) are built in. Add more with `--uom-map`, for example `CTN=BOX`.
- Description alone and unit cannot exceed 40, so a pair needs a part number relationship or a shared drawing to reach review.

## Clusters and survivors

Pairs in the auto band are joined into groups with a union-find structure, so that A matches B and B matches C gives one group of three. In each group the survivor is the record with the most complete data, with ties broken by system and identifier so that the output is stable. The merge proposal lists, for each non-survivor, the fields where the two records differ and need a decision, the weakest pair score in the group, and whether each record was matched directly to the survivor or only through another record. A group joined through a chain is a reason to look more closely.

## Chart of accounts suggestions

1. The manual mapping wins. Those rows are approved, with confidence 1.00. The tool checks that the target exists and is postable, and flags a type mismatch.
2. For every other source account, candidates are the postable target accounts of the same type. Types are normalised from the labels in each chart (for example "Fixed assets", "Cost of sales" and "Debtors" are recognised).
3. Candidates are ranked by normalised name similarity. The top candidate becomes a suggestion if its score is at least 0.65 (`--min-confidence`). A score of 0.85 or more is high confidence (`--high-confidence`). Between the two it is flagged `low_confidence`.
4. If the second candidate is within 0.03 of the first and is a different account, the suggestion is flagged `ambiguous`.
5. If the source type is not recognised, no type filter can be applied, so a suggestion is made only at high confidence.
6. If several source accounts point to one target, each is flagged `many_to_one`.
7. Suggestions always have status `review`. The tool never approves a mapping.

### Measured accuracy on the examples

The synthetic examples include a truth file for each chart (`examples/truth/coa_truth_*.csv`). With no manual mapping at all, the suggester gives these results, which a test asserts so the figures stay current:

| Chart | Accounts | High-confidence suggestions | Of which correct | Low-confidence suggestions | Of which correct | No suggestion |
|---|---:|---:|---:|---:|---:|---:|
| ERP A | 81 | 40 | 40 | 21 | 18 | 20 |
| ERP B | 110 | 35 | 33 | 34 | 23 | 41 |

Read this as: high-confidence suggestions were right in 73 of 75 cases, low-confidence suggestions in 41 of 55, and the tool made no suggestion for 61 accounts out of 191. This is data built by the author of the tool, with names that a human reader finds easy. Real charts are harder, so treat the figures as an upper bound and expect more manual work. The design intent is that the manual mapping does the work and the suggestions only reduce it.

## Reconciliation arithmetic

- Amounts are signed as debit minus credit, so debit balances are positive and credit balances negative. A trial balance with a single balance column is read as given.
- Per period, the source trial balance must net to zero within the tolerance, and the mapped balances plus unmapped balances must equal the source net.
- Per account class (asset, liability, equity, revenue, expense, unclassified), balances before are taken with the source account types and balances after with the target types. The difference is the reclassification caused by the mapping.
- If a trial balance from a trial load of the target is supplied, it is compared account by account with the mapped source, per period.
- The tolerance is an absolute amount (default 0.01) applied to each comparison. Reclassifications between classes are differences by default. `--allow-reclassification` lists them without counting them as differences, for cases where a type change is intended and agreed.
- No currency translation is done.

## Consolidation decision scores

The decision tool is described in [decision/README.md](../decision/README.md). In summary:

- Each criterion is scored 1 to 5 against written anchors for scores 1, 3 and 5, and has a weight from 1 to 3.
- Each of two axes (case for consolidation, ability to deliver) is the weighted mean of its criteria, rescaled so that all ones give 0 and all fives give 100.
- Consolidate needs a case score of 65 or more and an ability score of 60 or more. A case score of 40 or more but short of that gives partial integration. Below 40 gives keep separate.
- Gates are yes or no questions. A gate with effect `defer` stops the decision until it is resolved. A gate with effect `cap_partial` limits the outcome to partial integration.
- The sensitivity check moves each criterion up and down by one point and lists those that would change the outcome.

The thresholds are judgement, not research. They are chosen so that a full consolidation needs both a clear benefit and a credible ability to deliver, and so that a strong case with weak delivery capacity produces a lower risk option rather than a green light.
