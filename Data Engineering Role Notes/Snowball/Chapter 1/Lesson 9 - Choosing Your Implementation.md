There are two complete, working implementations of the 8-stage cascade sitting in this vault. They produce the same buckets from the same data and neither is the "correct" one — they're written in two different styles, and which one belongs in your project depends on where your project lives and how your brain works. This lesson is about making that choice deliberately, before you've sunk two days into the wrong one.

## The two options

**(A) The T-SQL Stored Procedure** — [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]]

Written in an **imperative** style. It builds a stack of `#temp` tables and then works through the eight buckets one at a time, mutating those tables as it goes. Each bucket follows the same four-beat rhythm: reset the bucket column to 0, compute a flag using a grouped CTE, cross-check that flag against the real activity dates, then `UPDATE` the bucket column with the result. Eight buckets, eight passes, executed in order.

This is what SQL looks like in most established enterprise SQL Server codebases. If your company has been running on SQL Server for a decade, this file will look completely at home next to everything else in the repo.

**(B) The ANSI SQL Template** — [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]]

Written in a **declarative** style. No temp tables, no procedure, no session state — one long chain of CTEs that a row flows through from top to bottom, picking up exactly one `claimed_by` label along the way:

```
customer_flags → plan_flags → service_flags → validated_flags → resolved_flags → bucket_amounts
```

It's portable: Snowflake, BigQuery, Postgres, and Databricks all run it with only minor date-function swaps.

## What "imperative vs declarative" actually means here

Those words get thrown around a lot. Here's the version that matters in practice.

**Imperative** = you write a sequence of steps that change state. "Make this column zero. Now compute a flag. Now overwrite the column based on the flag. Now do the next bucket." The correctness of step 6 depends on steps 1 through 5 having already run, in that exact order, against that exact table. The table is a shared, mutating thing that eight different blocks of code take turns writing to.

**Declarative** = you describe relationships between datasets and let the engine figure out execution. `plan_flags` isn't a thing that gets written to and later overwritten; it's a *definition* — "given `customer_flags`, here is what the product-grain view of it looks like." Nothing mutates. There's no ordering you have to remember, because the dependency structure of the CTE chain *is* the ordering.

This has a direct consequence for the cascade's most important property. In version (A), mutual exclusivity is something you **maintain by discipline**: the `WHERE` clause on bucket 5's `UPDATE` has to correctly exclude everything buckets 1 through 4 already claimed, and if someone reorders two `UPDATE` statements during a refactor, the query still runs and still returns numbers — just wrong ones. In version (B), exclusivity is **structural**: a row carries a single `claimed_by` value, and once it's set, later CTEs can't reassign it. You can't accidentally double-claim a row by editing things in the wrong order, because there is no order to get wrong.

## The 11pm debugging test

This is the tradeoff that will actually affect your life, so let's make it concrete.

It's late. The bridge doesn't tie out. Cedar Systems' numbers look wrong and you need to find out which stage mislabeled them.

**With the procedure (A):** you open the file, find the block that populates the bucket you suspect, and… you can't just run that block. It reads from `#temp` tables that only exist mid-execution, populated by everything above it. So you either run the whole procedure and then inspect the temp table afterward — which tells you the *final* state but not what it looked like three UPDATEs ago — or you manually comment out the tail of the procedure to create a breakpoint, run it, look, uncomment, adjust, run again. Each loop is a full re-execution. If the procedure takes four minutes on real data, that's a four-minute loop, and you've now got a modified copy of a production file open with pieces commented out, which is its own hazard.

**With the CTE chain (B):** you scroll to the bottom, and above the final `SELECT` you type:

```sql
SELECT * FROM plan_flags WHERE customer_id = 'CEDAR-001'
```

Run it. Every CTE the engine doesn't need is skipped. You see exactly what `plan_flags` thought about Cedar Systems, in seconds, with nothing edited or commented out. Wrong CTE? Change one word to `service_flags` and run again. You can walk the entire pipeline stage by stage in under a minute, and the file is never in a broken intermediate state.

That difference — "re-run everything and inspect the residue" versus "point at any intermediate stage and look" — is the single biggest practical gap between the two, and it compounds every single time you touch the model.

To be fair to (A): a long CTE chain has real costs too. Some query planners handle a six-deep CTE chain over large tables less gracefully than a sequence of writes to indexed temp tables, and on SQL Server specifically, materializing into `#temp` tables can be *faster* because it gives the optimizer concrete row counts and statistics to work from. Imperative code is also, for many people, simply easier to read linearly: "do this, then this, then this" needs no mental model of dataflow.

