# Cutover plan and rehearsal checklist

Cutover is the controlled move from the old system to the new one for an entity. This page is a template: copy it, fill in the dates and names, and keep it current. It does not replace the target platform's own guidance.

## Principles

- Rehearse at least twice for each entity, with the second rehearsal run as if it were the real thing, using the timings from the first.
- Record a time for every task. A cutover plan without measured durations is a guess.
- Set a go or no-go point before the irreversible step, with criteria written in advance and a named decision maker.
- Plan the rollback before the cutover, and know the point after which rollback is no longer possible.
- Avoid year end, audit fieldwork, statutory filing dates and peak trading where the calendar allows.

## Timeline

| Stage | Typical content | Evidence that it is done |
|---|---|---|
| Plan | Scope, calendar, freeze rules, roles, communication list, rollback criteria | Plan approved by the sponsor |
| Rehearsal 1 | Full extract, cleanse, map, load, reconcile in a non-production target | Timings recorded, defects logged, reconciliation report |
| Fix and retest | Close defects. Update mapping and transformation rules | Defect log closed or accepted with owners |
| Rehearsal 2 | As rehearsal 1, on a fresh target, with business users checking | Reconciliations within tolerance, user sign-off on test scripts |
| Readiness review | Scorecard, open issues, training done, support in place | Go or no-go recorded with names |
| Freeze | No master data or configuration changes in the source. Transaction cut-off agreed | Freeze notice sent and acknowledged |
| Final extract | Extract at the cut-off time. Record control totals | Control totals signed |
| Final load | Load in dependency order | Load logs reviewed |
| Reconcile | Trial balance, receivables, payables, stock, open orders | Reconciliations signed by owners |
| Go or no-go | Decision against the written criteria | Decision, time and decision maker recorded |
| Open | First transactions. Hypercare begins | Smoke tests passed |
| Hypercare | Daily issue review, first close in the target | Exit criteria met, handover to support |

## Roles on the day

| Role | Responsibility |
|---|---|
| Cutover manager | Owns the plan and the clock. Calls each step |
| Business owner (finance) | Signs the financial reconciliations and the go or no-go from the finance side |
| Business owner (operations) | Signs stock, open orders and shop floor readiness |
| Data lead | Runs extracts, transformations and loads. Keeps the log |
| Technical lead | Environments, interfaces, access, performance |
| Support lead | Service desk readiness, known issues list, escalation route |
| Sponsor | Decides when the criteria are not clearly met |

See [governance-and-roles.md](governance-and-roles.md) for the wider role model.

## Go or no-go criteria (examples to adapt)

- Every trial balance period in scope reconciles within the agreed tolerance, with no unmapped balances.
- Receivables and payables ledgers agree to control accounts by customer and supplier.
- Stock quantity and value agree by part and location within the agreed tolerance.
- No open defect rated as blocking. Every accepted defect has an owner and a workaround.
- Users trained, access granted, support rota published.
- Rollback tested, or its limits documented and accepted by the sponsor.

The toolkit's `readiness` command can supply the data quality, mapping and reconciliation evidence for the first point. The rest comes from the programme.

## Rehearsal checklist

Tick each item for each rehearsal and record the date, the person and the result.

### Before

- [ ] Rehearsal environment refreshed to a known state and the refresh time recorded.
- [ ] Extract specification agreed: tables, filters, encoding, delimiter, control totals.
- [ ] Mapping tables (accounts, units, tax codes, terms) at a named version.
- [ ] Merge decisions for duplicates approved by named owners, with the date.
- [ ] Transformation rules written down and under version control.
- [ ] Reconciliation scripts or reports agreed with the finance and operations owners.
- [ ] Test users and test scripts ready.

### During

- [ ] Start and end time of every task recorded.
- [ ] Extract row counts and control totals recorded and compared with the source system.
- [ ] Profile run on every extract. Format and key problems reviewed.
- [ ] Load rejects listed with reasons and owners.
- [ ] Trial balance reconciled by period, including reclassifications between account classes.
- [ ] Sub-ledger reconciliations done (receivables, payables, stock, fixed assets).
- [ ] Open transactions loaded and spot-checked against source documents.
- [ ] Interfaces (bank, EDI, tax, payroll, warehouse, shop floor) tested with realistic messages.
- [ ] Intercompany balances agree between the migrated entity and its counterparties.

### After

- [ ] Total elapsed time compared with the available window, with a margin.
- [ ] Defects logged, prioritised and assigned.
- [ ] Differences between expected and actual reconciliation results explained, not just accepted.
- [ ] Rollback steps walked through and the point of no return agreed.
- [ ] Lessons recorded and the plan updated for the next rehearsal.
- [ ] Decision recorded: repeat, proceed to the readiness review, or change the approach.

## After cutover

- Keep the source system read-only and available for the period needed for audit, statutory and query purposes. Decide the period before cutover and check any record retention rules that apply (see [pitfalls.md](pitfalls.md)).
- Run the first month end close in the target with the old and new figures side by side for the entities that moved.
- Review the first week's issues daily and keep a single list.
- Hold a review within a month: what the plan assumed, what happened, what to change for the next wave.
