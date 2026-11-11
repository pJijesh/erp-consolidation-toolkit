# Decision framework: consolidate, partially integrate or keep separate

Consolidating several companies onto one ERP and finance platform is sometimes the right decision and sometimes an expensive mistake. This framework turns the question into scored criteria with written anchors, so that a group can have a structured discussion, record the evidence behind each score, and see how sensitive the answer is.

It is a decision aid. It does not make the decision.

## The three outcomes

| Outcome | Meaning |
|---|---|
| Consolidate | One platform and one process template for the entities in scope. The case is strong and the group can deliver it |
| Partially integrate | Some common elements without a full migration: a shared chart of accounts and group reporting layer, shared master data for customers and suppliers, finance on one platform with operations left alone, or consolidation of a subset of entities |
| Keep separate | Entities keep their systems. Coordination is through reporting, policy and, where useful, light integration |

A fourth result, **Defer**, appears when a gate says the decision cannot yet be made (for example there is no accountable sponsor). It means resolve the blocker, then score again.

## How the scoring works

1. There are 13 criteria (C01 to C13) in two groups. Each group is an axis.
   - **Case for consolidation**: how much there is to gain (C01 to C06).
   - **Ability to deliver**: how likely the group is to deliver it without damage (C07 to C13).
2. Each criterion has a weight from 1 to 3 and is scored 1 to 5. The file [criteria.csv](criteria.csv) holds the question and written anchors for scores 1, 3 and 5. Use 2 and 4 for in-between cases.
3. Each axis is the weighted mean of its criteria, rescaled from 0 (all ones) to 100 (all fives).
4. Four gates (G01 to G04) are yes or no questions that override the scores.
5. The outcome follows from the two axis scores and the gates:

| Condition | Outcome |
|---|---|
| A gate with effect `defer` answered yes | Defer |
| Case 65 or more, and ability 60 or more | Consolidate |
| Case 40 or more, but not meeting the line above | Partially integrate |
| Case below 40 | Keep separate |
| Any `cap_partial` gate answered yes, otherwise Consolidate | Partially integrate |

Two axes are used on purpose. A strong case with weak ability to deliver is a pattern to guard against: the benefit is real, the programme is under-resourced, and the project damages the business. That combination leads to partial integration, which lowers risk and prepares the ground. A weak case with strong ability should not consolidate just because the group could.

The thresholds (65, 60 and 40) are judgement, not research. Change them in [erp_consol/decision.py](../erp_consol/decision.py) if the group's risk appetite differs, and record why.

## Criteria

### Case for consolidation

| Id | Criterion | Weight | What it asks |
|---|---|---:|---|
| C01 | Process similarity | 3 | How alike are the core processes across the entities? |
| C02 | Commercial case | 3 | Is there a net benefit over five years, validated by finance, that survives a pessimistic case? |
| C03 | Shared customers, suppliers and parts | 2 | Would one set of master data help? |
| C04 | Group reporting and control pain | 2 | How much does the current set-up hurt, and would a reporting layer fix it? |
| C05 | Contract and licence timing | 2 | Do contract and support dates line up with a migration window? |
| C06 | Strategic stability | 1 | Is the shape of the group stable enough for a long-lived platform decision? |

### Ability to deliver

| Id | Criterion | Weight | What it asks |
|---|---|---:|---|
| C07 | Customisation depth | 3 | How much custom code and unusual configuration would have to be rebuilt or retired? |
| C08 | Regulatory and statutory differences | 3 | How different are statutory reporting, tax, e-invoicing, language and retention requirements? |
| C09 | Currency and legal entity complexity | 2 | How complex are currencies, fiscal calendars, intercompany and entity structures? |
| C10 | Change capacity | 3 | Do finance, operations and IT have the capacity to deliver on top of the day job? |
| C11 | Data quality and master data readiness | 2 | How clean are the master data and charts? (The readiness scorecard supplies evidence.) |
| C12 | Sponsor and governance strength | 2 | Is there an accountable executive with authority over every entity, and a funded team? |
| C13 | Integration and interface footprint | 1 | How many integrations must be rebuilt? |

### Gates

| Id | Gate | Effect |
|---|---|---|
| G01 | Local system or statutory books required by law or regulation that the target cannot produce | Caps at partial integration |
| G02 | No accountable executive sponsor with authority over every entity | Defer |
| G03 | Sale or major restructure of an in-scope entity agreed or likely within twelve months | Defer |
| G04 | Target platform unproven for an in-scope entity's core process, with no working pilot or comparable reference | Caps at partial integration |

