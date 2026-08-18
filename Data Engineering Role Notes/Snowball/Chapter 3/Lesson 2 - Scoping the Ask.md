You now have six flagged issues in Corvid Systems' data and no idea what to do with any of them — and that's the correct state to be in. The next move is not more SQL. It's a conversation. Most bridges that get rebuilt from scratch aren't rebuilt because the SQL was wrong; they're rebuilt because the engineer answered a question nobody asked and skipped three that mattered. Scoping is a distinct skill from modeling, it has its own checklist, and this lesson treats it that way.

---

## The brief you didn't get

Chapter 2's capstone handed you a design brief for GreenTide Analytics: grain, metrics, refresh cadence, tolerances, deliverable — all specified up front. That was a deliberate simplification so you could focus on architecture. In the real version of that engagement, **somebody had to produce that brief**, and that somebody is usually you. See [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Chapter 2, Lesson 8 — Capstone]] for what the finished artifact looks like; this lesson is about how you get there from "can you build us an ARR bridge by end of quarter."

The mental shift: **a vague ask is not a request for you to use judgment. It's an unfinished requirement.** Stakeholders leave things unstated not because they don't care but because the answers are so obvious inside their heads that it doesn't occur to them the question exists. Your job is to make those questions visible cheaply, before they become rework.

---

## The six question families

### 1. Grain — what are the rows?

Company-level total only? Split by product, region, segment, sales channel? By customer, so anyone can drill in?

This is the single most expensive question to get wrong, because grain drives everything downstream — the join fan-out, whether the multi-grain cascade from Chapter 1 is needed at all, and how many of your profiling flags actually matter. Ask it first, and ask it concretely: *"When you look at this, is it one number per quarter, or one row per segment per quarter?"*

### 2. Metric scope — which numbers, over what window?

LTM, YTD, quarter-over-quarter, or several? Dollar-based NRR/GRR, logo retention, or both? Is Quick Ratio wanted? Are expansion and contraction reported separately or netted?

Every additional window is not just another column — it's another tie-out, another set of edge cases at the period boundary, and another thing to explain when it moves.

### 3. Definition of done — what artifact are you handing over?

A table in the warehouse someone else queries? A live dashboard? A one-time deck for a board meeting? A CSV emailed to the CFO?

These have wildly different engineering costs and wildly different quality bars. A one-time deck tolerates a manual step; a live dashboard does not. Ask explicitly: *"What does this look like when it's finished and you're happy?"*

### 4. Cadence and ownership — once, or forever?

One-time analysis or an ongoing pipeline? If ongoing, at what frequency, and who gets paged when it breaks? Does it need to survive you changing teams?

An engineer who builds a production pipeline for a one-time question has wasted weeks. An engineer who builds a one-time script for a quarterly board metric has created a maintenance liability that will outlive their tenure.

### 5. Judgment tolerance — who owns the conventions?

This is where your profiling log earns its keep. For each flagged issue: does finance want to be **consulted** on the convention, or do they want you to pick a **defensible default** and document it?

Also establish a **materiality threshold**. "Anything under $2,000 of ARR impact, use your judgment and note it; anything above, come ask me" converts an open-ended stream of interruptions into a clean decision rule.

### 6. Deadline, sequencing, and sign-off

What's the real date, and what's it tied to — a board meeting, an audit, a fundraise, or someone's curiosity? Which number does yours have to agree with, and who has authority to say it's right?

The tie-out question is the one engineers forget most often. If the CFO already has an ARR number in a spreadsheet, your bridge has to reconcile to it or explain the delta — and you want to know that *before* you build, not during the review.

---

## From profiling flags to scoping questions

Every flag from the last lesson converts into a specific question. Don't present the list as problems; present it as decisions that need an owner.

| Flag | The scoping question it becomes |
|---|---|
| Coral Bay — usage pricing | "How do you want usage accounts represented in ARR — annualize the latest month, average a trailing window, or report them separately from the subscription base?" |
| Driftwood — multi-year TCV | "For multi-year deals billed at signing, is ARR the total divided by term years, or do you recognize it some other way?" |
| Elmsworth — prorated first invoice | "When a first invoice is a partial-period stub, do we take the contract's stated annual rate as ARR from day one?" |
| Fenwick — duplicate identity | "Billing and CRM each have a record for Fenwick with different IDs and spellings. Can you confirm that's one account? And who owns fixing the crosswalk?" |
| Harlow — sentinel end date | *(Usually no stakeholder question — an engineering convention, handled in code.)* |
| Ivywood — late-arriving invoice | "When data arrives after a quarter closes and it changes a prior-period number, do we restate the published bridge or hold the number as reported?" |

Note the last row. Restatement policy is a finance-governance decision with audit implications, and it is never yours to make unilaterally.

---

## The conversation

