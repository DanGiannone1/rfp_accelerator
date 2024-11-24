import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
import requests
import json

from prompts import response_to_requirement_prompt, bing_search_query_rewrite_prompt

load_dotenv()

# Azure OpenAI Configuration
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Azure Cognitive Search Configuration
ai_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
ai_search_key = os.getenv("AZURE_SEARCH_KEY")
ai_search_index = os.getenv("AZURE_SEARCH_INDEX_KB")

# Bing Search Configuration
subscription_key = os.getenv("BING_SEARCH_KEY")
search_url = "https://api.bing.microsoft.com/v7.0/search"
bing_search_enabled = os.getenv("BING_SEARCH_ENABLED", "false").lower() == "true"
knowledge_base_search_enabled = os.getenv("KNOWLEDGE_BASE_SEARCH_ENABLED", "false").lower() == "true"

# Initialize clients
primary_llm = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint
)

primary_llm_json = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint,
    model_kwargs={"response_format": {"type": "json_object"}}
)

aoai_client = AzureOpenAI(
    azure_endpoint=aoai_endpoint,
    api_key=aoai_key,
    api_version="2023-05-15"
)

search_client = SearchClient(
    endpoint=ai_search_endpoint,
    index_name=ai_search_index,
    credential=AzureKeyCredential(ai_search_key)
)

def generate_embeddings(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """Generate embeddings for the given text using Azure OpenAI."""
    return aoai_client.embeddings.create(input=[text], model=model).data[0].embedding

def bing_search(requirement: str) -> List[Dict[str, str]]:
    """Perform a Bing web search with LLM-rewritten query and return formatted results."""
    # First, rewrite the requirement into a search query
    messages = [
        {"role": "system", "content": bing_search_query_rewrite_prompt},
        {"role": "user", "content": requirement}
    ]
    
    try:
        # Get the rewritten search query
        response = primary_llm.invoke(messages)
        search_query = response.content
        print(f"Original requirement: {requirement}")
        print(f"Rewritten search query: {search_query}")
        
        # Perform the Bing search with the rewritten query
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {
            "q": search_query,
            "textDecorations": True,
            "textFormat": "HTML",
            "count": 15
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        formatted_results = []
        if "webPages" in search_results and "value" in search_results["webPages"]:
            for result in search_results["webPages"]["value"]:
                formatted_results.append({
                    "source": "web",
                    "content": result["snippet"]
                })
                
        return formatted_results
    except Exception as e:
        print(f"Error in Bing search: {str(e)}")
        return []

def knowledge_base_query(requirement: str) -> List[Dict[str, Any]]:
    """Query the knowledge base using Azure Cognitive Search with the new index structure."""
    try:
        # Generate embeddings for the requirement
        query_vector = generate_embeddings(requirement)
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=3,
            fields="searchVector"  # Updated to match new field name
        )
        
        # Perform the search
        results = search_client.search(
            search_text=requirement,
            vector_queries=[vector_query],
            select=["content", "sourceFileName", "sourceFilePage", "date"],  # Updated to include new fields
            top=3
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "source": "kb",
                "content": result["content"],
                "metadata": {
                    "filename": result["sourceFileName"],
                    "page": result["sourceFilePage"],
                    "date": result["date"]
                }
            }
            formatted_results.append(formatted_result)
            
        return formatted_results
    except Exception as e:
        print(f"Error in knowledge base query: {str(e)}")
        return []

def format_knowledge_for_llm(knowledge_results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Format all knowledge sources into a single string for the LLM."""
    formatted_text = []
    
    for source_type, results in knowledge_results.items():
        if results:
            formatted_text.append(f"\n{source_type.upper()} RESULTS:")
            for idx, result in enumerate(results, 1):
                if source_type == "kb":
                    metadata = result.get("metadata", {})
                    formatted_text.append(
                        f"[Result {idx}] (Source: {metadata.get('filename', 'Unknown')}, "
                        f"Page: {metadata.get('page', 'Unknown')}, "
                        f"Date: {metadata.get('date', 'Unknown')}): "
                        f"{result['content']}"
                    )
                else:
                    formatted_text.append(f"[Result {idx}]: {result['content']}")
    
    return "\n".join(formatted_text)

def get_knowledge(requirement: str) -> Dict[str, List[Dict[str, Any]]]:
    """Gather knowledge from multiple sources based on the requirement."""
    results = {}
    
    if bing_search_enabled:
        bing_results = bing_search(requirement)
        if bing_results:
            results["bing"] = bing_results
    
    if knowledge_base_search_enabled:
        kb_results = knowledge_base_query(requirement)
        if kb_results:
            results["kb"] = kb_results
        
    return results

def respond_to_requirement(user_message: str, requirement: str):
    """Generate a response to a requirement using multiple knowledge sources."""
    # Get knowledge from various sources
    knowledge_results = get_knowledge(requirement)
    
    # Format the knowledge for the LLM
    knowledge_text = format_knowledge_for_llm(knowledge_results)
    
    # Prepare the complete input for the LLM
    llm_input = f"""<Start Requirement>
{requirement}
<End Requirement>

<Start Additional Knowledge>
{knowledge_text}
<End Additional Knowledge>

<User Message>
{user_message}
</User Message>"""

    print(f"Sending to LLM: {llm_input}")

    # Prepare messages for the LLM
    messages = [
        {"role": "system", "content": response_to_requirement_prompt},
        {"role": "user", "content": llm_input}
    ]
    
    # Stream the response
    for chunk in primary_llm.stream(messages):
        yield chunk.content

    return "success"