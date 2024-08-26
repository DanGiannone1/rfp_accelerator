# RFP Upload

[Insert screenshot of the RFP Upload Page here]

## Overview

The Upload process is the first step in the user flow for the application. When a user navigates to the Upload page, they will have the ability to upload an RFP or select & view the overview of a previously uploaded RFP. The upload process serves as the foundation for the rest of the application modules.

## High-level Flow

1. The user uploads an RFP
2. The file is passed to the backend upload API route 
3. The upload API route calls the `process_rfp` function from `upload.py` 
4. `process_rfp` consists of numerous steps:
   a. Upload the RFP to blob storage
   b. Read the RFP from blob storage with Azure Document Intelligence to convert the document to text
   c. Kick off the intelligent chunking process as a background thread
   d. Pass the RFP text to the LLM to generate and stream back the overview which is displayed to the user
   e. Store the overview on Cosmos DB

> **Note:** The chunking process is described in detail below.

[Insert architecture diagram here]

## Prerequisites and Setup

To set up and run the RFP Upload module, make sure you have followed the environment setup instructions in the main readme file.

Ensure you have the following services available and corresponding environment variables set up:
- Azure Data Lake Storage
- Azure Document Intelligence
- Azure OpenAI Service
- Azure Cosmos DB

Ensure you have authentication set up between your data lake storage and document intelligence service. The code assumes you configured a managed identity between the two, but you can use other authentication methods if you prefer.

## Intelligent Chunking 

RFPs are extremely large and can be potentially hundreds of different, unique formats. Out-of-the-box chunking strategies do not cut it and will lead to poor results when trying to leverage generative AI against them. The upload process kicks off a custom chunking process defined in `chunking.py`. If you want to swap this chunking strategy out for your own, simply replace `chunking.py` with your chunking code. 

`Chunking.py` aims to implement "section-based" chunking. When it comes to RFPs, we generally need a cohesive, whole section to be passed to the context window of an LLM in order to get a quality output. Chunking by an arbitrary number of tokens, or by page, will lead to incomplete and incorrect outputs. Services like Azure Document Intelligence allow us to identify the section headers within the document. We can use this information, in combination with some clever LLM prompts, to chunk the document into sections. 

The chunking process follows these steps:

1. We start by using the LLM to extract the table of contents from the RFP. This is technically an optional step; the process would work without it, but it improves performance of the subsequent steps. 

2. For each section heading identified by Azure Document Intelligence, we use the LLM to determine whether or not that section heading is "valid". Azure Document Intelligence (or any traditional ML model for section heading identification) is not perfect and will sometimes incorrectly identify a line of text as a section heading. We use the LLM to help filter out these mistakes. Our prompt is given the table of contents and the proposed section heading, and asked to determine whether or not it thinks it is a valid section heading. 

3. Once we have the refined list of section headings, we programmatically associate the content of each section with its respective section heading. This yields a python dictionary where each key is the section heading, and each value is the corresponding text of that section. 

4. We store the chunks in Cosmos DB for future use.

[Insert solution architecture diagram here]

> **Note:** This is a fairly token-intensive strategy, but necessary for accurate chunking and quality outputs downstream. When it comes to RFPs, a missed requirement or incomplete response could mean the difference between winning and losing the bid. The next version of this process will implement an agent-based approach where the agent iteratively checks and makes sure the document is chunking correctly.