Rowan Deitch is Corvid's VP Finance. The engineer has the profiling log open. Fifteen minutes.

> **Engineer:** Before I build anything — when you picture the finished output, is it one ARR bridge for the whole company, or does it break down by product line or segment?
>
> **Rowan:** Company-level for now. The board deck has one waterfall on one slide. I know sales will eventually want it by segment, but that's not this quarter's problem.
>
> **Engineer:** Good, that simplifies things a lot. Second — what window? Last twelve months, year-to-date, or both?
>
> **Rowan:** LTM. YTD in Q1 is a meaningless number and I've stopped putting it in front of the board.
>
> **Engineer:** Understood. Now the interesting part. I profiled the two exports and found six accounts where ARR isn't a straight read off the contract. The one I want your call on: Coral Bay Legal is on usage-based pricing — there's no annual value in the contract at all, just monthly invoices, and they bounce around. February was $1,850, May was $2,100. Whatever I annualize, that account will move quarter to quarter for reasons that have nothing to do with retention.
>
> **Rowan:** Then keep it out of the headline number. Show the subscription base as the waterfall, and put usage on its own line underneath. I don't want the board asking why expansion moved when it was just someone e-signing more contracts in May.
>
> **Engineer:** That's helpful — it means the annualization method won't drive your top-line at all. For the other five — a multi-year deal billed as a lump sum, a prorated first invoice, a duplicate customer record across billing and CRM, a date convention issue, and one invoice that landed in the warehouse after quarter close — do you want to review each one, or should I pick a defensible convention and document it?
>
> **Rowan:** Pick something sensible and write it down. If any single one of them swings ARR by more than a couple thousand dollars, flag it to me before you publish. The duplicate customer one — send me the two names, I'll confirm with our billing admin whether it's the same account.
>
> **Engineer:** Will do. Last two: what does "done" look like, and when do you need it?
>
> **Rowan:** Done is a table I can pull from plus a summary I can paste into the deck. Board meeting is in three weeks. And it has to tie to the ARR figure in my Q1 close file — if it doesn't, I need to understand why before the meeting, not during it.
>
> **Engineer:** One more that I should have asked earlier — is this a one-time build for this board meeting, or do you want it running every quarter?
>
> **Rowan:** Every quarter, eventually. But get me this quarter first. I'd rather have something right in three weeks than something automated in three months.

Fifteen minutes, and the build just changed shape considerably.

---

## What those answers actually bought

- **Company-level only** — no product/region dimension, no segment cascade. The multi-grain machinery from Chapter 1 isn't needed here, which removes a large chunk of the build.
- **LTM only** — one window to tie out, not two. The YTD derivation from Chapter 2 stays on the shelf.
- **Coral Bay reported separately** — the usage-annualization question drops from "blocking policy decision" to "presentation choice on a supplementary line." This is the clearest example in the chapter of scoping *dissolving* a technical problem rather than answering it.
- **Defensible defaults with a materiality escalation** — you can proceed on Driftwood, Elmsworth, Harlow, and Ivywood without waiting on anyone, as long as you document each convention and flag anything above the threshold. That converts four blockers into four documented decisions.
- **Fenwick escalated to the data owner** — identity resolution is being confirmed by a human with authority, not guessed at with a fuzzy string match. You still implement the merge; you just aren't the one asserting it's the same company.
- **Table + summary, tie to the Q1 close file, three weeks, quarterly later** — this defines the delivery artifact (Lesson 3), makes the tie-out target explicit rather than discovered late (Chapter 1, Lesson 9's discipline), and tells you to build for correctness now and automate second.

Every one of those constraints will show up in [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]], where this dataset gets built end to end.

---

## Write it up

A scoping conversation that lives only in your memory hasn't happened. Convert it to a short written brief and send it back to the stakeholder with a "does this match what you meant?" — the read-back catches misunderstandings while they're still free, and it gives you something to point at when the ask changes in week two.

The brief should be roughly one page, covering: the question being answered, grain, metrics and windows, the deliverable, cadence, every convention decision with its rationale, open items with owners and due dates, and the tie-out target. That's precisely the structure of the GreenTide design brief in [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Chapter 2, Lesson 8 — Capstone]] — reread it now with fresh eyes and notice that every section of it is the frozen output of a question somebody had to ask.

---

## Reusable scoping checklist

Take this into the room. You will not need all of it every time, but you will regret skipping the ones you skipped.

