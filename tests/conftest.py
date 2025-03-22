"""
Pytest configuration for Files-DB-MCP tests
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio


@pytest.fixture
def mock_vector_search():
    """
    Mock vector search engine for testing
    """
    mock = MagicMock()
    mock.search.return_value = [
        {
            "file_path": "test_file.py",
            "file_type": "py",
            "content": "# Test content",
            "score": 0.95,
        }
    ]

    # Add specific method mocks as needed
    mock.index_file.return_value = True
    mock.delete_file.return_value = True

    return mock


@pytest.fixture
def mock_file_processor():
    """
    Mock file processor for testing
    """
    mock = MagicMock()
    mock.get_file_list.return_value = ["test_file.py", "another_file.js"]
    mock.is_indexing_complete.return_value = True
    mock.get_indexing_progress.return_value = 100.0
    mock.get_files_indexed.return_value = 10
    mock.get_total_files.return_value = 10

    return mock


@pytest.fixture
def sample_project_dir(tmp_path):
    """
    Create a sample project directory with some files for testing
    """
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    # Create some sample files
    python_file = src_dir / "main.py"
    python_file.write_text(
        "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()"
    )

    js_file = src_dir / "script.js"
    js_file.write_text("function hello() {\n    console.log('Hello, world!');\n}\n\nhello();")

    # Create a .git directory to simulate a git repository
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    # Create a .gitignore file
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("__pycache__/\nnode_modules/\n*.pyc")

    return tmp_path


@pytest.fixture
def app():
    """Create a FastAPI application for testing"""
    from fastapi import FastAPI
    return FastAPI()


@pytest_asyncio.fixture
async def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client_id():
    """Generate a unique client ID for SSE tests"""
    return f"test_client_{id(asyncio.current_task())}"


@pytest_asyncio.fixture
async def async_queue():
    """Create an asyncio queue for SSE tests"""
    return asyncio.Queue()
