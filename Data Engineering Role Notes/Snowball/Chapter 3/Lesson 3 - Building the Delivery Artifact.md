A correct bridge that nobody can read is not a finished piece of work. At some point the query stops being the deliverable and something else becomes the deliverable — a chart in a deck, a tab in a dashboard, a one-page summary that a CFO skims in ninety seconds before a board call. This lesson is about that handoff shape. You already know what a waterfall chart *is*; what you probably do not know is that almost no tool will build one for you from a bucket table, and the trick that makes it work everywhere is the same trick in every tool.

## Why the waterfall is harder to build than it looks

[[Lesson 10 - Validating, Visualizing, and Avoiding Mistakes|Chapter 1, Lesson 10]] introduced the concept: solid anchor bars at each end for BOP and EOP, floating bars in between for each bucket, red for the things that took ARR away, green or blue for the things that added it. Conceptually obvious. Then you open Excel, or Google Sheets, or Tableau, and go looking for the chart type that accepts a table like this:

| bucket | value |
|---|---|
| BOP | 57,000 |
| New | 8,000 |
| Expansion | 6,000 |
| Contraction | -6,000 |
| Churn | -10,000 |
| Reactivation | 5,000 |
| EOP | 60,000 |

and there usually isn't one. Some tools have a bespoke waterfall visual with its own opinions about which bars are totals and which are deltas. Some have nothing native at all. Plot that table as a plain column chart and you get seven bars all growing up from zero, two of them pointing down — which communicates nothing, because the whole point of a waterfall is that each bar *starts where the previous one ended*.

The fix is a single mechanic that predates every tool that automates it, and it works in all of them.

## The invisible base bar

A floating bar is just a stacked bar where the bottom segment is invisible.

For every bar position you plot **two stacked series**:

1. **`invisible_base`** — a segment whose height is the distance from zero up to where the visible bar should *start*. Its fill is set to transparent / "no fill" / none. It occupies vertical space and then disappears.
2. **`visible_delta`** — a segment stacked directly on top of the base, whose height is the magnitude of that bucket's movement. This is the bar the reader actually sees, and this is the series you colour red or green.

That's it. The floating effect is an illusion produced by a stacked column chart with its lower half painted the same colour as the background — or, better, with no fill at all so it survives a theme change.

Two rules govern the base value:

- **Anchor bars (BOP, EOP):** base = 0, visible = the full ARR value. These are totals, not deltas — they sit on the floor.
- **Gain buckets (New, Expansion, Reactivation):** base = the running total *before* this bucket. The bar grows upward from where the running total already stood.
- **Loss buckets (Contraction, Churn):** base = the running total *after* this bucket, i.e. the running total minus the magnitude of the loss. The bar hangs downward from the old level to the new one, so its bottom edge is the new running total and its top edge is the old one.

That last rule is the one people get wrong. A loss bar's base is the *lower* of the two numbers it spans, because stacking always builds upward from zero — you cannot draw downward, you can only start lower.

## Walking Nimbus through it

Take the Q1→Q2 2026 bridge you know cold. Running total starts at zero, the BOP anchor establishes $57,000, and every subsequent bar advances a single running-total variable.

| # | Bar | Movement | Running total before | `invisible_base` | `visible_delta` | Running total after |
|---|---|---|---|---|---|---|
| 1 | BOP | anchor | — | **0** | **57,000** | 57,000 |
| 2 | New | +8,000 | 57,000 | **57,000** | **8,000** | 65,000 |
| 3 | Expansion | +6,000 | 65,000 | **65,000** | **6,000** | 71,000 |
| 4 | Contraction | −6,000 | 71,000 | **65,000** | **6,000** | 65,000 |
| 5 | Churn | −10,000 | 65,000 | **55,000** | **10,000** | 55,000 |
| 6 | Reactivation | +5,000 | 55,000 | **55,000** | **5,000** | 60,000 |
| 7 | EOP | anchor | — | **0** | **60,000** | 60,000 |

Read row 4 slowly, because it is the shape of every loss bar you will ever plot. The running total coming in is $71,000. Contraction removes $6,000. The bar must span from $71,000 down to $65,000, so the invisible base is $65,000 and the visible red segment is $6,000 tall, sitting on top of it. The bar's *top* lands at $71,000 — exactly where the Expansion bar ended — and its *bottom* lands at $65,000, exactly where the Churn bar will begin. Same logic for Churn: base $55,000, visible $10,000, spanning $65,000 down to $55,000.

Note two properties worth checking every time you build one:

- **`visible_delta` is always positive.** You feed the chart the magnitude, never the signed value. The direction is communicated by where the bar sits and what colour it is, not by a negative number.
- **The final running total must equal the EOP anchor.** Row 6 ends at $60,000 and row 7 plots $60,000 from a base of zero. If those two disagree, your bridge does not tie out and the chart is the least of your problems — go back to the arithmetic before you go back to the formatting.

