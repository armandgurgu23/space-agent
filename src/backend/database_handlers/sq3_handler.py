import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class ChatDatabase:
    """
    Database handler for chat sessions and messages.
    Encapsulates all SQLite operations for the chat assistant.
    """
    
    def __init__(self, db_path: str = "chat_sessions.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection.
        
        Returns:
            sqlite3.Connection: Database connection with row_factory set
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    
    def init_db(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_session(self, session_id: str) -> Dict:
        """
        Create a new chat session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dict containing session details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        created_at = datetime.now()
        
        try:
            cursor.execute(
                """
                INSERT INTO sessions (session_id, created_at, updated_at)
                VALUES (?, ?, ?)
                """,
                (session_id, created_at, created_at)
            )
            conn.commit()
            
            return {
                "session_id": session_id,
                "created_at": created_at,
                "updated_at": created_at
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session identifier to check
            
        Returns:
            bool: True if session exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT 1 FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone() is not None
            return result
        finally:
            conn.close()
    
    def add_message(self, session_id: str, role: str, content: str) -> Dict:
        """
        Add a message to a session.
        
        Args:
            session_id: Session to add message to
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            Dict containing the message details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now()
        
        try:
            # Insert message
            cursor.execute(
                """
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, timestamp)
            )
            
            # Update session's updated_at timestamp
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (timestamp, session_id)
            )
            
            conn.commit()
            
            return {
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": timestamp
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_messages(self, session_id: str) -> List[Dict]:
        """
        Retrieve all messages for a session.
        
        Args:
            session_id: Session to get messages from
            
        Returns:
            List of message dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT role, content, timestamp 
                FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
                """,
                (session_id,)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            return messages
        finally:
            conn.close()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session to delete
            
        Returns:
            bool: True if session was deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete messages
            cursor.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,)
            )
            
            # Delete session
            cursor.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def list_sessions(self) -> List[Dict]:
        """
        List all sessions with metadata.
        
        Returns:
            List of session dictionaries with message counts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT 
                    s.session_id, 
                    s.created_at, 
                    s.updated_at,
                    COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                """
            )
            sessions = [dict(row) for row in cursor.fetchall()]
            return sessions
        finally:
            conn.close()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session metadata.
        
        Args:
            session_id: Session to retrieve
            
        Returns:
            Dict with session details or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT session_id, created_at, updated_at
                FROM sessions 
                WHERE session_id = ?
                """,
                (session_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()