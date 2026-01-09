import pytest
from unittest.mock import MagicMock, patch
from database import DatabaseManager
import os

@pytest.fixture
def db_manager():
    # Force sqlite for basic unit tests
    with patch.dict(os.environ, {"DATABASE_TYPE": "sqlite"}):
        return DatabaseManager()

def test_db_manager_init(db_manager):
    """Test if manager initializes with correct defaults."""
    assert db_manager.db_type == "sqlite"
    assert "bugkiller.db" in db_manager.sqlite_path

@patch('sqlite3.connect')
def test_execute_query_sqlite(mock_connect, db_manager):
    """Test execute_query calls sqlite3 when type is sqlite."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    db_manager.execute_query("SELECT 1")
    
    mock_connect.assert_called_once()
    mock_conn.execute.assert_called_once_with("SELECT 1", ())
    mock_conn.commit.assert_called_once()

@patch('pymysql.connect')
def test_execute_query_mysql(mock_connect):
    """Test execute_query calls pymysql and handles param conversion."""
    with patch.dict(os.environ, {"DATABASE_TYPE": "mysql", "DB_HOST": "localhost"}):
        manager = DatabaseManager()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Test ? to %s replacement
        manager.execute_query("SELECT * FROM bugs WHERE id = ?", (1,))
        
        # Verify pymysql was used and query was converted
        mock_connect.assert_called()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM bugs WHERE id = %s", (1,))

def test_fetch_one_logic(db_manager):
    """Test fetch_one returns first item or None."""
    with patch.object(db_manager, 'execute_query') as mock_execute:
        # Case 1: Results found
        mock_execute.return_value = [{"id": 1}]
        assert db_manager.fetch_one("SELECT...") == {"id": 1}
        
        # Case 2: No results
        mock_execute.return_value = []
        assert db_manager.fetch_one("SELECT...") is None
