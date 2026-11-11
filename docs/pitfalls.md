# Common pitfalls

These are the recurring problems in ERP and finance consolidations, grouped by area. Each one lists the symptom, why it happens, and what to do. None of this is specific to a product.

## Master data

**Symptom:** the same customer, supplier or part exists several times, under slightly different names or numbers, and the target ends up with the same mess in one place.

**Why:** each system had its own creation habits, local naming, free-text name fields, and no check for existing records. Two systems in one group often trade with the same companies under different names.

**What to do:**
- Profile and match before mapping, not after. The `profile` and `dedupe` commands are built for this.
- Treat fuzzy matches as proposals. A shared tax number with a different name can be a parent and subsidiary, or a branch, or a typo. A near-identical name with a different tax number is often two legal entities.
- Decide survivorship rules in advance: which record wins, how bank details are verified, who approves a supplier merge. Bank detail changes during a merge are a fraud risk and need the same controls as any other change.
- Agree the group standard for names, addresses, units of measure and part numbering before the first load, and keep a cross-reference from old identifiers to new ones. Users search by the old number for years.
- Parts: watch for the same physical item under different numbers, different items sharing a number, revision suffixes, and units that differ (each, box, kilogram). A part that is bought in boxes of 12 and stocked in each needs a conversion, not a rename.

## Open transactions

**Symptom:** at cutover, invoices, orders, deliveries and payments are half way through their life, and the new system cannot continue them.

**Why:** a transaction crosses the cutover boundary. The source system holds the history, the target needs only what is still live, and the two have different document structures.

**What to do:**
- Decide what counts as open: unpaid invoices, undelivered sales orders, unreceived purchase orders, work orders in progress, unreconciled bank items, unapplied cash.
- Prefer to reduce the open population before cutover (close old orders, apply unapplied cash, clear stale accruals) rather than migrate clutter.
- Load open items as they stand, with their original dates and references, so ageing and matching still work. Reconcile the totals to the control accounts.
- For payments and goods in transit across the cutover, write down who handles each case, and for how long.

## Historical data

**Symptom:** users want years of history in the new system, the migration cost grows, and nobody checked what must be kept and what can go.

**Why:** history is easy to ask for and expensive to migrate cleanly, because it was created under old structures.

**What to do:**
- Separate three needs: statutory and tax record keeping, operational reference (customer order history, part usage), and trend reporting.
- Record keeping: UK companies generally have to keep accounting records for at least six years, with different rules for some situations and other jurisdictions having their own rules. The group needs a view per country, and legal or tax advice where there is doubt. This was checked against GOV.UK guidance during the build of this toolkit. It is not legal advice and the rules change.
- Often the practical answer is opening balances by period in the target, a read-only archive of the source for detail, and a limited detail migration (for example open items and the current and previous year's summary). Plan access to the archive, who can query it, and how long it is kept and supported. An unsupported system in a corner is a security and audit problem.
- Trend reporting usually works from summarised data and does not need transaction detail.

## Customisations

**Symptom:** the target is configured to look like the old system, or key functions disappear because they lived in custom code nobody listed.

**Why:** customisations accumulate over years. Some are real differentiators, some are workarounds for old limitations, and some nobody remembers.

**What to do:**
- Inventory every custom report, interface, extension and manual workaround, with an owner and a use count. Ask users, not only IT.
- Classify each: retire, replace with standard function, rebuild as an extension, or keep outside the ERP. Keep the rebuild list short and justified.
- Be sceptical of "we have always done it this way" where the target offers a standard route. Be equally sceptical of "the standard process is better" where the old customisation protects margin, compliance or customer service.
- Customisation depth is one of the criteria in the [decision framework](../decision/README.md), because it drives cost, risk and time more than most other factors.

## Intercompany

**Symptom:** intercompany balances do not agree between entities during or after migration, and group reporting needs manual adjustments.

**Why:** entities post intercompany transactions at different times, in different currencies, with different references, and sometimes on different charts. During a phased migration, one side of a transaction is in the old system and the other in the new.

**What to do:**
- Agree intercompany accounts, counterparty codes, pricing and settlement rules in the group standard before migration.
- In a phased migration, design the temporary intercompany process explicitly, including who reconciles it and how often.
- Reconcile intercompany balances by counterparty at every rehearsal and at cutover, and eliminate differences at source rather than in the consolidation.
- Transfer pricing and tax treatment are tax matters. Involve the tax function.

## Other recurring problems

- **Scope creep during migration.** Process redesign and new reporting are added to a programme that was meant to move data. Separate what must change at cutover from what can follow.
- **Mapping approved once and never revisited.** Charts change while the programme runs. Version the mapping and rerun the coverage and reconciliation checks before each rehearsal.
- **Unit and currency assumptions.** Amounts in thousands, quantities in different units, and decimal commas in text extracts all cause silent errors. The toolkit rejects ambiguous number formats rather than guessing, but only for the files it reads.
- **Weak ownership.** Data cleansing is treated as an IT task. Business owners must decide merges, mappings and what to retire. See [governance-and-roles.md](governance-and-roles.md).
- **Optimism about change capacity.** Finance teams close the month while testing the new system. The [decision framework](../decision/README.md) includes change capacity as a criterion because it is the most common unspoken constraint.
- **Treating a readiness score as a decision.** The scorecard shows evidence in a few areas. It does not know about training, contracts or morale. See [limitations.md](limitations.md).
