# DBT

Study notes for dbt (data build tool): the SQL-first transformation framework that adds version control, testing, documentation, and modularity on top of raw warehouse SQL. Start with the [[DBT Syllabus|dbt Learning Syllabus]] for the intended reading order, then use the map below to jump to any topic.

## 🗺️ Map of Content (auto-generated)

### Course roadmap
- [[DBT Syllabus|dbt Learning Syllabus]] — the six-module curriculum these notes follow.

### Module 1 — Foundations & Setup
- [[Foundations & Setup|Module 1: Foundations & Setup]] — what dbt is, standard project structure, installation, `profiles.yml`, and VS Code setup.

### Module 2 — Configuration & Jinja Templating
- [[Configuration Files|Configuration Files Overview]] — `dbt_project.yml`, `profiles.yml`, and source/property YAML files.
- [[Configs and Variables|Configs & the Hierarchy]] — the four ways to configure a model and the precedence rule between them.
- [[File Association & VS Code Setup|File Associations & VS Code Setup]] — configuring the dbt Power User extension for Jinja-aware SQL/YAML editing.
- [[Jinja Templating Fundamentals|Jinja Templating Fundamentals]] — the `{{ }}` / `{% %}` / `{# #}` delimiters and core control flow.
- [[Jinja SQL|Jinja in SQL]] — a deeper, dbt-first guide to macros, filters, whitespace control, and debugging Jinja.
- [[Jinja Data Structures|Jinja Data Structures]] — lists, dicts, tuples, booleans, and why Jinja has no native set literal.
- [[Length in Jinja|Length in Jinja]] — the `length` filter across lists, tuples, dicts, and strings.
- [[Jinja|Jinja (dbt Learn links)]] — bookmark to the official course lesson.

### Module 3 — Models, Materializations & the DAG
- [[Building Models & Materializations|Building Models & Materializations]] — what a model is and the four materializations (view/table/incremental/ephemeral).
- [[The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]] — how `ref()` builds the dependency graph and lineage.
- [[Difference Between Ref and Source Macro|Difference Between ref() and source() Macros]] — when to use each and how they relate to the DAG.

### Module 4 — Testing Framework
- [[Generic Tests & Their Types|Generic Tests & Their Types]] — the four built-in schema tests and how to apply them in YAML.
- [[Singular Tests|Singular Tests]] — custom SQL tests for business rules that generic tests can't express.
- [[Custom Generic Tests|Custom Generic Tests]] — writing your own reusable test macros.
- [[Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]] — selection syntax for tests, `warn` vs `error` severity, and `dbt build`.
- [[Python Models and Tests|dbt with Python: Models and How to Test Them]] — Python models on Snowflake/Databricks/BigQuery, and how they're actually tested (generic/singular/unit tests, not a separate "Python test" feature).
- [[Tests in DBT|Tests in DBT]] — condensed singular vs. generic test reference, including the `ref()`-in-YAML quoting rule.
- [[DBT Tests|DBT Tests (dbt Learn links)]] and [[DBT Generic Test YAML (dbt_utils)|DBT Generic Test YAML (dbt_utils)]] — course bookmark and the `dbt_utils` package hub.

### Module 5 — Snapshots & Node Selection
- [[Snapshots & Change Tracking|Snapshots & Change Tracking]] — Type 2 SCD history via SQL-file or YAML-property snapshots.
- [[dbt Node Selection Syntax|dbt Node Selection Syntax]] — `+`, `@`, tags, `resource_type:`, `state:modified`, and real CI/CD selection patterns.
- [[Snapshots|Snapshots (dbt Learn links)]] — course and docs bookmarks.

### Module 6 — Commands, Flags & Operators
- [[DBT Flags|dbt Flags That Actually Matter]] — `--full-refresh`, `--select`, `--exclude`, `--defer`, `--vars`, `--threads`, `--target`.
- [[Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]] — why `dbt build` is the production default.
- [[Plus Dependency Operator|What `+` Means in dbt Selection]] — a focused walkthrough of the `+` prefix/suffix/both-sides pattern.

### Macros Reference
- [[Var() Macro|var() in dbt]] — defining and reading project variables (`dbt_project.yml`, `--vars`, defaults).
- [[Code Gen Package|Code Gen Package]] — bookmark on the `codegen` package for generating source/staging boilerplate.

### YAML Reference
- [[Types of YAML File|Types of YAML File]] — `dbt_project.yml`, `profiles.yml`, `models.yml`, `sources.yml` and what each controls.
- [[YAML File and Its Structure|YAML File and Its Structure]] — YAML as a data-only format: key-value pairs, lists, nesting.
- [[Dash in YAML|Dash in YAML]] — the `-` that distinguishes a list item from a key-value pair, and the most common dbt YAML bug.
- [[Documentation in YAML|Documentation in YAML]] — inline `description:` strings vs. reusable `{% docs %}` blocks.
- [[Sources YAML File|Sources YAML File (dbt Learn links)]] and [[Source Freshness|Source Freshness (dbt Learn links)]] — course bookmarks on declaring sources and freshness checks.

- [[YAML File Purpose|YAML File Purpose (Images)]] — study screenshots on why dbt uses separate YAML files (config, testing, documentation).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]] — comparable change-tracking concept on the storage-layer side, referenced from Snapshots & Change Tracking.
