
```python
stock_analyzer/
├── .env.example
├── requirements.txt
├── README.md
│
├── shared/                                 # tiny, stable utilities
│   ├── __init__.py
│   ├── base_agent.py
│   ├── cache.py
│   ├── utils.py
│   └── logger.py
│
├── data/                                   # <--- NEW: dedicated data subsystem
│   ├── __init__.py
│   │
│   ├── sources/                            # Connectors to external APIs
│   │   ├── __init__.py
│   │   ├── base_source.py                  # Abstract class (fetch_raw)
│   │   ├── yahoo_source.py                 # Implements yfinance
│   │   ├── alpha_vantage_source.py
│   │   └── local_csv_source.py             # For offline testing
│   │
│   ├── normalizers/                        # Convert raw API responses to standard schemas
│   │   ├── __init__.py
│   │   ├── yahoo_normalizer.py
│   │   ├── alpha_normalizer.py
│   │   └── schema.py                       # Defines standard dict keys (e.g. 'revenue', 'net_income')
│   │
│   ├── repository/                         # The main interface for agents
│   │   ├── __init__.py
│   │   ├── financial_repo.py               # get_income_statement, get_balance_sheet, get_cashflow
│   │   ├── price_repo.py                   # get_price_history, get_current_price
│   │   └── company_repo.py                 # get_company_info (sector, market cap, etc.)
│   │
│   ├── storage/                            # Persistent storage (cache + optional DB)
│   │   ├── __init__.py
│   │   ├── cache_manager.py                # Advanced cache (with invalidation strategies)
│   │   └── db_connector.py                 # (optional) SQLite/PostgreSQL for large history
│   │
│   └── pipeline.py                         # Orchestrates fetch → normalise → store → serve
│
├── agents/                                 # Each agent still isolated
│   ├── fundamental/
│   │   ├── agent.py                        # Imports from data.repository
│   │   ├── metrics.py
│   │   ├── rules.yaml / rules.py
│   │   └── tests/
│   ├── technical/
│   └── sentiment/
│
├── orchestrator/
│   └── runner.py
│
└── examples/
    └── run_analysis.py
```