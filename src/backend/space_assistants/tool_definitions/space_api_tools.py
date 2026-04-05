

def get_latest_space_news(search_query:str) -> str:
    """Get the latest news article related to a given search question about a space-related topic or entity.
  
    Args:
        search_query: A short search query used to find the latest information about space-related topic or entity
        (example: James Webb Space Telescope)

    Returns:
        A string representing the latest news article found about the short search query.
    """
    # TODO: make the actual API call to the Space API. For now 
    print(search_query)
    return "The James Webb Space Telescope was built in 2075 and it's so huge!"

def make_space_api_call(search_query:str):
    pass