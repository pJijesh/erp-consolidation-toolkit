# Governance and roles

Consolidation programmes fail more often from unclear decisions than from technology. This page sets out a simple structure: who decides, who owns data, how decisions are recorded, and when to stop.

## Decision forums

| Forum | Members | Decides | Frequency |
|---|---|---|---|
| Steering group | Executive sponsor (chair), finance leader, IT leader, an operations leader, a representative of each entity | Scope, approach, budget, timeline, go or no-go at stage gates, escalated issues | Monthly, and at each gate |
| Design authority | Finance and process owners, IT architect, data lead | Group chart of accounts, master data standards, process template, customisation requests | Fortnightly |
| Data council | Data owners for customers, suppliers, parts and accounts, data lead | Merge approvals, survivorship rules, mapping sign-off, retention of historical data | Weekly during cleansing |
| Programme team | Programme manager, workstream leads | Day to day delivery, issues and risks, rehearsals | Weekly or more often |

Smaller groups can combine the design authority and the data council. Do not combine the steering group with the delivery team, or the people reporting progress and the people judging it become the same people.

## Roles

| Role | Accountable for | Common mistake |
|---|---|---|
| Executive sponsor | Outcome, authority across all entities, funding, resolving conflicts between entities | A nominal sponsor with no authority over a subsidiary |
| Finance leader | Chart of accounts, mapping, reconciliations, statutory and tax requirements, the commercial case | Leaving mapping to IT |
| IT leader | Platform, environments, integrations, security, technical delivery, support after go-live | Owning business decisions by default |
| Process owners | Process design and acceptance for order to cash, procure to pay, plan to produce, record to report | Joining only at user acceptance testing |
| Data owners | Quality and decisions for each master data domain | Treating data as an IT task |
| Data lead | Extract, cleanse, map, load and reconcile pipeline, evidence, tooling | Doing everything without owners' approvals |
| Entity leads | Local readiness, local statutory input, local people | Being informed rather than involved |
| Programme manager | Plan, risks, issues, dependencies, reporting | Reporting green until the last month |
| Change and training lead | Impact assessment, communications, training, support at go-live | Starting training too late to change anything |
| Internal audit or risk | Independent view of control design and migration evidence | Being asked after the event |

A RACI table for the main decisions should be agreed at the start. Keep it to one accountable person per decision.

## Decisions that need a named owner

- Which approach to use and when to stop or change it.
- The group chart of accounts and each entity's mapping to it.
- Survivorship rules and each merge group, for customers, suppliers and parts.
- What history is migrated, archived or discarded.
- What custom functions are rebuilt or retired.
- Tolerances for reconciliations and what counts as an acceptable difference.
- Go or no-go for each rehearsal and for each cutover.

## Records to keep

- A decision log with date, decision, options considered, who decided and why.
- A risk and issue log reviewed at every steering group.
- Approved mapping files and merge decisions with approver and date.
- Reconciliation and readiness evidence for each rehearsal and each cutover.
- Change requests against the agreed template, with the cost and effect on the plan.

The toolkit's reports are inputs to these records. A report in a folder is not an approval.

## Reporting and control

- Report against stage gates and evidence, not only percentage complete. A useful status is: what has been reconciled, what has not, what has been decided, what is blocked.
- Escalate early. A risk that is known for three weeks and not escalated is an issue.
- Keep an independent check on data reconciliations. The person who loaded the data should not be the only person to sign it off.
- Agree before the programme starts what would make the group stop, pause or change approach: a failed rehearsal, loss of the sponsor, a sale of an entity, or a business case that no longer holds.

## When the answer is not to proceed

Stopping or scaling back is a legitimate outcome, and the governance should make it possible. The [decision framework](../decision/README.md) is designed to be revisited at stage gates, not only at the start. If the evidence moves from "consolidate" to "partially integrate", the steering group should be able to say so without it being read as failure.
