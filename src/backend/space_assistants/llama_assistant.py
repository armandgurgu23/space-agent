from src.backend.models.server_models import ChatHistory
from jinja2 import Environment, FileSystemLoader
from src.backend.utils.jinja_utils import render_prompt
from src.backend.space_assistants.tool_definitions.space_api_tools import get_latest_space_news
from src.backend.space_assistants.tool_definitions import message_user
from ollama import chat

import logging
logger = logging.getLogger(__name__)


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
            messages=messages,
            tools=[get_latest_space_news, message_user]
        )
    
    def extract_assistant_message_from_response(self, llm_response):
        response_generation = llm_response.message
        if not response_generation.tool_calls:
            # TODO: Figure out what the best fallback strategy is here. For now defaulting to a generic ERROR message to track how many times this happens.
            return 'ERROR: I could not understand your intent. Please try again.', False      
        if len(response_generation.tool_calls) > 1:
            raise RuntimeError('Model responded with parallel tool calls instead of just 1 tool call. Unexpected behaviour.')
        
        generated_tool = response_generation.tool_calls[0].function.model_dump()

        if generated_tool['name'] == 'message_user':
            # The communication tool does not need to be executed.
            logger.info('Assistant generated a message to the end user!')
            return generated_tool['arguments']['message'], generated_tool['arguments']['should_chat_end']
        
        print('TODO: Handle cases where we generate a tool to execute!!!!!')
        breakpoint()

        return 

    
    def get_assistant_response(self, current_user_message:str, chat_history:ChatHistory):
        # TODO: Integrate LLM based chat. For now echo back.
        should_chat_end = False

        # TODO: Let LLM naturally determine this based on context.
        if current_user_message == 'Quit' or current_user_message == 'quit':
            should_chat_end = True
        
        current_messages = self.prepare_messages_for_llm_call(current_user_message, chat_history)
        llm_response = self.make_llm_call(current_messages)
        print('\n\n')
        print(llm_response)
        print('\n\n')
        assistant_response, should_chat_end = self.extract_assistant_message_from_response(llm_response)        
        return assistant_response, should_chat_end