# **Module 2, Topic 3: File Associations & VS Code Setup**

A proper development environment is crucial for working efficiently with dbt and Jinja. This topic will guide you through configuring **Visual Studio Code (VS Code)** to recognize and enhance your `.sql` and `.yml` files when they contain Jinja code.

## **1. Why This Setup Matters**

Without proper configuration, VS Code treats your dbt SQL files as plain SQL. This means:
*   **No syntax highlighting** for Jinja tags (`{{ ... }}`, `{% ... %}`).
*   **No IntelliSense (autocomplete)** for critical dbt functions like `ref()` and `source()`.
*   **Difficulty navigating** your project's dependency graph.

The **dbt Power User** extension solves all of this by enabling language-aware features for Jinja-SQL and Jinja-YAML files.

## **2. Step-by-Step VS Code Configuration**

### **Step 1: Install the "dbt Power User" Extension**
1.  Open **VS Code**.
2.  Go to the **Extensions** view (Ctrl+Shift+X or Cmd+Shift+X on Mac).
3.  Search for `dbt Power User`.
4.  Click **Install** on the extension by `innoverio`.

### **Step 2: Configure File Associations (The Core Setting)**
This step tells VS Code to treat certain files as "Jinja-SQL" or "Jinja-YAML" instead of plain text.

**Method A: Using the Settings UI (Easier)**
1.  Open VS Code Settings (Ctrl+, or Cmd+, on Mac).
2.  In the search bar, type `files.associations`.
3.  Click "Add Item."
4.  In the "Key" box, enter `*.sql`.
5.  In the "Value" box, enter `jinja-sql`.
6.  Click "Add Item" again.
7.  For the new item, enter `*.yml` as the Key and `jinja-yaml` as the Value.

**Method B: Editing `settings.json` Directly (More Control)**
1.  Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P on Mac).
2.  Type `Preferences: Open Settings (JSON)` and select it.
3.  Add or update the following block in the JSON file:
```json
{
    // ... your other settings ...

    "files.associations": {
        "*.sql": "jinja-sql",
        "*.yml": "jinja-yaml"
    },
}
```

### **Step 3: Recommended Additional Settings**
Add these to your `settings.json` file below the associations for a superior experience. They enable formatting and ensure the extension uses your project's profile.

```json
{
    // ... files.associations and other settings ...

    // Automatically format Jinja-SQL files when you save
    "[jinja-sql]": {
        "editor.formatOnSave": true
    },

    // Tell the dbt Power User extension where your dbt project is
    "dbt.projectSubdirectory": "/path/to/your/dbt/project", // Replace with your actual project path

    // Use the dbt Power User extension for SQL files
    "dbt.enableCodeCompletion": true,
}
```

## **3. What You Gain: Key Features of the dbt Power User Extension**

Once configured, your VS Code will unlock these powerful features:

| Feature | What It Does | Why It's Useful |
| :--- | :--- | :--- |
| **Syntax Highlighting** | Colors Jinja tags, dbt functions, and SQL keywords distinctly. | Instantly visually separates logic (Jinja) from query (SQL). |
| **Autocomplete & IntelliSense** | Suggests model names inside `{{ ref('...') }}` and `{{ source('...') }}`. | Prevents typos, speeds up coding, and helps discover available models. |
| **SQL Compilation** | Preview the raw SQL that dbt will send to the warehouse. | Debug your Jinja logic by seeing the exact output. |
| **Dependency Graph** | Visually see a model's upstream parents and downstream children. | Understand data lineage directly in your editor. |
| **Run/Test Commands** | Execute `dbt run` or `dbt test` on a specific model with a right-click. | No need to switch to the terminal for common commands. |
| **Jump to Definition** | Ctrl+Click (or Cmd+Click) on a `ref('model_name')` to open that model's file. | Fast navigation through complex projects. |

## **4. A Practical Example in Action**

With the extension active, here's how your `models/orders.sql` might look and behave:

```sql
-- The extension provides color coding and tooltips.
-- Hovering over `ref` shows its documentation.
-- Typing `{{ r` triggers a suggestion for `ref`.

{{
    config(
        materialized='table'
    )
}}

SELECT
    o.order_id,
    -- Autocomplete works here: type `{{ c` to see `customer_id`
    c.customer_name,
    -- The extension understands Jinja variables
    {% set status = 'completed' %}
    '{{ status }}' as order_status
FROM {{ ref('stg_orders') }} o -- Ctrl+Click on 'stg_orders' jumps to its file!
LEFT JOIN {{ ref('dim_customers') }} c
    ON o.customer_id = c.customer_id
```

**Right-clicking** on the file in the Explorer now gives you menu options like **"Run dbt models"** and **"Show DAG for this node."**

## **5. Troubleshooting Common Issues**

*   **Extension features aren't working**: Ensure the `dbt.projectSubdirectory` path in your settings is correct. It should be the absolute path to the folder containing your `dbt_project.yml` file.
*   **No syntax highlighting**: Double-check your `files.associations` setting. Restart VS Code after making changes.
*   **Autocomplete doesn't suggest models**: Run `dbt compile` or `dbt parse` in your terminal first. The extension needs dbt to have parsed your project to know what models exist.

---
**Summary:** Installing the **dbt Power User** extension and configuring **file associations** (`*.sql` as `jinja-sql`, `*.yml` as `jinja-yaml`) unlocks syntax highlighting, autocomplete for `ref()`/`source()`, one-click model execution, and visual dependency graphs — a meaningful productivity upgrade over editing dbt projects as plain text.

## 🔗 Related Notes
- [[Foundations & Setup|Module 1: Foundations & Setup]]
- [[Jinja Templating Fundamentals|Jinja Templating Fundamentals]]
- [[Configuration Files|Configuration Files Overview]]
