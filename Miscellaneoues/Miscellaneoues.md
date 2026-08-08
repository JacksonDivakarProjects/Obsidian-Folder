Cross-cutting reference notes that don't belong to one specific domain — LLM prompting technique and general-purpose Python utilities (moved here from Data Science/Miscellaneous 1).

## 🗺️ Map of Content (auto-generated)
- [[Miscellaneoues/Prompting Frameworks|Prompting Frameworks]] — Catalog of LLM prompting frameworks (RTF, BAB, TAG, RISE, CARE, Plan-and-Solve, CoT-SC, ReAct, R-E-F) with templates and a summary table for choosing among them.
- [[Miscellaneoues/Asynchronous Programming/Asynchronous Programming|Asynchronous Programming]] — asyncio core concepts and sync-vs-async execution models in Python.
- [[Miscellaneoues/File Handling In Python/File Handling in Python|File Handling in Python]] — Opening, reading, writing, and the full file-mode reference.
- [[Miscellaneoues/OS Module/OS Module|OS Module]] — Paths, environment variables, system info, permissions, and os.walk.
- [[Miscellaneoues/Pydantic/Pydantic|Pydantic]] — Models, validators, computed fields, serialization, and inheritance.
- [[Miscellaneoues/Regular Expression/Regular Expression|Regular Expression]] — Regex reference diagrams and learning resources.
- [[Miscellaneoues/Thread Pool Executor/Thread Pool Executer|Thread Pool Executor]] — concurrent.futures.ThreadPoolExecutor: submit/map/as_completed and error handling.

## 🔗 Cross-Topic Connections (auto-generated)
- [[Miscellaneoues/Asynchronous Programming/Asynchronous Programming|Asynchronous Programming]] and [[Miscellaneoues/Thread Pool Executor/Thread Pool Executer|Thread Pool Executor]] are the two main Python concurrency models — async I/O vs. threaded I/O-bound work.
- [[Miscellaneoues/File Handling In Python/File Handling in Python|File Handling in Python]] and [[Miscellaneoues/OS Module/OS Module|OS Module]] are typically used together for filesystem-heavy scripts.
- [[Miscellaneoues/Pydantic/Pydantic|Pydantic]] models often validate data extracted via [[Miscellaneoues/Regular Expression/Regular Expression|Regular Expression]] parsing.
- [[Miscellaneoues/Prompting Frameworks|Prompting Frameworks]] is the LLM-facing counterpart to the general Python utilities below — both are cross-cutting tools used across the other areas of this vault (e.g. Data Engineering scripts, AI Notes).
