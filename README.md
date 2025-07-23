# PostgreSQL OpenAI Foreign Data Wrapper

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A PostgreSQL Foreign Data Wrapper (FDW) that integrates with OpenAI's API to generate structured data from prompts, mapped directly to your table schemas. Built on Multicorn2.

---

## 🚀 Key Features

- Maps AI-generated content to real PostgreSQL schemas
- Flexible prompt-driven data generation
- Supports GPT-3.5, GPT-4
- Robust error handling and logging
- Production-ready via Multicorn2

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

## ⚙️ Configuration Options

| Option         | Description                   | Default         | Example                           |
|----------------|-------------------------------|-----------------|-----------------------------------|
| `api_key`      | OpenAI API key                | *Required*      | `sk-abc123...`                    |
| `prompt`       | Data generation prompt        | *Required*      | `Generate customer data`          |
| `model`        | OpenAI model                  | `gpt-3.5-turbo` | `gpt-4`                           |
| `max_tokens`   | Token limit                   | `2000`          | `3000`                            |
| `temperature`  | Creativity (0.0-1.0)          | `0.7`           | `0.5`                             |
| `max_rows`     | Max rows returned             | `100`           | `50`                              |

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

## 📄 License

MIT — see [LICENSE](LICENSE).