In a spreadsheet, this is two columns next to your bucket table. If your bucket values live in column B with signs intact, the base for row *n* is a running expression over the rows above it, and the delta is `ABS(B_n)`. Then select the three columns — label, base, delta — and insert a stacked column chart.

## What that looks like in the tool you actually have

The mechanic above is the thing to learn, because it transfers. The tool-specific parts are shortcuts over it.

- **Excel / Google Sheets, manual:** stacked column chart on `label | invisible_base | visible_delta`. Click the base series, set fill to "No fill". Optionally set its border to none as well, since some themes outline series. Then colour `visible_delta` by point — this is the step people forget: the deltas are one series, so you must recolour individual data points (red for Contraction and Churn, green for the gains, a neutral grey or navy for the two anchors) rather than the series as a whole.
- **Excel 2016 and later, native:** there is a built-in **Waterfall** chart type that does the base arithmetic for you. Feed it the *signed* bucket values — including the negatives — and then explicitly mark BOP and EOP as totals (right-click the point → "Set as Total"). Skip that step and Excel treats your anchors as deltas and the chart runs off the top of the axis. Convenient, but it hides the mechanic, which is why it is worth building one by hand first.
- **Power BI:** a native **Waterfall** visual. Category on the axis, signed value in the Y field, and a breakdown field if you want it to decompose automatically. Its default behaviour is to compute a total for you rather than accept your BOP and EOP as bars, so you will usually feed it the five deltas and show BOP/EOP as separate cards or as explicit rows depending on how much you want to fight the visual's opinions.
- **Tableau:** no waterfall primitive. The idiomatic build is a Gantt bar chart driven by a running-sum calculated field — which is the same invisible-base idea expressed differently: the running total positions the mark, and a size calculation gives it height. The stacked-bar version with a transparent base works identically if you prefer it.
- **Looker / other BI layers:** almost always the stacked-bar technique, with the base computed in the model rather than the visualization layer. Compute it in SQL, expose `invisible_base` and `visible_delta` as fields, and let the chart be dumb. This is generally the most maintainable option: the arithmetic lives somewhere testable instead of inside a chart config that nobody diffs.

If you take one thing from the tool list, take this: compute the base in the data layer whenever you can. A transparent series is a formatting choice that a well-meaning colleague can undo by applying a theme. A base column in a query is not.

## Shaping the table for the consumer

The chart is one artifact. The table underneath it is another, and the correct shape depends entirely on who is consuming it.

**Wide format** — one row per period, one column per bucket:

| period | BOP | New | Expansion | Contraction | Churn | Reactivation | EOP |
|---|---|---|---|---|---|---|---|
| 2026-Q2 | 57,000 | 8,000 | 6,000 | -6,000 | -10,000 | 5,000 | 60,000 |

This is what a human reads. It is what belongs in a deck, in an email, in an exec summary, and in any spreadsheet where someone will eyeball whether the row adds up. It also makes the tie-out visually checkable in one line, which matters more than it sounds.

**Long / tidy format** — one row per bucket per period:

| period | bucket | value |
|---|---|---|
| 2026-Q2 | BOP | 57,000 |
| 2026-Q2 | New | 8,000 |
| 2026-Q2 | Expansion | 6,000 |
| … | … | … |

This is what a BI tool wants. Adding a period means adding rows, not columns, so nothing in the data model breaks when the next quarter lands. Filters, colour-by-bucket encodings, and the bucket ordering field all attach cleanly. Every BI tool in the list above is happier with long data, and every human is happier with wide data.

Build long, pivot to wide at the last moment. Doing it the other way around — storing wide and unpivoting for the dashboard — means a schema change every single period, and it is the most common reason a snowball dashboard quietly stops updating.

One thing the long table needs that the wide one gets for free: an explicit **sort order column**. Alphabetical bucket ordering puts Churn before New before Reactivation, which produces a waterfall that is arithmetically valid and completely unreadable. Ship `bucket_order` as an integer alongside `bucket`, and set BOP = 1 through EOP = 7.

## The executive summary one-pager

For most audiences, the highest-value artifact is not the dashboard. It is one page. A structure that holds up:

1. **Headline number and its direction.** "Q2 2026 ending ARR: $60,000, up $3,000 (+5.3%) from Q1." One line, at the top, unambiguous.
2. **The waterfall chart.** Directly under the headline, because the headline raises the question "from what?" and the chart is the answer.
3. **The two or three largest individual movements, by name and dollar amount.** Not "churn was elevated" — *"Echo Retail churned entirely (−$10,000), the single largest movement in the quarter. Bramble Inc landed as new business (+$8,000). Delta Tech contracted (−$6,000)."* Named customers are what turn a chart into a conversation, and they are the thing an exec will actually follow up on.
4. **NRR, GRR, and Quick Ratio, each with its convention stated.** For Nimbus: NRR 82.5%, GRR 71.9%, Quick Ratio 0.875 — with a note that the Quick Ratio here uses the New + Expansion over Contraction + Churn convention, excluding Reactivation from the numerator. State that even though it feels pedantic. Especially because it feels pedantic.
5. **One line of interpretation.** The Nimbus story is that ARR rose while retention deteriorated: $3,000 of net growth sitting on top of an NRR under 100% means the base is shrinking and new logos are papering over it. If you leave the reader to derive that from three ratios, half of them won't.

