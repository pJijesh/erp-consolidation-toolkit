# Business case outline

A consolidation business case should be short enough to read and honest enough to survive a pessimistic review. This page is an outline for finance and IT leaders to adapt. It contains no benchmark figures, because credible numbers come from the group's own costs and estimates.

## 1. Decision requested

State what is being asked: approve the programme, fund a pilot, or approve a smaller alternative. Name the options considered, including the option to do nothing and the option to keep systems separate with a group reporting layer. The [decision framework](../decision/README.md) gives a structured way to compare them.

## 2. Context and problem

- The entities in scope, their systems, versions, support dates and contract end dates.
- The problems that justify change, with evidence: close duration, manual effort, audit findings, intercompany differences, control weaknesses, system support risk, duplicated licences and infrastructure.
- What happens if nothing changes, over the same horizon as the options.

## 3. Options

For each option (for example consolidate in phases, consolidate finance only, coexist with a reporting layer, do nothing):

- Scope and approach (see [approaches.md](approaches.md)).
- What changes for users and what does not.
- Timeline with stage gates.
- Dependencies and assumptions.

## 4. Costs

Count the full cost over the horizon, normally five years, including costs that are easy to leave out.

| Category | Examples |
|---|---|
| Platform | Licences or subscriptions, environments, integration tooling |
| Implementation | Partner or consultancy fees, internal team time, backfill for people released to the programme |
| Data | Extraction, cleansing, mapping, merge reviews, reconciliation, archiving of history |
| Integrations | Rebuilding banks, EDI, shop floor, warehouse, tax, payroll, reporting |
| Customisation | Rebuild of retained extensions and reports |
| People | Training, change management, temporary productivity loss |
| Parallel running | Old and new systems side by side, extra reconciliation effort, temporary interfaces |
| Exit | Contract termination fees, data retention and archive access, decommissioning |
| Support | Run costs after go-live, upgrade effort |
| Contingency | Stated explicitly, with the basis for the percentage |

Separate one-off from recurring cost. State which figures are quotes, which are estimates and which are assumptions.

## 5. Benefits

Be specific about what changes and who owns the benefit.

| Type | Examples | Care needed |
|---|---|---|
| Cost reduction | Fewer licences and systems, fewer finance posts, lower support cost | Only count savings that will actually be taken |
| Cost avoidance | Avoiding an upgrade or an unsupported platform | Show the cost that would otherwise be incurred |
| Control and risk | Fewer audit findings, stronger intercompany control, fewer manual journals | Describe the risk reduced, even if it is not given a monetary value |
| Speed | Faster close, faster group reporting | Say what the group will do with the time |
| Commercial | A single view of customers and suppliers, better purchasing leverage, consistent pricing | Often the weakest evidence. Test it with the people who would deliver it |

Do not count benefits that need other changes that are not in the scope. Do not double count a saving under two headings.

## 6. Evidence from the toolkit

The toolkit can supply some of the evidence a case needs:

- The readiness scorecard shows how much data work remains before a migration could go ahead.
- The duplicate reports size the merge workload and show how much customer and supplier overlap exists between entities.
- The mapping coverage shows how close the charts are and how much manual mapping remains.

These measure effort and data quality. They do not measure benefit.

## 7. Risks

List the main risks with an owner and a response, not just a description. Typical ones are covered in [pitfalls.md](pitfalls.md): master data quality, open transactions, history, customisations, intercompany, change capacity, vendor delivery, sponsor change, and the possibility that a rehearsal fails.

## 8. Sensitivity and a pessimistic case

Show what happens if costs are higher, benefits are delayed, or the timeline slips. State the point at which the case no longer holds. A case that depends on one assumption should say so. The commercial case criterion (C02) in the decision framework asks whether the benefits survive a pessimistic case for the same reason.

## 9. Governance and gates

Who decides, when, and on what evidence. Stage gates tied to rehearsals and readiness evidence, and the conditions under which the programme would pause, change approach or stop. See [governance-and-roles.md](governance-and-roles.md).

## 10. Recommendation

One paragraph, plain language: what is recommended, why, what it costs, what it returns, what could go wrong and what the next decision point is.

## Presenting it

- Lead with the decision and the recommendation, then the evidence.
- Keep a short version for executives and a longer one for finance and IT.
- Show the options side by side with the same measures.
- Record assumptions and who validated each one. Finance should own the numbers.
