[[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script]]'s date cross-check answers one yes/no question: is this claimed churn confirmed by real lifecycle dates, or not? Thornfield's pipeline needs a richer answer, because "gone" isn't one thing in a veterinary business — a pet can stop generating revenue because its owner formally left the practice, because the pet died, or because nobody can say why it just stopped coming in. Those are three different business realities, and a good bridge should tell them apart.

## Behavioral signal vs. event-sourced signal

Lesson 2's `is_fully_lapsed`/`is_partially_lapsed` flags are **behavioral** — inferred purely from the absence of transactions. They answer "did revenue stop," not "why." Thornfield's `dim_client` and `dim_pet` tables carry two **event-sourced** dates that answer the why, when they exist:

- `churn_date` — the client formally left or transferred away, an explicit business event.
- `death_date` — the pet died, an explicit, unambiguous event.

Most lapsed pets have neither date — they just went quiet, and "lapse" is the honest, most specific label available. But when one of these dates *does* exist, it should override the generic behavioral label with the real reason.

## Precedence, and why it's load-bearing

```python
lifecycle_flags = lapse_flags.withColumn(
    "gone_reason",
    sf.expr("""
        CASE
            WHEN (is_fully_lapsed = 1 OR is_partially_lapsed = 1) AND month_roll >= death_month
                THEN 'death'
            WHEN (is_fully_lapsed = 1 OR is_partially_lapsed = 1) AND month_roll >= churn_month
                THEN 'churn'
            WHEN is_fully_lapsed = 1 OR is_partially_lapsed = 1
                THEN 'lapse'
            ELSE NULL
        END
    """),
)
```

This is the exact same discipline as the 8-bucket cascade's `claimed_by` `CASE` chain in [[Bucket Cascade Logic|Bucket Cascade Logic]]: **first match wins, and the ordering encodes a business rule, not an arbitrary choice.** Death is checked before churn, and churn is checked before falling back to lapse, because a pet can technically have both a `churn_date` (its last owner transferred away before it died) and a `death_date` — and the more specific, more final reason should win. Reverse the order and a genuine death could get mislabeled as a mundane churn, which matters operationally: churn might be win-back-able with the right outreach, death is not, and an unexplained lapse needs a human to go find out why.

## Three pets, one quiet month

| Pet | `l12m_transactions` this month | `death_month` | `churn_month` | `gone_reason` |
|---|---|---|---|---|
| Biscuit | 0 | — | — | `lapse` — no event on file, needs investigating |
| Whiskers | 0 | 2024-06 (this month) | — | `death` |
| Max | 0 | — | 2024-06 (this month) | `churn` |

All three pets look identical on the revenue line alone — zero this month, something last month. Only the event-sourced dates tell you what actually happened, and only the precedence order (death checked first) protects a pet like Whiskers from being misfiled as an ordinary churn if it happened to also have a stale `churn_date` on record from an earlier practice transfer.

## What this buys you over a binary confirm/deny

The Contract Dates note's `date_confirmed` flag is binary: a claim is either backed by real dates or it gets demoted. This is a genuine escalation of that idea — instead of confirming or demoting a single claim, real dates actively **reclassify** it into one of three named categories, each of which gets its own signed bucket in Stage 5 (`lapse_revenue`, `churn_revenue`, `death_revenue`). The bridge still reconciles exactly the same way — every dollar lands in exactly one bucket — but now the report itself answers "why," not just "how much."

## 📌 Key Takeaways

- Behavioral signals (L12M/L14M going quiet) tell you revenue stopped; event-sourced dates (`death_date`, `churn_date`) tell you why, when they exist.
- The `CASE` chain checks death before churn before falling back to generic lapse — the same "first match wins, ordering is load-bearing" rule as the 8-bucket cascade, applied one level up: classifying the *reason* something left, not just which bucket the dollars go in.
- This is a richer answer to the same question [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script]]'s date cross-check asks — instead of confirming or demoting one claim, real dates reclassify it into one of several named, separately-bucketed outcomes.

## ✅ Check Your Understanding

**1.** A pet has both a `churn_date` and a later `death_date` on record. Which `gone_reason` does it get, and why does the `CASE` order guarantee that?

**Answer:** `death` — because the `CASE` chain checks `month_roll >= death_month` first, before it ever evaluates the churn condition. As soon as the death condition is true, that arm wins and the churn arm is never reached for that row.

**2.** Why is a plain `lapse` label still useful, rather than trying to force every quiet pet into either `churn` or `death`?

**Answer:** Because most quiet pets genuinely have neither event on file — forcing a label would be guessing. `lapse` honestly represents "revenue stopped and we don't yet know why," which is itself a useful, actionable signal: it's the group that needs a human to investigate, as opposed to `churn`/`death`, where the reason is already known and closed.

## 🔗 Continue

[[Lesson 4 - One Table, Two Periods|Lesson 4 — One Table, Two Periods]]

## 🔗 Related Notes
- [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script]] — the binary date cross-check this lesson extends into a three-way classification.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the "first match wins, ordering is load-bearing" `CASE`-arm discipline this lesson reuses.
- [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — Stage 3 in full.
- [[ARR Bridge Course - Chapter 4|Chapter 4 — Chapter index]]
