# DBT

Study notes for dbt (data build tool): the SQL-first transformation framework that adds version control, testing, documentation, and modularity on top of raw warehouse SQL. Start with the [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Syllabus|dbt Learning Syllabus]] for the intended reading order, then use the map below to jump to any topic.

## 🗺️ Map of Content (auto-generated)

### Course roadmap
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Syllabus|dbt Learning Syllabus]] — the six-module curriculum these notes follow.

### Module 1 — Foundations & Setup
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 01/Foundations & Setup|Module 1: Foundations & Setup]] — what dbt is, standard project structure, installation, `profiles.yml`, and VS Code setup.

### Module 2 — Configuration & Jinja Templating
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 02/Configuration Files|Configuration Files Overview]] — `dbt_project.yml`, `profiles.yml`, and source/property YAML files.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 02/Configs and Variables|Configs & the Hierarchy]] — the four ways to configure a model and the precedence rule between them.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 02/File Association & VS Code Setup|File Associations & VS Code Setup]] — configuring the dbt Power User extension for Jinja-aware SQL/YAML editing.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja Templating Fundamentals|Jinja Templating Fundamentals]] — the `{{ }}` / `{% %}` / `{# #}` delimiters and core control flow.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja SQL|Jinja in SQL]] — a deeper, dbt-first guide to macros, filters, whitespace control, and debugging Jinja.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja Data Structures|Jinja Data Structures]] — lists, dicts, tuples, booleans, and why Jinja has no native set literal.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Length in Jinja|Length in Jinja]] — the `length` filter across lists, tuples, dicts, and strings.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/Jinja|Jinja (dbt Learn links)]] — bookmark to the official course lesson.

### Module 3 — Models, Materializations & the DAG
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/Building Models & Materializations|Building Models & Materializations]] — what a model is and the four materializations (view/table/incremental/ephemeral).
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]] — how `ref()` builds the dependency graph and lineage.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/ref() and source() Macros/Difference Between Ref and Source Macro|Difference Between ref() and source() Macros]] — when to use each and how they relate to the DAG.

### Module 4 — Testing Framework
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]] — the four built-in schema tests and how to apply them in YAML.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Singular Tests|Singular Tests]] — custom SQL tests for business rules that generic tests can't express.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Custom Generic Tests|Custom Generic Tests]] — writing your own reusable test macros.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]] — selection syntax for tests, `warn` vs `error` severity, and `dbt build`.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Python Models and Tests|dbt with Python: Models and How to Test Them]] — Python models on Snowflake/Databricks/BigQuery, and how they're actually tested (generic/singular/unit tests, not a separate "Python test" feature).
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Tests In DBT/Tests in DBT|Tests in DBT]] — condensed singular vs. generic test reference, including the `ref()`-in-YAML quoting rule.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/DBT Tests|DBT Tests (dbt Learn links)]] and [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/DBT Generic Test YAML (dbt_utils)|DBT Generic Test YAML (dbt_utils)]] — course bookmark and the `dbt_utils` package hub.

### Module 5 — Snapshots & Node Selection
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/Snapshots & Change Tracking|Snapshots & Change Tracking]] — Type 2 SCD history via SQL-file or YAML-property snapshots.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/dbt Node Selection Syntax|dbt Node Selection Syntax]] — `+`, `@`, tags, `resource_type:`, `state:modified`, and real CI/CD selection patterns.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/Snapshots|Snapshots (dbt Learn links)]] — course and docs bookmarks.

### Module 6 — Commands, Flags & Operators
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]] — `--full-refresh`, `--select`, `--exclude`, `--defer`, `--vars`, `--threads`, `--target`.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]] — why `dbt build` is the production default.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Plus Dependency Operator|What `+` Means in dbt Selection]] — a focused walkthrough of the `+` prefix/suffix/both-sides pattern.

### Macros Reference
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/var() Macro/Var() Macro|var() in dbt]] — defining and reading project variables (`dbt_project.yml`, `--vars`, defaults).
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/Code Gen Package|Code Gen Package]] — bookmark on the `codegen` package for generating source/staging boilerplate.

### YAML Reference
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/Types of YAML File|Types of YAML File]] — `dbt_project.yml`, `profiles.yml`, `models.yml`, `sources.yml` and what each controls.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/YAML File and Its Structure|YAML File and Its Structure]] — YAML as a data-only format: key-value pairs, lists, nesting.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/Dash in YAML|Dash in YAML]] — the `-` that distinguishes a list item from a key-value pair, and the most common dbt YAML bug.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Documentation/Documentation in YAML|Documentation in YAML]] — inline `description:` strings vs. reusable `{% docs %}` blocks.
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/Sources YAML File|Sources YAML File (dbt Learn links)]] and [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/DBT Topic Links/Source Freshness|Source Freshness (dbt Learn links)]] — course bookmarks on declaring sources and freshness checks.

- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Images/YAML File Purpose/YAML File Purpose|YAML File Purpose (Images)]] — study screenshots on why dbt uses separate YAML files (config, testing, documentation).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]] — comparable change-tracking concept on the storage-layer side, referenced from Snapshots & Change Tracking.
