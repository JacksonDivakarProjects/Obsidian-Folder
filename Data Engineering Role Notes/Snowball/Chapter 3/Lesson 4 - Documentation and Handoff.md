GreenTide Analytics' leadership had already been burned once before you ever showed up: a retention metric went into a board deck, and it was wrong. Reconstruct incidents like that and you almost never find a math error. You find a convention — how a multi-year contract was annualized, whether the Quick Ratio counted reactivation, what the BOP anchor was for a year-to-date view — that lived in exactly one person's head, got applied one way in March and another way in June, and was eventually discovered by an outsider rather than by the team that owned the number. This lesson builds the artifact that stops that from happening: a methodology document.

## The failure mode this prevents

There is a specific and very ordinary sequence that produces a wrong number in a board deck.

Someone builds a bridge. They make a dozen judgment calls along the way — most of them defensible, several of them arguable, none of them recorded. The numbers look right, so nobody interrogates them. Six months later that person is on another project, or another team, or another company. Someone else needs the same metric for a new period. They read the SQL, form a reasonable but different understanding of what it does, adjust something, and rerun it. Now two versions of the number exist and nobody can say which is correct, because *correct* was never written down — it was only ever implemented.

The test suite from [[Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] does not catch this. Every one of those six tests can pass on a bridge built with the wrong convention, because the tests verify that the bridge is internally consistent, not that its assumptions match the business's intent. A methodology doc is the only thing that makes an assumption *reviewable*.

## The template

What follows is meant to be copied and filled in, not read once. Eight sections. Keep it in the repo next to the SQL so it moves with the code, and link it from the artifact itself per the labeling discipline in [[Lesson 3 - Building the Delivery Artifact|Lesson 3]].

```markdown
# ARR Bridge — Methodology
Owner: <name / team>          Last reviewed: <YYYY-MM-DD>
Refresh cadence: <daily / weekly / monthly, and when>

## 1. Input contract
Source tables and the exact columns depended on.
| Table | Columns used | Required? | Behaviour if missing/null |
|---|---|---|---|
| | | | |

## 2. Grain
This bridge is built at the ____ grain.
Dimensions available for slicing (not part of the grain): ____
Why this grain: ____

## 3. Date handling
Scenario in use: <1 / 2 / 3>  (see Ch.1 L6)
Period boundary rule: ____
Precedence when source systems disagree: ____

## 4. ARR normalization conventions applied
| Contract type | Present in this dataset? | Rule applied | Rationale |
|---|---|---|---|
| Usage-based | | | |
| Multi-year / prepaid | | | |
| Prorated / mid-period | | | |
| Non-USD / FX | | | |
| Discounts, credits, one-offs | | | |

## 5. LTM vs YTD
Built as: <LTM / YTD / both>
BOP anchor logic: ____
Reset behaviour at fiscal year boundary: ____

## 6. What the tests guarantee — and what they don't
Tests in place: ____
Guaranteed: ____
NOT guaranteed: ____

## 7. Known limitations
| # | Limitation | Judgment call made | Impact if wrong | Flagged by |
|---|---|---|---|---|

## 8. Ownership and support
Maintainer: ____      Backup: ____
Runs: ____            Alerting: ____
"This number looks wrong" → contact: ____
Escalation for a convention change: ____
```

Now, what actually goes in each section — and what a thin version of it looks like, since a thin version is worse than none at all.

### 1. Input contract

Name the exact source tables and columns the bridge reads, and state what happens when one of them isn't there or is null. Not "we read from the subscriptions table" — the column list, because the column list is what a future upstream migration will break.

The failure-behaviour column is the part people skip and the part that matters. If `contract_end_date` is null, does the row get excluded, treated as open-ended, or does the build fail loudly? All three are legitimate choices. Only one of them is *your* choice, and if it isn't written down, the next person will assume a different one — silently, and only for the rows where it matters.

### 2. Grain

Customer-only? Customer × product? Customer × region? [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Chapter 2, Lesson 8]] drew the distinction that belongs here: **grain** is the level at which buckets are *computed*, **dimensions** are attributes you can slice a computed bridge by afterward. They are not the same decision and they produce different numbers.

A customer-grain bridge where a customer drops product A and adds product B of equal value shows *nothing* — no expansion, no contraction, a flat line. A customer × product grain bridge on the same data shows churn on A and new on B. Neither is wrong. But a reader who assumes the wrong one will misread every quarter you publish.

So write the grain, and write *why*. "Customer grain, because the retention conversation leadership cares about is 'are we keeping accounts', and product-level movement inside a stable account is a product question we answer separately."

### 3. Date-handling scenario

