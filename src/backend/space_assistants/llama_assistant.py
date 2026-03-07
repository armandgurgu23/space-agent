from src.backend.models.server_models import ChatHistory


class LlamaSpaceAssistant(object):

    def __init__(self):
        pass
        
    def __call__(self, current_user_message:str, chat_history: ChatHistory):
        return self.get_assistant_response(
            current_user_message, chat_history
        )
    
    def get_assistant_response(self, current_user_message:str, chat_history:ChatHistory):
        # TODO: Integrate LLM based chat. For now echo back.
        should_chat_end = False

        # TODO: Let LLM naturally determine this based on context.
        if current_user_message == 'Quit' or current_user_message == 'quit':
            should_chat_end = True

        assistant_response = f"Echo: {current_user_message}"
        return assistant_response, should_chat_end