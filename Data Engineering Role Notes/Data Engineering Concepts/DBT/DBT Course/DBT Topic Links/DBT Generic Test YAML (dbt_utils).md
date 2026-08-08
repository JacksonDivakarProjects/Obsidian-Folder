

dbt_utils package page on dbt Hub: https://hub.getdbt.com/dbt-labs/dbt_utils/latest/

`dbt_utils` (dbt Labs) is the standard library most dbt projects install — it adds reusable generic tests (`equal_rowcount`, `not_constant`, `unique_combination_of_columns`, `at_least_one`) and macros (`surrogate_key`, `date_spine`, `pivot`) on top of the four built-in tests covered in [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]. Reference its tests in YAML as `dbt_utils.<test_name>` after adding it to `packages.yml` and running `dbt deps`.
