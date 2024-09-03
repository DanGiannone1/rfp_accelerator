"""
Search module for RFP-based resume matching.

This module handles the search and matching of resumes based on RFP requirements using Azure AI Search and Azure OpenAI.
"""

# Standard library imports
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI

# Local imports
from helper_functions import get_rfp_analysis_from_db
from prompts import explanation_prompt, query_prompt

# Load environment variables
load_dotenv()

# Azure Cognitive Search configuration
AI_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
AI_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
AI_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]

# Azure OpenAI configuration
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize clients
search_client = SearchClient(AI_SEARCH_ENDPOINT, AI_SEARCH_INDEX, AzureKeyCredential(AI_SEARCH_KEY))

aoai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-05-15"
)

primary_llm = AzureChatOpenAI(
    azure_deployment=AOAI_DEPLOYMENT,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT
)

primary_llm_json = AzureChatOpenAI(
    azure_deployment=AOAI_DEPLOYMENT,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT,
    model_kwargs={"response_format": {"type": "json_object"}}
)

def search(rfp_name, user_input):
    """
    Perform a search for matching resumes based on RFP requirements and user input.

    Args:
        rfp_name (str): The name of the RFP document.
        user_input (str): Additional input from the user to refine the search.

    Returns:
        list: A list of dictionaries containing formatted search results.
    """
    skills_and_experience = get_rfp_analysis_from_db(rfp_name)
    llm_input = f"Write-up: {skills_and_experience}. \n\nAdditional User Input: {user_input}"
    print(llm_input)

    messages = [
        {"role": "system", "content": query_prompt},
        {"role": "user", "content": llm_input}
    ]

    response = primary_llm_json.invoke(messages)
    data = json.loads(response.content)
    search_query = data['search_query']
    filter_value = data['filter']

    print("Search Query:", search_query)
    print("Filter:", filter_value)

    query_vector = generate_embeddings(search_query)
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=3, fields="searchVector")

    results = search_client.search(
        search_text=search_query,
        vector_queries=[vector_query],
        top=3,
        filter=filter_value
    )

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_result = {executor.submit(generate_explanation, result['content'], skills_and_experience): result for result in results}
        
        formatted_results = []
        for future in as_completed(future_to_result):
            result = future_to_result[future]
            try:
                explanation_data = future.result(timeout=10)
                formatted_results.append({
                    "name": result['sourceFileName'],
                    "jobTitle": result['jobTitle'],
                    "experienceLevel": result['experienceLevel'],
                    "relevantProjects": explanation_data['relevant_projects'],
                    "explanation": explanation_data['explanation']
                })
            except Exception as exc:
                print(f'Generating explanation for {result["sourceFileName"]} generated an exception: {exc}')
                formatted_results.append({
                    "name": result['sourceFileName'],
                    "jobTitle": result['jobTitle'],
                    "experienceLevel": result['experienceLevel'],
                    "relevantProjects": 0,
                    "explanation": "Unable to generate explanation."
                })

    return formatted_results

def generate_explanation(content, skills_and_experience):
    """
    Generate an explanation for why a resume matches the RFP requirements.

    Args:
        content (str): The content of the resume.
        skills_and_experience (str): The required skills and experience from the RFP.

    Returns:
        dict: A dictionary containing the explanation and number of relevant projects.
    """
    input_text = f"Write-up: {skills_and_experience}\n\nResume: {content}"

    messages = [
        {"role": "system", "content": explanation_prompt},
        {"role": "user", "content": input_text}
    ]

    try:
        response = primary_llm_json.invoke(messages)
        print(response.content)
        response_content = json.loads(response.content)
        
        explanation = response_content.get('explanation', "No explanation provided.")
        relevant_projects = int(response_content.get('relevant_projects', 0))
        
        return {
            "explanation": explanation,
            "relevant_projects": relevant_projects
        }
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return {
            "explanation": "Unable to generate explanation due to an error.",
            "relevant_projects": 0
        }

def generate_embeddings(text, model="text-embedding-ada-002"):
    """
    Generate embeddings for the given text using Azure OpenAI.

    Args:
        text (str): The text to generate embeddings for.
        model (str): The name of the embedding model to use.

    Returns:
        list: The generated embedding vector.
    """
    return aoai_client.embeddings.create(input=[text], model=model).data[0].embedding

if __name__ == "__main__":
    # Example usage
    search("rfp_name", "user_input")