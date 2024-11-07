import pytest
import respx

from langchain_remote_tool import RemoteTool


@pytest.fixture
def mock_schema():
    return {
        "openapi": "3.0.0",
        "paths": {
            "/api/v1/tools/md-to-docx": {
                "post": {
                    "operationId": "convertMdToDocx",
                    "description": "Convert Markdown to DOCX",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["markdown"],
                                    "properties": {
                                        "markdown": {
                                            "type": "string",
                                            "description": "Markdown content",
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        },
    }


@pytest.mark.asyncio
async def test_remote_tool_initialization(mock_schema):
    with respx.mock() as mocker:
        mocker.get(
            "https://www.middleman-ai.com/api/v1/tools/md-to-docx/openapi.json"
        ).respond(json=mock_schema)

        tool = RemoteTool(
            url="https://www.middleman-ai.com/api/v1/tools/md-to-docx/openapi.json",
            api_key="test-key",
        )

        assert tool.name == "convertMdToDocx"
        assert tool.description == "Convert Markdown to DOCX"


@pytest.mark.asyncio
async def test_remote_tool_execution(mock_schema):
    with respx.mock() as mocker:
        mocker.get(
            "https://www.middleman-ai.com/api/v1/tools/md-to-docx/openapi.json"
        ).respond(json=mock_schema)
        mocker.post("/api/v1/tools/md-to-docx").respond(
            json={"docxUrl": "https://example.com/doc.docx"}
        )

        tool = RemoteTool(
            url="https://www.middleman-ai.com/api/v1/tools/md-to-docx/openapi.json",
            api_key="test-key",
        )

        result = await tool.arun("# Test")
        assert result["docxUrl"] == "https://example.com/doc.docx"