The weights reflect the author's judgement of what drives cost and risk (process fit, commercial case, customisation depth, regulatory differences and change capacity carry the most weight). They are a starting point, not research findings. If the group agrees different weights, edit the `weight` column and say so in the record.

## Using it

1. Convene the people who know: finance, IT, operations, and a representative from each entity. Do not score alone.
2. Copy one of the files in [examples/](examples/) as a template. Each row needs an `id`, a `value` (1 to 5 for criteria, `yes` or `no` for gates) and `evidence`.
3. Write the evidence before agreeing the score. "We think it is similar" is not evidence. "Both run make-to-order with the same routings, differing in quoting" is.
4. Run:

```
python -m erp_consol decide --scores decision/examples/two-manufacturers.csv --out output/decision
```

5. Read the report. It shows the two axis scores, the outcome and reasons, every score with its evidence, the weakest criteria, and a sensitivity list of criteria where a change of one point would change the outcome. It warns about criteria with no evidence.
6. Challenge the result. Ask which scores were generous. Ask what evidence would change them. Repeat scoring when facts change, and at each stage gate.

If the sensitivity list is long, the outcome is fragile and the group should say so. If it is empty, no single change of one point alters the outcome.

## When not to consolidate

Consolidation is often assumed to be the goal. It is not always the right one. The following situations justify keeping systems separate, or integrating only partly.

- **The businesses are different.** Different business models, different regulated activities, or process designs that would need a different system anyway. One platform does not create synergy where the processes do not share anything. A single ERP forced over two different businesses usually means heavy customisation, which removes much of the benefit.
- **A regulator or a law requires a local system or local books.** Where a legal or regulatory requirement cannot be met by the target, the answer is not to ignore it. Keep the local system, and integrate at the reporting layer.
- **The benefit is mostly reporting.** If the main pain is slow or manual group reporting, a reporting layer with a mapped group chart of accounts often solves it at a fraction of the cost and risk. The mapping and reconciliation tools in this toolkit are exactly that work.
- **The commercial case depends on one assumption.** Savings claimed from licences alone rarely cover migration, parallel running and exit costs. If the case does not survive a pessimistic scenario, treat it as unproven.
- **The group is about to change shape.** If an entity may be sold, merged or restructured within a year, a migration may be thrown away. If an entity is likely to be sold, keeping it separable has value.
- **Change capacity is not there.** If finance is already stretched by audit, year end or another programme, adding a migration puts the close, controls and people at risk. Sequencing can help. Sometimes the right answer is later.
- **The target platform is unproven for the entity.** Without a pilot or a comparable reference, the first migration is also the proof of concept. That can be acceptable for a small entity. It is a risk for the whole group.
- **Contracts and support run for years.** Termination fees and double running can outweigh the benefit if there is no window.
- **There is no empowered sponsor.** Consolidation requires decisions that cross entity boundaries. If no one can make them stick, the programme will stall at the first conflict.

Keeping separate is not doing nothing. It still needs a group chart of accounts or a mapping, intercompany discipline, and shared standards. The toolkit supports that too.

It is also not a one-off choice. A group can keep systems separate today, build the reporting layer and master data discipline, and revisit consolidation when contracts, capacity or structure change.

## Worked examples

Three fictional scoring files are included and their reports are committed under [examples/reports/decision/](../examples/reports/decision/).

| File | Outcome | Case | Ability |
|---|---|---:|---:|
| [two-uk-distributors.csv](examples/two-uk-distributors.csv) | Consolidate | 80.8 | 76.6 |
| [two-manufacturers.csv](examples/two-manufacturers.csv) | Partially integrate | 57.7 | 29.7 |
| [different-regulated-businesses.csv](examples/different-regulated-businesses.csv) | Keep separate | 17.3 | 34.4 |

[worked-example.md](worked-example.md) walks through the middle one.

## Limits of the framework

- The numbers look precise and are not. Scores are judgements recorded on a scale. A difference of one point between two panels is normal.
- The weights and thresholds have not been validated against a set of real programme outcomes.
- The criteria are not exhaustive. Add criteria that matter to the group (security posture, a specific regulator, a key customer requirement) by adding rows to the criteria file. Each criterion needs a weight, an axis and written anchors.
- It supports a conversation. It does not replace the business case ([../docs/business-case.md](../docs/business-case.md)), the approach decision ([../docs/approaches.md](../docs/approaches.md)) or the governance of the programme ([../docs/governance-and-roles.md](../docs/governance-and-roles.md)).
