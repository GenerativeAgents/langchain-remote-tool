# LangChain Remote Tool

A Python package that enables the creation of LangChain tools from OpenAPI schemas, allowing seamless integration of external APIs into your LangChain applications.

## Features

- Create LangChain tools dynamically from OpenAPI schemas
- Automatic request/response handling
- Asynchronous execution support
- Bearer token authentication

## Requirements

- Python 3.9 or later
- langchain-core 0.3 or later

## Installation

```bash
pip install langchain-remote-tool
```

## Usage

```python
from langchain_remote_tool import RemoteTool

# Initialize the tool with OpenAPI schema URL and API key
tool = RemoteTool(
  url="https://api.example.com/openapi.json",
  api_key="your-api-key"
)

# Use the tool asynchronously
result = await tool.arun("input text")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
