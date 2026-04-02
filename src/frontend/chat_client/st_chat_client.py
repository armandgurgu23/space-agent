import requests
from typing import Dict


class ChatClient:
    """Client for interacting with the FastAPI chat backend."""
    
    def __init__(self, base_url: str):
        """
        Initialize the chat client.
        
        Args:
            base_url: Base URL of the FastAPI backend (e.g., "[HOST]:[PORT]")
        """
        self.base_url = base_url.rstrip('/')
    
    def start_chat(self) -> Dict:
        """
        Start a new chat session.
        
        Returns:
            Dict containing session_id, message, and created_at
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.post(f"{self.base_url}/start_chat")
        response.raise_for_status()
        return response.json()
    
    def send_message(self, session_id: str, message: str) -> Dict:
        """
        Send a message to the chat assistant.
        
        Args:
            session_id: The session identifier
            message: The user's message
            
        Returns:
            Dict containing session_id, user_message, assistant_response, and timestamp
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.post(
            f"{self.base_url}/chat/{session_id}",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    
    def get_chat_history(self, session_id: str) -> Dict:
        """
        Retrieve the complete chat history for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dict containing session_id and messages list
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(f"{self.base_url}/chat/{session_id}/history")
        response.raise_for_status()
        return response.json()
    
    def end_chat(self, session_id: str) -> Dict:
        """
        End an active chat session, marking it as closed without deleting history.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dict containing a confirmation message
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.post(f"{self.base_url}/end_chat/{session_id}")
        response.raise_for_status()
        return response.json()

    def delete_session(self, session_id: str) -> Dict:
        """
        Delete a chat session and its history entirely.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dict containing success message
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(f"{self.base_url}/chat/{session_id}")
        response.raise_for_status()
        return response.json()