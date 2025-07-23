# PostgreSQL OpenAI Foreign Data Wrapper

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A PostgreSQL Foreign Data Wrapper (FDW) that integrates with OpenAI's API to generate structured data from prompts, mapped directly to your table schemas. Built on Multicorn2.

---

## 🚀 Features

- Integrates with OpenAI Chat Completion API (e.g., `gpt-3.5-turbo`, `gpt-4`)
- Ensures OpenAI returns data matching your table structure
- Converts OpenAI JSON responses into PostgreSQL rows with type checks
- Configurable prompt, model, temperature, max tokens, and max rows
- Logs warnings and errors in PostgreSQL logs

---

## 📦 Requirements

- PostgreSQL 12+
- Python 3.7+
- [Multicorn2](https://github.com/pgsql-io/multicorn2)
- OpenAI API key

---

## ⚙️ Installation (Summary)

```bash
# System deps
sudo apt install postgresql-server-dev-all python3-dev python3-pip

# Multicorn2
git clone https://github.com/pgsql-io/multicorn2.git
cd multicorn2 && make && sudo make install

# Clone & install
git clone https://github.com/greenbea/openai_fdw.git
cd openai_fdw && pip3 install -r requirements.txt && python3 setup.py install
```

---

## 🧲 Example Usage

```sql
-- Create a foreign table powered by OpenAI
CREATE FOREIGN TABLE users_ai (
    id INTEGER,
    name TEXT,
    email TEXT,
    city TEXT
) SERVER openai_server OPTIONS (
    api_key 'sk-...',
    prompt 'Generate realistic user data',
    model 'gpt-3.5-turbo',
    max_rows '10'
);

-- Generate data
SELECT * FROM users_ai LIMIT 5;
```

---

## 🛠️ Configuration Options

| Option        | Description                    | Default         | Example          |
| ------------- | ------------------------------ | --------------- | ---------------- |
| `api_key`     | Your OpenAI API key (required) | *none*          | `sk-abc123...`   |
| `prompt`      | Prompt text to generate data   | *none*          | `Generate users` |
| `model`       | OpenAI chat model name         | `gpt-3.5-turbo` | `gpt-4`          |
| `max_tokens`  | Maximum tokens in response     | `2000`          | `3000`           |
| `temperature` | Controls creativity (0.0-1.0)  | `0.7`           | `0.5`            |
| `max_rows`    | Maximum rows to return         | `100`           | `50`             |

---

## 🔐 Security Tips

- Store your OpenAI key in environment variables or config
- Grant minimal permissions to FDW users
- Avoid hardcoding secrets in SQL

---

## 🛠️ Troubleshooting

- Verify Multicorn2 is installed and loaded
- Use `SET log_min_messages = DEBUG1;` to view FDW logs
- Ensure prompts return expected fields matching your table schema

---

## 🤝 Contributing

PRs are welcome! Clone the repo, create a feature branch, and submit your improvements.

---

## ⚠️ Limitations

- WHERE and ORDER BY clauses are evaluated by PostgreSQL, not by OpenAI — data is generated first, then filtered/sorted locally
- API keys in FDW options are visible to users with schema access — keep keys secure
- Relies on OpenAI Chat Completion API responses as valid JSON arrays

---

## 📄 License

MIT — see [LICENSE](LICENSE).