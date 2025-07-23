-- Installation script for OpenAI FDW
CREATE EXTENSION IF NOT EXISTS multicorn;

CREATE SERVER openai_server
FOREIGN DATA WRAPPER multicorn
OPTIONS (wrapper 'openai_fdw.OpenAIForeignDataWrapper');

-- Example table
CREATE FOREIGN TABLE customers_ai (
    id INTEGER,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT
) SERVER openai_server OPTIONS (
    api_key 'your-openai-api-key-here',
    prompt 'Generate realistic customer data',
    max_rows '10'
);
