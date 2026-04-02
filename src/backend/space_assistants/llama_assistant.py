from src.backend.models.server_models import ChatHistory
from jinja2 import Environment, FileSystemLoader
from src.backend.utils.jinja_utils import render_prompt
from ollama import chat


class SpaceChatAssistant(object):

    def __init__(self, prompt_templates_path:str, model_name:str = "llama3.2:3b"):
        self.model_name = model_name
        self.prompt_templates_path = prompt_templates_path
        self.jinja_env = Environment(loader=FileSystemLoader(prompt_templates_path))
        self.system_prompt = render_prompt(
            template_file='system_prompt.jinja', jinja_env=self.jinja_env
        )

        
    def __call__(self, current_user_message:str, chat_history: ChatHistory):
        return self.get_assistant_response(
            current_user_message, chat_history
        )
    
    def prepare_messages_for_llm_call(self, current_user_message:str, chat_history:ChatHistory):

        messages = [
            {
                'role': 'system', 'content': self.system_prompt
            }
        ]

        if chat_history:
            llm_session_context = [{'role': curr_turn['role'], 'content': curr_turn['content']} for curr_turn in chat_history]
            messages.extend(llm_session_context)

        messages.append({'role': 'user', 'content': current_user_message})
        print(messages)
        return messages


    def make_llm_call(self, messages:list[dict]):
        return chat(
            model=self.model_name,
            messages=messages
        )
    
    def extract_assistant_message_from_response(self, llm_response):
        # TODO: Logic to parse assistant response. May want to add database logging
        # here when doing tool calls.
        return llm_response.message.content
    
    def get_assistant_response(self, current_user_message:str, chat_history:ChatHistory):
        # TODO: Integrate LLM based chat. For now echo back.
        should_chat_end = False

        # TODO: Let LLM naturally determine this based on context.
        if current_user_message == 'Quit' or current_user_message == 'quit':
            should_chat_end = True
        
        current_messages = self.prepare_messages_for_llm_call(current_user_message, chat_history)
        llm_response = self.make_llm_call(current_messages)
        assistant_response = self.extract_assistant_message_from_response(llm_response)        
        return assistant_response, should_chat_end