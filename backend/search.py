
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
import concurrent.futures


#import lib for pypdf2


from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  

import os  
from dotenv import load_dotenv  
import json

from openai import AzureOpenAI  
import os
from langchain_openai import AzureChatOpenAI

from azure.search.documents.models import VectorizedQuery
from prompts import explanation_prompt, query_prompt, relevant_projects_prompt
from helper_functions import get_rfp_analysis_from_db

from dotenv import load_dotenv 


load_dotenv()

connect_str = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
container_name = "resumes"
storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")

form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")

ai_search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
ai_search_key = os.environ["AZURE_SEARCH_KEY"]
ai_search_index = os.environ["AZURE_SEARCH_INDEX"]

# Azure OpenAI
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")



search_index_client = SearchIndexClient(ai_search_endpoint, AzureKeyCredential(ai_search_key))
search_client = SearchClient(ai_search_endpoint, ai_search_index, AzureKeyCredential(ai_search_key))

aoai_client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2023-05-15"
        )



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




def generate_relevant_projects_number(content, skills_and_experience):

    input_text = f"Write-up: {skills_and_experience}\n\nResume: {content}"

    messages = [
        {"role": "system", "content": relevant_projects_prompt},
        {"role": "user", "content": input_text}
    ]

    try:
        response = primary_llm.invoke(messages)
        response = response.content
        print(response)


        return response
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return "Unable to generate explanation due to an error."





def search(rfp_name, user_input):
    # Get the necessary skills and experience for this RFP from Cosmos
    skills_and_experience = get_rfp_analysis_from_db(rfp_name)
    #print(skills_and_experience)

    # Generate a search query based on the skills and experience
    llm_input = f"Write-up: {skills_and_experience}. \n\nAdditional User Input: {user_input}"
    print(llm_input)

    messages = [
        {"role": "system", "content": query_prompt},
        {"role": "user", "content": llm_input}
    ]

    response = primary_llm_json.invoke(messages)
    data = json.loads(response.content)
    # Extract values into variables
    search_query = data['search_query']
    filter_value = data['filter']

    # Print the variables to verify
    print("Search Query:", search_query)
    print("Filter:", filter_value)



    #Vectorize the search query
    query_vector = generate_embeddings(search_query)
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=3, fields="searchVector")

    #Run a hybrid search against the index
    results = search_client.search(
        search_text=search_query,
        vector_queries=[vector_query],
        top=3,
        filter=filter_value
    )

    # Use ThreadPoolExecutor for asynchronous explanation and relevant projects generation
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_result = {executor.submit(generate_explanation, result['content'], skills_and_experience): result for result in results}
        
        formatted_results = []
        for future in concurrent.futures.as_completed(future_to_result):
            result = future_to_result[future]
            try:
                explanation_data = future.result(timeout=10)  # 10 second timeout
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
    input_text = f"Write-up: {skills_and_experience}\n\nResume: {content}"

    messages = [
        {"role": "system", "content": explanation_prompt},
        {"role": "user", "content": input_text}
    ]

    try:
        response = primary_llm_json.invoke(messages)
        print(response.content)
        response_content = json.loads(response.content)
        
        # Ensure the response contains both fields
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

def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    return aoai_client.embeddings.create(input = [text], model=model).data[0].embedding






if __name__ == "__main__":

    #reset_processed_files()

    search("rfp_name", "user_input")
    

    
    


    

