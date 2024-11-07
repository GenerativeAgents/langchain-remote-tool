from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class RemoteTool(BaseTool):
    """External API tool based on OpenAPI schema"""

    url: str = Field(description="URL of OpenAPI schema")
    api_key: str = Field(description="API key")
    name: str = Field(default="remote_tool", description="Name of the tool")
    description: str = Field(
        default="External API tool based on OpenAPI schema",
        description="Description of the tool",
    )
    _schema: Dict[str, Any] = {}
    _client: Optional[httpx.AsyncClient] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._load_schema()
        self._setup_client()

    def _load_schema(self) -> None:
        """Load and parse OpenAPI schema"""
        response = httpx.get(self.url)
        self._schema = response.json()

        # Set tool information from schema
        operation = self._get_first_operation()
        if "operationId" in operation:
            self.name = operation["operationId"]
        if "description" in operation:
            self.description = operation["description"]

    def _setup_client(self) -> None:
        """Initialize HTTP client"""
        parsed_url = urlparse(self.url[1:])
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self._client = httpx.AsyncClient(
            base_url=base_url, headers={"Authorization": f"Bearer {self.api_key}"}
        )

    def _get_first_operation(self) -> Dict[str, Any]:
        """Get first operation information from schema"""
        paths = self._schema.get("paths", {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                return operation
        raise ValueError("No valid operation found")

    def _run(self, *args, **kwargs) -> Any:
        """Synchronous execution is not supported"""
        raise NotImplementedError("RemoteTool only supports asynchronous execution")

    async def _arun(self, tool_input: str, **kwargs) -> Any:
        """Asynchronous execution of the tool"""
        if not self._client:
            raise RuntimeError("Client is not initialized")

        # Get operation information from schema
        operation = self._get_first_operation()
        path = list(self._schema.get("paths", {}).keys())[0]

        # Get request body schema
        request_body = operation.get("requestBody", {})
        content = request_body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})

        # Get required parameters and type information from schema
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Build payload
        payload = {}

        # Assign tool_input to appropriate parameter based on schema
        if required and properties:
            first_required_param = required[0]
            # Check property type information
            param_schema = properties.get(first_required_param, {})
            if param_schema.get("type") == "string":
                payload[first_required_param] = tool_input

        # Merge additional keyword arguments
        payload.update(kwargs)

        # Execute request
        response = await self._client.post(path, json=payload)
        response.raise_for_status()

        return response.json()
