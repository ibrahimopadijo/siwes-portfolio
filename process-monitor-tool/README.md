# Linux Process & Memory Monitor

A Python-based SOC automation tool that interacts directly with the Linux operating system to monitor running processes, evaluate memory consumption, and flag resource anomalies.

## Key Capabilities
* **Native OS Integration:** Uses the Python `subprocess` module to interface directly with the Linux `ps` utility.
* **Automated Data Parsing:** Dynamically structures raw Linux text output into sortable arrays.
* **Defensive Error Handling:** Utilizes `try/except` blocks to safely parse variable data types and ignore non-numerical header rows without crashing.
* **Anomaly Detection:** Applies logical thresholds (e.g., > 10% memory consumption) to flag high-risk processes that could indicate memory leaks or Denial of Service (DoS) conditions.

## Usage
```bash
python3 process_monitor.py
