"""
Query expansion module for semantic search.

Generates multiple query variations to capture different aspects
and phrasing of the user's information need.
"""

from functools import lru_cache
from langchain_openai import ChatOpenAI
from core.settings import settings


@lru_cache(maxsize=1)
def _get_llm():
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )


def generate_query_variations(user_query: str) -> list[str]:
    """
    Generate 3 semantic query variations plus the original.
    
    This improves retrieval by searching for different phrasings
    and perspectives on the same information need.
    
    Args:
        user_query: Original user question
    
    Returns:
        List of 4 queries: original + 3 variations
    
    Example:
        Input: "What are the IPO risks?"
        Output:
        - "What are the IPO risks?"
        - "risk factors in IPO prospectus"
        - "investment risks mentioned in filing"
        - "financial risk disclosures"
    """
    try:
        llm = _get_llm()
        
        prompt = f"""Generate exactly 3 semantic variations of this question that would help retrieve different facets of relevant information from a financial document.

Each variation should:
1. Use different terminology or phrasing
2. Focus on a different aspect or perspective
3. Be phrased as a natural question or search query

Return ONLY the 3 variations, one per line, starting with a dash:
- variation 1
- variation 2
- variation 3

Original question: {user_query}

Generate 3 variations:"""
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse variations
        variations = [
            line.strip("- ").strip()
            for line in content.split("\n")
            if line.strip() and line.strip().startswith("-")
        ]
        
        # Ensure we have exactly 3 variations
        variations = variations[:3]
        while len(variations) < 3:
            # Fallback variations if generation fails
            variations.append(user_query)
        
        # Return original query first, then variations
        result = [user_query] + variations
        
        print(f"[MULTI_QUERY] Original: {user_query}")
        for i, var in enumerate(variations, 1):
            print(f"[MULTI_QUERY] Variation {i}: {var}")
        
        return result
        
    except Exception as e:
        print(f"[MULTI_QUERY ERROR] Query expansion failed: {e}")
        print(f"[MULTI_QUERY] Returning original query only")
        return [user_query]


def generate_queries(user_query: str) -> list[str]:
    """Legacy function name - calls generate_query_variations."""
    return generate_query_variations(user_query)
