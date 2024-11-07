import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool


from prompts import response_to_requirement_prompt

load_dotenv()

aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

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




def respond_to_requirement(user_message, requirement):




    llm_input = f"<Start Requirement>\n{requirement}\n<End Requirement>\n{user_message}"
    print(llm_input)

    messages = [
        {"role": "system", "content": response_to_requirement_prompt},
        {"role": "user", "content": llm_input},
    ]
    
    response = ''
    for chunk in primary_llm.stream(messages):
        response += chunk.content
        yield chunk.content

    print(response)
    return "success"

