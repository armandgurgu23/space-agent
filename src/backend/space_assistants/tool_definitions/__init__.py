

# Default tool to handle communication with the user. Implemented this because
# Ollama does not allow passing format and tools together as per these
# Github issues:
# 1. https://github.com/ollama/ollama/issues/8095
# 2. https://github.com/ollama/ollama/issues/7778

def message_user(message: str, should_chat_end: bool) -> dict:
    """Respond to the user's message. Always call this tool to deliver a response unless you are calling get_latest_space_news.

    Args:
        message: Your response to the user. Must always be grounded in space topics. If the user asks something off-topic, this should contain your refusal and redirection back to space.
        should_chat_end: Set to True ONLY if the user's message is a clear closing farewell with no follow-up intent (e.g. "bye!", "thanks, that's all"). Set to False if there is any remaining intent or question.

    Returns:
        A dictionary containing the message and should_chat_end flag.
    """
    return {
        'message': message,
        'should_chat_end': should_chat_end
    }