## Which one should you pick

**Choose (A), the T-SQL procedure, if:**
- You're working inside an existing SQL Server codebase and want something that drops in with minimal risk. Introducing an unfamiliar style into a mature repo has a real cost your teammates pay.
- Your team is already fluent in temp-table-and-UPDATE patterns and will maintain this after you.
- You've hit measured performance problems with CTE chains on your data volumes and materializing intermediates genuinely helps.
- The stored-procedure shape fits how your orchestration already runs things.

**Choose (B), the ANSI template, if:**
- You're building fresh on a modern cloud warehouse — Snowflake, BigQuery, Databricks, Postgres.
- Portability matters, either because you might migrate or because more than one warehouse is in play.
- You expect to iterate a lot — every debugging cycle is dramatically shorter, and this model *will* need iterating as your bucket definitions get argued over.
- You want mutual exclusivity guaranteed by structure rather than by careful review.
- You personally find "each step is a named dataset built from the previous one" easier to hold in your head than "eight statements that take turns editing one table."

That last point deserves emphasis. This isn't purely a technical decision. You will be reading and re-reading whichever version you choose, often under time pressure. Genuine comprehension beats theoretical elegance every time. If the CTE chain makes your eyes glaze and the procedure reads cleanly to you, take the procedure — a model you understand and can fix beats one you admire and can't.

## A note on what doesn't change

Whichever you pick, the *logic* is identical. Same eight stages, same order, same exclusion semantics, same activity-date cross-checks, same buckets out the other end. Everything you learned in Lesson 8 applies to both files without modification.

That's worth knowing for two reasons. First, you can read one to understand the other — if a stage in the procedure confuses you, find the matching CTE in the template and see if it's clearer there, or vice versa. Second, switching later is a rewrite of form, not of thinking. You're not locked in conceptually. Pick the one that fits today.

## 📌 Key Takeaways

- Two complete implementations of the same 8-stage cascade exist in this vault — an **imperative T-SQL procedure** and a **declarative ANSI CTE chain**. The logic is identical; only the style differs.
- **Imperative** means ordered statements mutating shared temp tables — familiar in enterprise SQL Server codebases, but exclusivity depends on statement order staying correct.
- **Declarative** means a chain of CTE definitions where each row gets one `claimed_by` label — exclusivity becomes a structural property that can't be broken by reordering.
- The biggest practical difference is **debugging**: the procedure requires a full re-run plus temp-table inspection, while the CTE chain lets you `SELECT * FROM plan_flags WHERE customer_id = 'X'` and inspect any stage in seconds.
- Pick **(A)** for an existing SQL Server codebase or a team already fluent in that style; pick **(B)** for a modern cloud warehouse, portability, heavy iteration — or simply because it's the one you understand better.

## ✅ Check Your Understanding

**2 minutes into a refactor, a teammate reorders two of the `UPDATE` statements in the T-SQL procedure. Why is that more dangerous than reordering two CTE definitions in the ANSI template?**

**Answer:** The procedure's exclusion filters assume specific statements have already run. Reordering them means a later bucket's `WHERE` clause no longer excludes what it was written to exclude, so rows get double-claimed — and the query still executes without error, just producing silently wrong numbers. In the CTE chain, ordering is determined by dependencies rather than by position in the file, so a reordering either changes nothing or fails outright rather than quietly corrupting results.

**Your company runs everything on SQL Server and your team has maintained stored procedures for years, but you personally find CTE chains much easier to reason about. Which do you choose?**

**Answer:** There's no single right answer, but the strongest argument is (A) — the code has to be maintained by the team after you, and introducing an unfamiliar style into a mature codebase pushes cost onto everyone else. A reasonable middle path is to prototype in the ANSI style for the fast debugging loop, then port the validated logic into the procedure form for production.

**You're building a new ARR model on Snowflake and expect the bucket definitions to be debated and revised repeatedly over the next quarter. Which implementation, and what's the deciding factor?**

**Answer:** (B), the ANSI template. Modern cloud warehouse plus heavy expected iteration is exactly the case it's built for — the short debugging loop compounds across every revision, and the portable ANSI syntax needs only minor date-function swaps to run on Snowflake.

## 🔗 Continue

**Next:** [[Lesson 10 - Validating, Visualizing, and Avoiding Mistakes|Lesson 10 — Validating, Visualizing, and Avoiding Mistakes]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]]
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]]
