import streamlit as st
import requests
from src.frontend.chat_client.st_chat_client import ChatClient


class ChatUI:
    """Streamlit UI components for the chat application."""
    
    def __init__(self, chat_client: ChatClient):
        """
        Initialize the chat UI.
        
        Args:
            chat_client: Instance of ChatClient for backend communication
        """
        self.chat_client = chat_client
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "session_ended" not in st.session_state:
            st.session_state.session_ended = False
        if "has_interaction" not in st.session_state:
            st.session_state.has_interaction = False
    
    def render(self):
        """Main render method for the chat UI."""
        st.title("Chat Assistant")
        
        if st.session_state.session_id is None:
            self._render_start_screen()
        else:
            self._render_chat_interface()
    
    def _render_start_screen(self):
        """Render the initial screen with 'Start Chat' button."""
        st.info("Click the button below to start a new chat session")
        
        if st.button("Start Chat", type="primary"):
            self._handle_start_chat()
    
    def _render_chat_interface(self):
        """Render the main chat interface."""
        self._render_header()
        st.divider()
        self._render_message_history()
        self._handle_user_input()
    
    def _render_header(self):
        """Render the header with session ID and action buttons."""
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        
        with col1:
            st.caption(f"**Session ID:** `{st.session_state.session_id}`")
        
        with col2:
            if st.session_state.session_ended:
                if st.button("Start New Session", type="primary"):
                    self._handle_new_session()
            else:
                if st.button("Reset", type="secondary"):
                    self._handle_reset()

        with col3:
            # End Chat only appears after at least one full (user, assistant) turn
            # and only while the session is still active.
            if st.session_state.has_interaction and not st.session_state.session_ended:
                if st.button("End Chat", type="secondary"):
                    self._handle_end_chat()
    
    def _render_message_history(self):
        """Render all messages in the chat history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def _handle_user_input(self):
        """Handle user input from the chat input widget."""
        if prompt := st.chat_input("Type your message here...", disabled=st.session_state.session_ended):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Add to session state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get and display assistant response
            self._get_assistant_response(prompt)
    
    def _handle_start_chat(self):
        """Handle the start chat button click."""
        try:
            data = self.chat_client.start_chat()
            st.session_state.session_id = data["session_id"]
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to start chat session: {str(e)}")
            st.error("Make sure the backend server is running")
    
    def _handle_end_chat(self):
        """Handle the End Chat button click.
        
        Marks the session as closed on the backend (history is preserved)
        and updates the UI to reflect the ended state.
        """
        try:
            self.chat_client.end_chat(st.session_state.session_id)
            st.session_state.session_ended = True
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to end chat session: {str(e)}")

    def _handle_new_session(self):
        """Handle the Start New Session button click.

        The previous session was already cleanly closed via end_chat, so we
        leave it intact on the backend and simply start a fresh session.
        """
        st.session_state.messages = []
        st.session_state.session_ended = False
        st.session_state.has_interaction = False

        try:
            data = self.chat_client.start_chat()
            st.session_state.session_id = data["session_id"]
        except requests.exceptions.RequestException as e:
            st.session_state.session_id = None
            st.error(f"Failed to start new chat session: {str(e)}")

        st.rerun()

    def _handle_reset(self):
        """Handle the Reset button click.
        
        Deletes the current active session entirely and starts a fresh one.
        """
        try:
            self.chat_client.delete_session(st.session_state.session_id)
        except:
            pass  # Ignore errors on delete

        # Reset all session state
        st.session_state.messages = []
        st.session_state.session_ended = False
        st.session_state.has_interaction = False

        try:
            data = self.chat_client.start_chat()
            st.session_state.session_id = data["session_id"]
        except requests.exceptions.RequestException as e:
            st.session_state.session_id = None
            st.error(f"Failed to start new chat session: {str(e)}")

        st.rerun()
    
    def _get_assistant_response(self, user_message: str):
        """
        Get and display the assistant's response.
        
        Args:
            user_message: The user's message
        """
        try:
            data = self.chat_client.send_message(
                st.session_state.session_id,
                user_message
            )
            assistant_response = data["assistant_response"]

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

            # Add to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response
            })

            # Track whether this is the first completed (user, assistant) turn.
            # If so, rerun so the header re-renders and shows the End Chat button.
            first_interaction = not st.session_state.has_interaction
            st.session_state.has_interaction = True

            if data["session_ended"]:
                st.session_state.session_ended = True
                st.rerun()
            elif first_interaction:
                # Only rerun on the first turn — subsequent turns don't need it
                # since the End Chat button is already visible in the header.
                st.rerun()

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with backend: {str(e)}")
            # Remove the user message if the request failed
            st.session_state.messages.pop()