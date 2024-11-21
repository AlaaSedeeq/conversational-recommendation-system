from langchain_core.tools import tool

from src.infrastructure.search_engine.faiss import FAISS_Search

@tool
def get_recommendations(collected_info: str) -> list[dict]:
    """
    Get movie recommendations based on collected user preferences.
    
    Args:
        collected_info (str): Concise summary of user preferences from follow-up agent
            Example: "User is looking for intense psychological thrillers like Inception and Shutter Island, prefer modern movies with complex plots"
    
    Returns:
        list[str]: List of recommended movies
    """
    template = """<provided_context>\n: {conversations}"""
    try: 
        similarity_search = FAISS_Search()
        results = similarity_search.search(collected_info)
    
        if not results.response:
            return "No recommendations found."
            
        formatted_results = []
        
        for i, (doc, score) in enumerate(results.response, 1):
            recommendation = (
                f"{'-' * 40}\n"
                f"{doc.page_content.strip()}\n"
                f"{'-' * 40}"
            )
            formatted_results.append(recommendation)
        
        separator = "\n\n" + "=" * 80 + "\n\n"
        return template.format_map({"conversations": separator.join(formatted_results)})
        
    except Exception as e:
        return f"Failed to get similar movies: {e}"
    return f"Failed to get similar movies"