[[Lesson 6 - Getting Real-World Dates Right|Chapter 1, Lesson 6]] laid out three scenarios for how source data expresses time. Say which one this dataset is, and how you determined that — because the determination is usually an inference from profiling, not a fact stated anywhere in the source system.

Then the part that only shows up in real datasets: **precedence rules when sources disagree.** If billing says a contract ended 2026-03-31 and the CRM says 2026-04-15, which one wins, and is it always the same one? Write the rule. "Billing system is authoritative for end dates; CRM is authoritative for customer hierarchy" is a perfectly good rule. An unwritten rule that billing usually wins except when the CRM date is later is not a rule, it's a habit, and habits don't survive handoff.

### 4. ARR normalization conventions actually applied

The heart of the document, and the direct descendant of [[Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4]]. For every non-standard contract type present in *this* dataset, state the rule in enough detail that a reader never has to open the SQL to find it.

"Usage-based contracts are annualized" is not enough. Annualized from what window? A trailing month × 12? A trailing three months × 4? A trailing twelve months as-is? Those produce materially different ARR for the same customer, and they produce differently *volatile* ARR, which is what shows up as phantom expansion and contraction in your bridge.

Write it like this instead: "Usage-based contracts are annualized as the most recent complete calendar month of consumption × 12. Chosen for consistency with the finance team's existing revenue reporting; accepted tradeoff is that seasonal accounts will show expansion and contraction that reflects usage timing rather than a commercial change."

Note the shape of that sentence: rule, rationale, known cost. All three. The rationale is what lets someone evaluate whether the rule still fits when the business changes, and the cost is what stops them from being surprised by it.

### 5. LTM vs YTD

Which one was built, and the **exact BOP-anchor logic**. For LTM, the anchor is the same period one year prior. For YTD, it is the start of the fiscal year — which requires you to state when the fiscal year starts, whether the anchor resets on that boundary, and what happens to a customer who was acquired mid-year.

If both views exist, say so and state which is the default in the artifact, because "ARR bridge" on a dashboard tab with no qualifier is exactly the ambiguity that produces two people quoting two different retention numbers in the same meeting.

### 6. What the tests guarantee — and what they don't

