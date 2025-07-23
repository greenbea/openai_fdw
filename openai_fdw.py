"""
OpenAI Foreign Data Wrapper for PostgreSQL using Multicorn

This FDW allows PostgreSQL to create tables based on OpenAI API responses
with schema validation to ensure JSON data matches table structure.
"""

import json
import requests
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
from logging import INFO


class OpenAIForeignDataWrapper(ForeignDataWrapper):
    """
    A foreign data wrapper for querying OpenAI API and returning structured data
    that matches the table schema.
    """

    def __init__(self, options, columns):
        super(OpenAIForeignDataWrapper, self).__init__(options, columns)
        
        # Required options
        self.api_key = options.get('api_key')
        if not self.api_key:
            log_to_postgres('api_key is required for OpenAI FDW', ERROR)
            
        self.prompt = options.get('prompt')
        if not self.prompt:
            log_to_postgres('prompt is required for OpenAI FDW', ERROR)
        
        self.model = options.get('model', 'gpt-3.5-turbo')
        self.max_tokens = int(options.get('max_tokens', '2000'))
        self.temperature = float(options.get('temperature', '0.7'))
        self.max_rows = int(options.get('max_rows', '100'))
        
        self.columns = columns
        self.column_names = list(columns.keys())
        
        self._response_cache = None
        
        log_to_postgres(f'OpenAI FDW initialized with model: {self.model}', DEBUG)

    def execute(self, quals, columns):
        """
        Execute the query by calling OpenAI API and returning matching rows
        """
        try:
            schema_info = self._generate_schema_info()
            
            response_data = self._make_openai_request(schema_info)
            
            if not response_data:
                log_to_postgres('No data returned from OpenAI API', WARNING)
                return
            
            for row_data in response_data:
                if self._validate_row_schema(row_data):
                    yield self._convert_row_to_postgres_format(row_data)
                else:
                    log_to_postgres(f'Skipping invalid row: {row_data}', WARNING)
                    
        except Exception as e:
            log_to_postgres(f'Error in OpenAI FDW execution: {str(e)}', ERROR)
            raise

    def _generate_schema_info(self):
        """
        Generate schema information to include in the OpenAI prompt
        """
        schema_obj = {}
        
        for column_name, column_def in self.columns.items():
            pg_type = column_def.type_name.lower()
            
            if pg_type in ['integer', 'int4', 'int8', 'bigint', 'smallint']:
                json_type = 'number (integer)'
            elif pg_type in ['real', 'float4', 'float8', 'double precision', 'numeric', 'decimal']:
                json_type = 'number (float)'
            elif pg_type in ['boolean', 'bool']:
                json_type = 'boolean'
            elif pg_type in ['date']:
                json_type = 'string (YYYY-MM-DD format)'
            elif pg_type in ['timestamp', 'timestamptz']:
                json_type = 'string (ISO 8601 format)'
            else:
                json_type = 'string'
            
            schema_obj[column_name] = json_type
        
        schema_instruction = f"""
IMPORTANT: Return ONLY a valid JSON array of objects. Each object must match this exact schema:

{json.dumps(schema_obj, indent=2)}

Example format:
[
  {{{', '.join([f'"{k}": <{v}>' for k, v in schema_obj.items()])}}},
  {{{', '.join([f'"{k}": <{v}>' for k, v in schema_obj.items()])}}}
]

Return {self.max_rows} rows maximum. Do not include any text before or after the JSON array.
"""
        
        return schema_instruction

    def _make_openai_request(self, schema_info):
        """
        Make HTTP request to OpenAI API with schema validation instructions
        """
        full_prompt = f"{self.prompt}\n\n{schema_info}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a data generator. Always return valid JSON arrays matching the requested schema exactly. Never include explanatory text.'
                },
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
        
        try:
            log_to_postgres(f'Making OpenAI API request with model: {self.model}', DEBUG)
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                log_to_postgres('No choices in OpenAI response', ERROR)
                return None
            
            content = result['choices'][0]['message']['content'].strip()
            
            try:
                # Remove any potential markdown code blocks
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                data = json.loads(content)
                
                if not isinstance(data, list):
                    log_to_postgres(f'Expected JSON array, got: {type(data)}', ERROR)
                    return None
                
                log_to_postgres(f'Successfully parsed {len(data)} rows from OpenAI response', INFO)
                return data
                
            except json.JSONDecodeError as e:
                log_to_postgres(f'Failed to parse JSON response: {e}\nContent: {content}', ERROR)
                return None
                
        except requests.exceptions.RequestException as e:
            log_to_postgres(f'HTTP request failed: {str(e)}', ERROR)
            return None
        except Exception as e:
            log_to_postgres(f'Unexpected error in OpenAI request: {str(e)}', ERROR)
            return None

    def _validate_row_schema(self, row_data):
        """
        Validate that a row from the API response matches the expected schema
        """
        if not isinstance(row_data, dict):
            return False
        
        for column_name, column_def in self.columns.items():
            if column_name in row_data:
                value = row_data[column_name]
                pg_type = column_def.type_name.lower()
                
                # Type validation
                if pg_type in ['integer', 'int4', 'int8', 'bigint', 'smallint']:
                    if not isinstance(value, int):
                        return False
                elif pg_type in ['real', 'float4', 'float8', 'double precision', 'numeric', 'decimal']:
                    if not isinstance(value, (int, float)):
                        return False
                elif pg_type in ['boolean', 'bool']:
                    if not isinstance(value, bool):
                        return False
                elif pg_type in ['text', 'varchar', 'char', 'date', 'timestamp', 'timestamptz']:
                    if not isinstance(value, str):
                        return False
        
        return True

    def _convert_row_to_postgres_format(self, row_data):
        """
        Convert a row from the API response to PostgreSQL format
        """
        converted_row = {}
        
        for column_name in self.column_names:
            if column_name in row_data:
                value = row_data[column_name]
                
                # Handle null values
                if value is None:
                    converted_row[column_name] = None
                else:
                    # Convert based on PostgreSQL column type
                    column_def = self.columns[column_name]
                    pg_type = column_def.type_name.lower()
                    
                    if pg_type in ['integer', 'int4', 'int8', 'bigint', 'smallint']:
                        converted_row[column_name] = int(value)
                    elif pg_type in ['real', 'float4', 'float8', 'double precision', 'numeric', 'decimal']:
                        converted_row[column_name] = float(value)
                    elif pg_type in ['boolean', 'bool']:
                        converted_row[column_name] = bool(value)
                    else:
                        converted_row[column_name] = str(value)
            else:
                # Column not in response, set to None
                converted_row[column_name] = None
        
        return converted_row

    def can_sort(self, sortkeys):
        """
        Indicate that we cannot handle sorting (OpenAI API doesn't support it)
        """
        return []

    def explain(self, quals, columns, sortkeys=None, verbose=False):
        """
        Provide query execution plan information
        """
        return [
            f"OpenAI API call to model: {self.model}",
            f"Prompt: {self.prompt[:100]}..." if len(self.prompt) > 100 else f"Prompt: {self.prompt}",
            f"Expected columns: {', '.join(self.column_names)}",
            f"Max rows: {self.max_rows}"
        ]