Notice what is not on the page: the SQL, the row counts, the list of every customer. The one-pager is a summary with a path to the detail, not the detail.

## Labels belong on the artifact, not in a doc

This course has hammered one point from Chapter 1 onward, and it lands hardest here, at the moment the work leaves your hands. Every ambiguous convention you resolved needs to be *printed on the thing itself*:

- **LTM or YTD**, and if YTD, what the BOP anchor is.
- **Which Quick Ratio convention** — whether Reactivation counts in the numerator, whether Contraction counts in the denominator.
- **Which ARR normalization rules were applied** — how usage-based contracts were annualized, how multi-year deals were spread, how mid-period prorations were handled.
- **The period grain and the as-of date** the data was pulled.

A footnote in eight-point type at the bottom of the chart is sufficient. What is *not* sufficient is a separate methodology document that the artifact links to but nobody opens — and yet you should write that document anyway, because the footnote is the summary and the document is the source. That is the next lesson.

The rule of thumb: a chart that gets screenshotted into Slack should still be self-describing after it has been separated from every piece of context you attached to it. It will be. Every chart you have ever built has been.

## 📌 Key Takeaways

- Almost no tool has a waterfall primitive that accepts a bucket table directly. The universal technique is a **stacked column chart with an invisible base series**: `invisible_base` (transparent) plus `visible_delta` (coloured) per bar.
- **Anchor bars** get base = 0 and the full value. **Gain bars** get base = the running total *before* the movement. **Loss bars** get base = the running total *after* the movement, so the bar hangs from the old level down to the new one. `visible_delta` is always a positive magnitude.
- Nimbus walks 0 → 57,000 → 65,000 → 71,000 → 65,000 → 55,000 → 60,000, and the final running total must equal the EOP anchor or the bridge does not tie out.
- Store data **long** (one row per bucket per period, with an explicit `bucket_order`) for BI tools; pivot to **wide** (one column per bucket) at the last moment for humans, decks, and exec summaries.
- The executive one-pager is headline → chart → named largest movements → NRR/GRR/Quick Ratio with conventions labeled → one line of interpretation. Convention labels go **on the artifact**, because artifacts get screenshotted away from their context.

## ✅ Check Your Understanding

**1. Nimbus's Contraction bar is −$6,000 and the running total coming into it is $71,000. What are the `invisible_base` and `visible_delta` values, and why isn't the base $71,000?**

**Answer:** `invisible_base` = $65,000 and `visible_delta` = $6,000. Stacked bars can only build upward from zero, so a loss bar has to *start* at the lower of the two levels it spans — the running total after the loss ($65,000) — and be $6,000 tall, putting its top edge at $71,000 where the previous bar ended. Setting the base to $71,000 would draw a bar from $71,000 up to $77,000, which is the opposite of what happened.

**2. You're publishing the bridge to a BI dashboard that will accumulate a new quarter every three months. Should the underlying table be wide or long, and what breaks if you choose wrong?**

**Answer:** Long — one row per bucket per period. Adding a quarter then adds rows, which every downstream chart, filter, and colour encoding absorbs automatically. If you store wide (one column per bucket) the shape is fine for a single period, but a growing dataset in wide format means the *columns* change identity as you extend the model, and any per-bucket encoding has to be rebuilt by hand. Store long, pivot to wide only for the human-facing summary — and ship a `bucket_order` integer so BOP through EOP don't get sorted alphabetically.

**3. Your one-pager reports Quick Ratio 0.875. What must appear alongside it, and why does it matter for this specific number?**

**Answer:** The convention — that this is (New + Expansion) ÷ (Contraction + Churn), with Reactivation excluded from the numerator. It matters concretely here because Nimbus had $5,000 of Reactivation from Foxglove Ltd. Counting it in the numerator gives 19,000 ÷ 16,000 = 1.19, which reads as a healthy company. Excluding it gives 0.875, which reads as a company losing ground. Same bridge, same data, opposite conclusion — and the only thing separating them is a convention that has to be stated on the artifact.

## 🔗 Continue

[[Lesson 4 - Documentation and Handoff|Lesson 4 — Documentation and Handoff]]

## 🔗 Related Notes

- [[Snowball|Snowball]] — course hub
- [[Lesson 10 - Validating, Visualizing, and Avoiding Mistakes|Chapter 1, Lesson 10 — Validating, Visualizing, and Avoiding Mistakes]] — where the waterfall concept was introduced
- [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]] — building the delivery artifact against a real messy dataset
