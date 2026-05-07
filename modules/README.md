# 🦅 VigilantReaper v1.1 (BETA)

**VigilantReaper** is an automated, asynchronous reconnaissance framework designed for continuous attack surface monitoring. It helps security researchers and Bug Bounty hunters detect new assets and critical data leaks (.env, API keys, backups) in real-time, before others.

> **Status:** Early Beta. This is the first functional version of the pipeline.

## ⚠️ Disclaimer
This tool is for **educational purposes and authorized security testing only**. The author is not responsible for any misuse. Always follow the Bug Bounty program policy before scanning.

## 🚀 Key Features

*   **Modular Attack Surface Discovery:** Wraps powerful tools like `Subfinder` and `Assetfinder` into a single Python orchestrator.
*   **Asynchronous Probing:** Uses `httpx` and `asyncio.Semaphore` to validate thousands of subdomains concurrently without overloading the system.
*   **Smart Diff-Monitoring:** Implemented via **SQLite**. The framework identifies only **NEW** subdomains from the last scan, allowing the researcher to focus on fresh, unvetted targets.
*   **Automated Loot & Secret Hunting:**
    *   Scans for "forgotten" files: `.env`, `.git/config`, `phpinfo()`, and backups.
    *   Extracts hardcoded secrets from JS files (AWS Keys, Google APIs, JWT, Private RSA).
*   **Real-time Alerting:** Structured HTML notifications sent directly to a Telegram Bot.
*   **Secure Configuration:** Centralized YAML-based config system with `.gitignore` protection for API tokens.

## 🏗️ Architecture

The framework is built following **SOLID** principles for easy expansion:

- **`core/`**: Orchestration logic, Database Management (SQLite), Telegram Notifier, and YAML Parser.
- **`modules/`**: 
    - `discovery`: Subdomain enumeration wrappers.
    - `prober`: Async HTTP validation & title extraction.
    - `loot_scanner`: Sensitive file discovery.
    - `secret_finder`: Regex-based JS analysis.
- **`bin/`**: Storage for external binary dependencies (e.g., subfinder).

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Async Engine:** `asyncio`, `httpx`
- **Database:** SQLite
- **Config:** YAML
- **External Tools:** Subfinder, Assetfinder

## 📋 Roadmap (Future Updates)

As this is a **Beta** version, the following features are planned:
- [ ] Integration of `Waybackurls` and `Gau` for historical data analysis.
- [ ] Automated **Subdomain Takeover** detection (CNAME record analysis).
- [ ] Implementation of a Web Dashboard using **FastAPI** for visual scan management.
- [ ] Random User-Agent rotation to bypass basic WAF filters.

## ⚙️ Installation & Usage

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/YourUsername/VigilantReaper.git
    cd VigilantReaper
    ```
2.  **Setup environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Configure:** Create a `config.yaml` based on the provided template and add your Telegram credentials.
4.  **Run:**
    ```bash
    python3 main.py
    ```