List the tests from [[Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] that are actually running, and then — the section people leave out — state the boundary of what a passing suite means.

Those tests verify **internal consistency**: that BOP plus the buckets equals EOP, that no customer appears in mutually exclusive buckets in the same period, that this period's EOP equals next period's BOP, that no bucket contains a sign it shouldn't, that customer counts reconcile, that the bridge total matches the source ARR total.

They cannot verify **business judgment**. A green suite tells you nothing about whether annualizing usage from a single trailing month was the right call, whether customer grain was the right grain, whether the CRM should have won the date dispute. Every one of those can be wrong while every test passes, because the tests check that the bridge is consistent with itself and the conventions are an input to the bridge, not an output of it.

Write that sentence, verbatim if you like, into the doc. A stakeholder who sees "all tests passing" and reads it as "the number is right" is one board deck away from GreenTide's incident.

### 7. Known limitations

Everything flagged during profiling that was a **judgment call rather than a certainty**. This is the section that ages best and gets written least, because writing it feels like admitting weakness, and it is in fact the strongest thing in the document — it is the difference between a number that can be defended and a number that can only be asserted.

Entries look like this:

> *Coral Bay Legal's ARR is usage-based and annualized from the trailing single month. Their contract started six weeks ago, so this figure may not reflect a full year of typical usage. If they show large expansion or contraction next quarter, check whether the underlying consumption pattern actually changed before reporting it as a commercial event.*

That entry does three jobs at once: it names the specific account, it explains why the number is soft, and it tells the next reader what to check before they act on it. That is what a limitation entry should do. "Some ARR values are estimates" does none of them.

Anything you hesitated over during profiling goes here. If you had to decide it, someone will eventually have to re-decide it, and they should start from your reasoning rather than from scratch.

### 8. Ownership and refresh cadence

Who maintains this. Who covers when they're out. How often it reruns and on what trigger. Where the alerting goes when a run fails. And the single most-used line in the whole document: **who to contact when a number looks wrong.**

Without that line, "this number looks wrong" gets raised in a meeting instead of a ticket, and the default resolution to a number nobody owns is that people stop using it.

Add one more: **how a convention gets changed.** Changing an ARR normalization rule silently re-bases every historical period and makes this quarter incomparable to last quarter. That should require a decision and a note in this document, not a pull request.

## The argument, stated plainly

A methodology doc is not process for its own sake. It is the mechanism by which someone *other than you* can trust the bridge and maintain it.

Trust, concretely, means a stakeholder can answer "why is this number what it is?" without you in the room. Maintain, concretely, means the next person can extend it without reverse-engineering your intent from SQL — because reverse-engineering intent from code recovers *what* it does and never *why*, and the why is the entire content of a convention.

And it is specifically what would have caught GreenTide's problem before the board deck instead of after. A written convention is a **reviewable** convention. Put "usage-based ARR is annualized from the trailing single month" on a page in front of a finance lead and there is a real chance they say "that's not how we do it — we use trailing twelve." That conversation takes ninety seconds and it happens *before* the deck. The same disagreement, undocumented, surfaces as a discrepancy someone finds afterward, and by then the argument is no longer about a convention. It's about whether the data team's numbers can be relied on at all.

Which is the actual cost of skipping this lesson. Numbers without a legible methodology don't get corrected — they get quietly abandoned. Somebody rebuilds them in a spreadsheet they control, with their own conventions, also undocumented, and now the organization has two retention numbers and a slow argument about which is real. Every bridge that gets rebuilt from scratch in a spreadsheet was, at some point, a correct bridge that nobody could vouch for.

## 📌 Key Takeaways

- A wrong metric in a board deck is almost never a math error. It's an unwritten convention, applied inconsistently, found by an outsider. The methodology doc exists to make conventions reviewable before they ship.
- Eight sections: input contract, grain, date handling, ARR normalization conventions, LTM vs YTD, what tests do and don't guarantee, known limitations, ownership and cadence.
- State every convention as **rule + rationale + known cost**. "Usage-based ARR is annualized" is not documentation; "annualized from the most recent complete month × 12, chosen to match finance's reporting, with the accepted cost that seasonal accounts show phantom expansion" is.
- A green test suite proves **internal consistency**, not business correctness. Every one of the Chapter 2 Lesson 6 tests can pass on a bridge built with the wrong normalization convention or the wrong grain. Write that limitation down where stakeholders will read it.
- The known-limitations section is the strongest part of the document, not the weakest — it turns a number you assert into a number you can defend, and it tells the next reader exactly what to check.
- Undocumented numbers don't get corrected, they get rebuilt in someone else's spreadsheet. That is the real cost of skipping the doc.

## ✅ Check Your Understanding

**1. Your bridge passes all six tests from Chapter 2, Lesson 6. A stakeholder asks whether that means the ARR figures are correct. What do you tell them?**

**Answer:** That the tests prove the bridge is internally consistent — buckets sum to the EOP, periods chain correctly, no customer lands in contradictory buckets, totals reconcile to source — but they cannot evaluate the conventions the bridge was built on. Grain choice, date precedence, and ARR normalization rules are *inputs* to the calculation, so a bridge built on a convention the business disagrees with will pass every test cleanly. Correctness of conventions is established by review of the methodology doc, not by the test suite.

**2. A methodology doc says "multi-year contracts are annualized." Why is that entry inadequate, and what would a sufficient version contain?**

**Answer:** It states that something was done without stating what, so the next reader still has to open the SQL — which defeats the purpose. Annualizing a three-year $300,000 prepaid deal could mean $100,000 per year for three years, or the full $300,000 recognized in year one, or a schedule tied to the billing terms; each produces a different ARR and a different bridge. A sufficient entry gives the rule ("total contract value ÷ contract term in years, held flat across the term"), the rationale for choosing it, and the known cost ("renewals at the same rate show as neither expansion nor contraction, which understates commercial activity on multi-year accounts").

**3. What kind of item belongs in the known-limitations section, and why is it more valuable than it looks?**

**Answer:** Anything that was a judgment call rather than a certainty — typically things surfaced during profiling. The Coral Bay Legal example is the shape: a usage-based account annualized from a single trailing month, flagged because six weeks of history may not represent a typical year, with a note to check the underlying consumption before treating next quarter's swing as a commercial event. It's valuable because it converts a hidden assumption into a visible one: a stakeholder can challenge it, a successor can re-evaluate it against new data, and nobody has to rediscover it the hard way when the number moves. A limitation you wrote down is a limitation you can defend; one you didn't is a surprise waiting for a board meeting.

## 🔗 Continue

[[Lesson 5 - Capstone, Ship It|Lesson 5 — Capstone, Ship It]]

## 🔗 Related Notes

- [[Snowball|Snowball]] — course hub
- [[Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4 — Taming Non-Standard ARR]] — the conventions section 4 documents
- [[Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6 — Testing Your Snowball Like a Data Engineer]] — what section 6 records the guarantees of
- [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Chapter 2, Lesson 8 — Capstone]] — GreenTide Analytics, and the grain-vs-dimension distinction
- [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]] — writing a methodology doc for a real dataset
