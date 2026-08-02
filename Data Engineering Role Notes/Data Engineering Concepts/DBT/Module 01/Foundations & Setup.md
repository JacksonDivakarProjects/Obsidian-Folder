# **Module 1: Foundations & Setup**

## **1.1 Introduction to dbt (Data Build Tool)**

### **What is dbt?**
dbt (data build tool) is a transformation framework that enables data analysts and engineers to transform data in their warehouses more effectively. It uses SQL for transformations and adds software engineering best practices like version control, testing, documentation, and modularity.

### **Key Characteristics:**
- **SQL-Centric:** Write SELECT statements, dbt handles DDL/DML
- **Jinja-Powered:** Templating language for dynamic SQL
- **Version Control Ready:** All code is plain text files
- **Testing Framework:** Built-in data quality testing
- **Documentation:** Auto-generates documentation from code

## **1.2 dbt Project Structure & Components**

### **Standard Project Structure:**
```
your_project/
│
├── dbt_project.yml          # Main configuration file
├── profiles.yml            # Connection profiles (usually in ~/.dbt/)
│
├── models/                 # SQL models
│   ├── staging/           # Staging models
│   ├── marts/             # Business-facing models
│   └── sources.yml        # Source definitions
│
├── tests/                  # Test files
├── macros/                 # Jinja macros
├── snapshots/             # Type 2 slowly changing dimensions
├── analysis/              # Ad-hoc analysis queries
├── seeds/                 # CSV seed files
└── target/                # Compiled files (generated)
```

### **Core Components:**
1. **Models (.sql files):** SQL transformations
2. **Sources (.yml files):** Table declarations
3. **Tests (.yml/.sql):** Data quality checks
4. **Macros (.sql):** Reusable SQL/Jinja code

## **1.3 Installation & Initial Setup**

### **Installation Steps:**

```bash
# Using pip (Python package manager)
pip install dbt-core

# Install adapter for your database (example: BigQuery)
pip install dbt-bigquery

# Check installation
dbt --version
```

### **Initializing a Project:**

```bash
# Initialize a new dbt project
dbt init my_project

# Navigate to project directory
cd my_project

# Project structure is automatically created
```

### **Connecting to Database:**

**profiles.yml** (located in `~/.dbt/`):
```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: your-gcp-project
      dataset: your_dataset
      keyfile: /path/to/service-account.json
      threads: 4
      timeout_seconds: 300
      
    prod:
      type: bigquery
      method: service-account
      project: your-gcp-project
      dataset: your_prod_dataset
      keyfile: /path/to/service-account.json
      threads: 8
      timeout_seconds: 600
```

### **Basic Commands:**

```bash
# Test connection
dbt debug

# Install dependencies
dbt deps

# Run all models
dbt run

# Run specific model
dbt run --select customers

# Clean compiled files
dbt clean

# Parse project files
dbt parse
```

### **VS Code Setup with dbt Power User:**

1. **Install Extension:** Search for "dbt Power User" in VS Code Extensions
2. **Configure File Associations:**
   - Open Command Palette (Ctrl+Shift+P)
   - Type "Preferences: Open Settings (JSON)"
   - Add these associations:
   ```json
   {
     "files.associations": {
       "*.sql": "jinja-sql",
       "*.yml": "jinja-yaml"
     },
     "[jinja-sql]": {
       "editor.formatOnSave": true
     }
   }
   ```
3. **Features Enabled:**
   - Syntax highlighting for Jinja in SQL/YAML
   - Auto-completion for ref(), source()
   - Model dependency graphs
   - SQL compilation preview

## **Key Files Explained:**

### **dbt_project.yml (Project Configuration):**
```yaml
name: my_project
version: '1.0.0'
config-version: 2

profile: my_project

model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]
analysis-paths: ["analysis"]

models:
  my_project:
    materialized: table
    staging:
      materialized: view
      schema: staging
    marts:
      schema: analytics
```

### **Basic Model Example:**

**models/staging/stg_customers.sql:**
```sql
{{
    config(
        materialized='view',
        schema='staging'
    )
}}

SELECT
    customer_id,
    customer_name,
    email,
    created_at,
    updated_at
FROM {{ source('raw_data', 'customers') }}
WHERE is_active = true
```

## **Summary of Module 1:**
- ✅ Understand dbt's purpose and advantages
- ✅ Know standard project structure
- ✅ Set up dbt with database connection
- ✅ Configure VS Code for optimal development
- ✅ Recognize core configuration files

---

**Ready to proceed to Module 2: Configuration & Jinja Templating?**  
*Type `NEXT` to continue or `REVIEW` to go over any topic again.*

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Syllabus|dbt Learning Syllabus]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 02/Configuration Files|Configuration Files Overview]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 02/File Association & VS Code Setup|File Associations & VS Code Setup]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/Building Models & Materializations|Building Models & Materializations]]
