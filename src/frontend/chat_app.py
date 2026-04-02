from src.frontend.chat_client.st_chat_client import ChatClient
from src.frontend.chat_ui.st_chat_ui import ChatUI
from dotenv import load_dotenv
from os import environ

load_dotenv('src/frontend/.env')


def main():
    # Configuration
    BACKEND_URL = environ['BACKEND_URL']
    
    # Initialize chat client
    chat_client = ChatClient(BACKEND_URL)
    
    # Initialize UI
    chat_ui = ChatUI(chat_client)
    
    # Render the UI
    chat_ui.render()


if __name__ == "__main__":
    main()