```markdown
## ARR Bridge — Scoping Checklist

### Purpose
- [ ] What decision does this number inform? Who reads it?
- [ ] Is there an existing number this must agree with? Whose is it?

### Grain
- [ ] Company-level total, or split by product / region / segment / channel?
- [ ] Customer-level detail needed for drill-down, or aggregates only?
- [ ] Contract-grain or customer-grain in the source? (from profiling)

### Metrics & windows
- [ ] LTM, YTD, QoQ — which, and are multiple required?
- [ ] NRR / GRR / logo retention / Quick Ratio — which are in scope?
- [ ] Expansion and contraction reported separately, or netted?
- [ ] Currency, and is FX conversion in scope?

### Deliverable
- [ ] Warehouse table / dashboard / deck / CSV — which, exactly?
- [ ] Who consumes it, and in what tool?
- [ ] Is a tie-out summary or reconciliation view required alongside?

### Cadence & ownership
- [ ] One-time or recurring? At what frequency?
- [ ] Who owns it after handoff? Who gets alerted on failure?
- [ ] Does history need to be preserved as-published, or recomputed each run?

### Judgment & tolerance
- [ ] For each profiling flag: consult, or defensible default + documentation?
- [ ] Materiality threshold for escalation ($ or % of ARR)?
- [ ] Restatement policy: do prior published periods get corrected or frozen?
- [ ] Who confirms customer identity questions?

### Timeline
- [ ] Hard deadline, and what is it tied to?
- [ ] What's the minimum acceptable v1 if the timeline compresses?
- [ ] Who signs off that the number is right?
```

---

## 📌 Key Takeaways

- Scoping is its own discipline with its own output — a written brief — and skipping it produces bridges that are technically correct and functionally wrong.
- A vague ask is an unfinished requirement, not an invitation to use judgment. Stakeholders omit things that are obvious to them, not things they don't care about.
- Six question families cover almost everything: grain, metrics/windows, definition of done, cadence and ownership, judgment tolerance, and deadline/tie-out/sign-off.
- Every profiling flag converts into a specific stakeholder question with a named owner. Ask which ones need consultation and which need only a documented default — a materiality threshold turns an open stream of interruptions into a decision rule.
- Scoping sometimes **dissolves** a technical problem instead of answering it: once Corvid's finance lead put usage accounts on a separate line, the Coral Bay annualization question stopped affecting the headline number at all.
- Ask for the tie-out target up front. Discovering during review that your bridge has to reconcile to someone's existing spreadsheet is the most avoidable form of rework in this entire course.

---

## ✅ Check Your Understanding

**1.** In the conversation, Rowan's answer about Coral Bay didn't tell the engineer *how* to annualize usage revenue. Why was it still the most valuable answer in the exchange?

**Answer:** Because it changed which problems were load-bearing. By putting usage accounts on a separate supplementary line rather than blending them into the subscription waterfall, the decision removed the annualization convention from the critical path — whatever method gets chosen, it no longer moves the headline ARR, the expansion bucket, or NRR. A question that looked like it required a finance policy ruling turned out to require a presentation choice instead. That's the pattern to watch for: scoping frequently makes technical problems smaller or irrelevant rather than solving them, which is why doing it before the build saves more time than doing it well during the build.

**2.** Corvid's finance lead said "pick something sensible and write it down" for five of the six flags. What obligations does that answer create for you, and what would misusing it look like?

**Answer:** It delegates the *choice* but not the *transparency*. You now owe a documented convention for each flag — stated in the brief and ideally in the model's comments or a data dictionary — with enough rationale that someone can disagree with it later on purpose rather than discover it by accident. It also came with a materiality threshold, so anything swinging ARR by more than a couple thousand dollars still escalates before publication. Misusing it looks like burying a `CASE WHEN contract_type = 'multiyear' THEN amount / 2` in a CTE with no comment and no mention in the writeup — technically within the delegation, but it converts a reviewable business decision into invisible engineering trivia that nobody can audit.

**3.** Chapter 2's GreenTide capstone handed you a complete design brief. Why does this chapter make you produce one instead, and what changes about the work?

**Answer:** GreenTide's brief was given so the exercise could focus purely on architecture — the requirements were treated as settled inputs. In real engagements nobody hands you that document; the ask arrives as a sentence in a chat message, and the brief is an artifact you create by interrogating stakeholders and then writing their answers down. What changes is that requirements become a thing you are accountable for eliciting and read-back-confirming, not a thing you receive. Practically, it means the first deliverable of any bridge project is a one-page written brief, not a query — and that brief is what protects you when the ask shifts mid-build, because you can point to what was agreed and scope the change explicitly.

---

## 🔗 Continue

[[Lesson 3 - Building the Delivery Artifact|Lesson 3 — Building the Delivery Artifact]]

---

## 🔗 Related Notes

- [[Snowball|Snowball]] — course hub
- [[Lesson 1 - Profiling a Stranger's Dataset|Chapter 3, Lesson 1 — Profiling a Stranger's Dataset]] — where the six Corvid flags come from
- [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Chapter 2, Lesson 8 — Capstone]] — a completed design brief, i.e. the written output of a scoping conversation like this one
- [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]] — where these scoping decisions get built
