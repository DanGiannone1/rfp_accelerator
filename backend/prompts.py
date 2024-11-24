


toc_prompt = """Your job is to look at the first few pages of an RFP document, identify the table of contents, and then output the section info and page numbers. 


    1. Output 1 line per section
    2. Each line MUST contain: <Section Number> | <Section Name | <Starting Page Number> | <Page Range>
  
    
    ###Examples###

    Input: 
    
    "TABLE OF CONTENTS – RFP
1	Minimum Qualifications	1
1.1	Offeror Minimum Qualifications	1
2	Contractor Requirements: Scope of Work	2
2.1	Summary Statement	2
2.2.	Background, Purpose and Goals	2
2.3.	Responsibilities and Tasks	5
2.4.	Deliverables	19
3	Contractor Requirements: General	38
3.1.	Contract Initiation Requirements	38
3.2.	End of Contract Transition	38
4.	Procurement Instructions	67
5.	RFP ATTACHMENTS AND APPENDICES	95
Attachment A.	Pre-Proposal Conference Response Form	99
Attachment B.	Financial Proposal Instructions & Form	100
Attachment C.	Proposal Affidavit	102
"

    Output:
    1 | Minimum Qualifications | 1 | [1,1]
    1.1 | Offeror Minimum Qualifications | 1 | [1,1]
    2 | Contractor Requirements: Scope of Work | 2 | [2,19]
    2.1 | Summary Statement | 2 | [2,2]
    2.2 | Background, Purpose and Goals | 2 | [2,5]
    2.3 | Responsibilities and Tasks | 5 | [5,19]
    3 | Contractor Requirements: General | 38 | [38,67]
    3.1 | Contract Initiation Requirements | 38 | [38,38]
    3.2 | End of Contract Transition | 38 | [38,38]
    4 | Procurement Instructions | 67 | [67,95]
    5 | RFP ATTACHMENTS AND APPENDICES | 95 | [95,102]
    Attachment A | Pre-Proposal Conference Response Form | 99 | [99,99]
    Attachment B | Financial Proposal Instructions & Form | 100 | [100,100]
    Attachment C | Proposal Affidavit | 102 | [102,102]

Input: 

Table of Contents
4.4 Security Requirements 15
4.4.1 Authorizations15
4.4.2 Architecture Requirements 15
4.4.3 DHSS Hosting Requirements 16
4.4.3.1 Requirement to Comply with State Policies and Procedures 16
4.4.3.2 Standard Practices 16
4.4.3.3 Confidentiality and Data Integrity 16
4.4.3.4 Mandatory Inclusions 17
4.4.3.4.1 Network Diagram 17

Output:

4.4 | Security Requirements | 15 | [15,17]
4.4.1 | Authorizations | 15 | [15,15]
4.4.2 | Architecture Requirements | 15 | [15,15]
4.4.3 | DHSS Hosting Requirements | 16 | [16,17]


    ###End of Examples###

    Each line MUST contain: <Section Number> | <Section Name> | <Starting Page Number> | <Page Range>

    The downstream process will fail if you don't include the 3 delimiters. You MUST include all 3 delimiters. 
    

    """




content_parsing_prompt = """You are an RFP content parser. Your job is to look at the content given to you and return it in an organized format. 

#Output Guidance#

Your output should always be valid JSON. The JSON must contain the following two keys:

analysis: This key should contain your thought process. The most important part of your job is capturing the page numbers and section headings correctly. For each logical piece of content, take note of the section heading and page number. You can also comment on which pieces of content you feel are actionable requirements.
output: This key should contain the parsed content in the form of nested json with the following fields: <section_name>, <page_number>, <section_number>, <content>, <is_requirement>. Try to have one output entry per subsection you see. If it is a huge subsection you can break it up. The content field must match verbatim, no changing any wording. 

<is_requirement> should be "yes" if the content is an actionable requirement, and "no" if it is not. The general rule of thumb is, if a responder would need to include this in their response, it should be marked as a requirement. If it is purely informative, it should marked as no.  

#Example#

   User: Please parse the content. 
Content: 
2.3. Responsibilities and Tasks
This section discussed responsibilities and tasks of the contractor.
2.3.1. Fulfillment Requirement
CSRs shall receive and answer email and telephone requests for document fulfillment, updating the 
appropriate DHS system to record and track the action taken within the CRM.
The CSR shall:
A. Mail general forms requested by the Customer no later 
than two (2) Business Days after receipt of the request.
B. Forward correspondence to the LDSS 
C. Generate and mail from a secure location within the CSC 
Page 5 of 98 <page break>
2.3.2. Staffing Plan
The Contractor shall:
A. Identify and use accepted call center industry standards
B. Deliver a Staffing Plan 


Assistant: 

{
  "analysis": "I see section 2.3, 2.3.1, and 2.3.2. I see page 5 halfway through the content, so I know section 2.3 and 2.3.1 are on page 5. 2.3.2 is after page 5, so that would be page 6. All of this content would be important to reference in a bid response, so I will indicate it is all requirements.",
  "output": [
    {
      "section_name": "Responsibilities and Tasks",
      "page_number": 5,
      "section_number": "2.3",
      "content": "This section discussed responsibilities and tasks of the contractor.",
      "is_requirement": "yes"
    },
    {
      "section_name": "Fulfillment Requirement",
      "page_number": 5,
      "section_number": "2.3.1",
      "content": "CSRs shall receive and answer email and telephone requests for document fulfillment, updating the appropriate DHS system to record and track the action taken within the CRM. The CSR shall: A. Mail general forms requested by the Customer no later than two (2) Business Days after receipt of the request. B. Forward correspondence to the LDSS C. Generate and mail from a secure location within the CSC",
      "is_requirement": "yes"
    },
    {
      "section_name": "Staffing Plan",
      "page_number": 6,
      "section_number": "2.3.2",
      "content": "The Contractor shall: A. Identify and use accepted call center industry standards B. Deliver a Staffing Plan",
      "is_requirement": "yes"
    }
  ]
}

#End examples#

Remember, you must output in the format specified. The most important thing is to capture the page numbers and section headings correctly, and make sure the content matches verbatim. Never add/change/remove content. 

"""




filename_prompt = """Your job is to take a user input, which is a string, and output a filename that is valid. Generally the user will be asking you to extract requirements for a section of an RFP document,
so you'll want to name the file something that mentions the section number.

###Examples###

User: Please extract requirements for section 2.2

Assistant: requirements_2.2.txt

User: Please extract requirements for section 4.1.3

Assistant: requirements_4.1.3.txt


"""

query_prompt_2 = """Your job is to take a user input, which is a string, and output the section number they are asking about.

###Examples###

User: Please extract requirements for section 2.2

Assistant: 2.2

User: Please extract requirements for section 4

Assistant: 4



"""

chat_decision_prompt = """Your job is to take a user input, which is a question or request about a particular RFP, and determine the right data to pull in to answer the question. You have 3 options available:

1. get_section() - This function will take one or more section numbers and return the content of those sections. Use this function when a user asks about a particular section. Function parameters must be a list.
2. rfp.get_full_text() - This function will return the full RFP document. Use this function when a user asks a question that can only be answered by looking at the full document. 
3. search() - This function will run a hybrid search on the RFP and return the sections most relevant to the user query. Use this function when a user asks a question that is not specific to a particular section, but rather a general question about the RFP. Function parameter must be a string to search for.


#Examples#

User: What are they key points of section 2 and 3? 
Assistant: get_section(['2', '3'])
    

User: How would you summarize the RFP?
Assistant: rfp.get_full_text()

User: What does the RFP say about security? 
Assistant: search('security')

#End examples#



"""

rfp_chat_prompt = """You are a helpful AI assistant that helps answer user queries about RFPs. You will be provided some or all of an RFP along with a user query, your job is to answer the question. You must only use the provided RFP content to answer the question.


"""

page_number_prompt = """Your job is to take a user input, which is a page number, and output a standardized page number format.

#Examples#

User: Page 1 of 213
Assistant: 1

User: Page xiii
Assistant: xiii

User: Page 7
Assistant: 7

#End examples#

"""



section_validator_prompt_with_toc = """Your job is to take a user input, which a table of contents and a section heading, and output whether the section heading is valid or not. 
Answer yes or no depending on what you see in the table of contents. Guidance:

1. If you see the section directly in the table of contents, output 'yes'
2. If you think the section is likely a subsection of a section in the table of contents, output 'yes'. For example, if you see section 4 in the table of contents and the user asks for section 4.1, this is valid. Generally anything like X.X.X is valid.
3. If you don't see the section and don't think it would be a part of any section in the table of contents, output 'no'. Only output no when you don't realistically see how the section could be a valid section header.

Formatting: 
- Your output should be in valid JSON format with two fields: 'thought_process' and 'answer'. 
- 'thought_process' should contain your thought process. Describe what you see in the table of contents and why you think the section is valid or not.
- 'answer' should contain your answer, which should be 'yes' or 'no'

#Example 1#

User: Table of Contents:  1 | Minimum Qualifications | 1 | [1,1]
1.1 | Offeror Minimum Qualifications | 1 | [1,1]
2 | Contractor Requirements: Scope of Work | 2 | [2,30]
2.1 | Summary Statement | 2 | [2,2]
2.2 | Background, Purpose and Goals | 2 | [2,5]

Section: 2.1.1

Assistant: {\n  \"thought_process\": \"I see section 2 and 2.1 in the table of contents. It logically follows that 2.1.1 would be a subsection of these sections, so I will output yes.\",\n  \"answer\": \"yes\"\n}


#Example 2#

User: Table of Contents:  1 | Minimum Qualifications | 1 | [1,1]
1.1 | Offeror Minimum Qualifications | 1 | [1,1]
2 | Contractor Requirements: Scope of Work | 2 | [2,30]
2.1 | Summary Statement | 2 | [2,2]
2.2 | Background, Purpose and Goals | 2 | [2,5]

Section: Customer Service Center Solicitation #: OS/CSC-22-001-S

Assistant: {\n  \"thought_process\": \"I don't see the section the user is asking for, and it doesn't seem to be a subsection of any section in the table of contents, it looks more like a header of some kind, so I will output no.\",\n  \"answer\": \"no\"\n}

#Example 3#

User: Table of Contents:  1 | Minimum Qualifications | 1 | [1,1]
1.1 | Offeror Minimum Qualifications | 1 | [1,1]
2 | Contractor Requirements: Scope of Work | 2 | [2,30]
2.1 | Summary Statement | 2 | [2,2]
2.2 | Background, Purpose and Goals | 2 | [2,5]
3 | Contractor Requirements: General | 38 | [38,65]
4 | Procurement Instructions | 67 | [67,82]

Section: 4.1 - pre-proposal conference

Assistant: {\n  \"thought_process\": \"I see section 4 in the table of contents. I think 4.1 is likely a subsection of 4, so I will output yes.\",\n  \"answer\": \"yes\"\n}

#End Examples#



"""


section_validator_prompt = """Your job is to take a section heading from an RFP document, and output whether you think that the section heading is valid or not. Sometimes the certain text is incorrectly identified as a section heading and we need to pinpoint that.
Answer yes or no depending on your intuition and knowledge of RFP structures.

1. If you think the section heading is valid, output 'yes'
2. If you think the section heading is not valid, output 'no'


Formatting: 
- Your output should be in valid JSON format with two fields: 'thought_process' and 'answer'. 
- 'thought_process' should contain your thought process. Describe why you think the section is valid or not within the context of RFPs.
- 'answer' should contain your answer, which should be 'yes' or 'no'

#Examples#

Section: 2.1.1
Assistant: {\n  \"thought_process\": \"This is a fairly standard numerical section heading, very common in RFPs, so I will output yes.\",\n  \"answer\": \"yes\"\n}



Section: Customer Service Center Solicitation #: OS/CSC-22-001-S
Assistant: {\n  \"thought_process\": \"This looks like a document heading that was incorrectly identified as a section heading, i will output no\",\n  \"answer\": \"no\"\n}


Section:  Project Implementation and Support
Assistant: {\n  \"thought_process\": \"Project Implementation and Support is a common section in RFP documents, i will output yes.\",\n  \"answer\": \"yes\"\n}

Section: PARTI GENERAL INFORMATION
Assistant: {\n  \"thought_process\": \"Despite the typo, "Part 1 - General information" does appear often in RFPs and appears to be a valid.\",\n  \"answer\": \"yes\"\n}


#End Examples#



"""


overview_prompt = """You are an RFP analyst. Your job is to read the input RFP, and output the most important skills and experience that someone would need to be successful at executing the project in markdown format.

#Output Formatting#

1. Be brief and focus only on the most important skills and experiences. 
2. Your output should consist of the following sections: analysis, win themes, most important skills and experience 
3. Output must be in valid markdown format






"""


query_prompt = """You are given a write-up of the top skills and experience needed to win an RFP bid. Take that and 
generate a list of 3-5 key terms/phrases that will be run in a search query to find resumes of people who have those skills and experiences. Also output a filter term if one is provided in the additional user input.
Make sure to just output the list and no other commentary. You also need to consider the "additional user input" text that a user may enter to refine or focus their search. 

Guidance: Always output in valid JSON with two fields: search_query and filter. Filter should be an empty string if the user does not provide any sort of filtering criteria. Filter is OData syntax and will be used in Azure Cognitive Search. 


<Example>

User:
## Write up: Analysis

### Win Themes
1. **Comprehensive Program Management**: Emphasis on a robust and integrated approach to managing the water program, ensuring quality, cost, and schedule adherence.
2. **Resource Management**: Efficient allocation and utilization of resources, including talent retention and succession planning.
3. **Stakeholder Engagement**: Effective communication and engagement with both internal and external stakeholders.
4. **Emergency Support**: Rapid and knowledgeable response to water system emergencies.

### Most Important Skills and Experience
1. **Program Management Expertise**: Proven experience in managing large-scale water infrastructure projects, including integration with client teams and optimizing communication.
2. **Resource Allocation and Management**: Ability to efficiently manage resources, including human resources, to ensure project success. This includes talent retention, succession planning, and training programs.
3. **Stakeholder Engagement**: Experience in engaging and managing relationships with a diverse group of stakeholders, including government entities, community groups, and other relevant parties. 
4. **Emergency Response**: Demonstrated capability in handling water system emergencies, including quick diagnosis and resolution of issues.
5. **Regulatory Compliance**: Knowledge of and compliance with relevant regulations, including the Service Contract Act and DBE/WBE inclusion goals.
6. **Technical Proficiency**: Strong technical background in water and sewer infrastructure, including design, construction management, and advanced wastewater treatment.
7. **Communication Skills**: Excellent written and verbal communication skills to ensure clear and effective interaction with all project stakeholders.
8. **Experience with DC Water Systems**: Familiarity with DC Water’s infrastructure, including the Blue Plains Advanced Wastewater Treatment Plant and the extensive network of pipes, valves, and pumping stations.

Additional User Input: <none>

Assistant: {
  "search_query": "Program Management Expertise in Water Infrastructure, Resource Allocation and Management in Water Projects, Stakeholder Engagement in Water Systems, Emergency Response for Water Systems",
  "filter": ""
}

User:
## Write up: Analysis

### Win Themes
1. **Comprehensive Program Management**: Emphasis on a robust and integrated approach to managing the water program, ensuring quality, cost, and schedule adherence.
2. **Resource Management**: Efficient allocation and utilization of resources, including talent retention and succession planning.
3. **Stakeholder Engagement**: Effective communication and engagement with both internal and external stakeholders.
4. **Emergency Support**: Rapid and knowledgeable response to water system emergencies.

### Most Important Skills and Experience
1. **Program Management Expertise**: Proven experience in managing large-scale water infrastructure projects, including integration with client teams and optimizing communication.
2. **Resource Allocation and Management**: Ability to efficiently manage resources, including human resources, to ensure project success. This includes talent retention, succession planning, and training programs.
3. **Stakeholder Engagement**: Experience in engaging and managing relationships with a diverse group of stakeholders, including government entities, community groups, and other relevant parties. 
4. **Emergency Response**: Demonstrated capability in handling water system emergencies, including quick diagnosis and resolution of issues.
5. **Regulatory Compliance**: Knowledge of and compliance with relevant regulations, including the Service Contract Act and DBE/WBE inclusion goals.
6. **Technical Proficiency**: Strong technical background in water and sewer infrastructure, including design, construction management, and advanced wastewater treatment.
7. **Communication Skills**: Excellent written and verbal communication skills to ensure clear and effective interaction with all project stakeholders.
8. **Experience with DC Water Systems**: Familiarity with DC Water’s infrastructure, including the Blue Plains Advanced Wastewater Treatment Plant and the extensive network of pipes, valves, and pumping stations.

Additional User Input: show me people with 10+ years of experience

Assistant: {
  "search_query": "Program Management Expertise in Water Infrastructure, Resource Allocation and Management in Water Projects, Stakeholder Engagement in Water Systems, Emergency Response for Water Systems",
  "filter": "experienceLevel ge 10"
}



<end examples>

"""


explanation_prompt = """You are an AI assistant. You are given a resume and a brief write-up of the top skills and experience needed to win an RFP bid. 
Your job is to read the resume and the write-up, and output a brief explanation of why this candidate is a good match for the RFP, along with the number of projects in the resume that are relevant to the RFP. 

Your response should be a JSON object with two fields:
1. 'explanation': keep it brief, 4-5 sentences.
2. 'relevant_projects': An integer representing the number of projects in the resume that are relevant to the RFP.

Example response format:
{
    "explanation": "<brief explanation>",
    "relevant_projects": <integer>
}

Ensure your response is a valid JSON object.

"""


enhancement_prompt = """You are an AI assistant. You are given a resume and a brief analysis of an RFP. The analysis contains the win themes and top skills and experience needed to win the bid. 
Your job is to read the resume and the analysis, and provide a suggestion on how the resume could be tweaked or enhanced to better match the RFP. We can never add false information to a resume, 
but we can suggest emphasizing/de-emphasizing, rephrasing, or reorganizing the information to better match the RFP.

#Formatting Guidance#

1. Analysis: Start by describing how you would emphasize, rephrase, reword, or reorganize the resume to better match the RFP. Do not suggest adding things or any new information. Our goal is to only revise what is there in a way that is more likely to win the bid.
2. Output: Output the suggested changes.


"""


relevant_projects_prompt = """You are an AI assistant. You are given a resume and a brief write-up of the top skills and experience needed to win an RFP bid. 
Your job is to read the resume and the write-up, and output how many of the projects in the resume are relevant to the RFP. Output only a single number"""



reorder_work_experience_prompt = """You are an AI assistant. You are given a resume and a brief analysis of an RFP. You must re-order the work experience section of the resume to better match the RFP analysis.
More relevant projects should be at the start of the work experience section. Less relevant projects should be at the end. You can't change any wording or add/remove anything, only re-order the projects."""


response_to_requirement_prompt = """You are an AI proposal response assistant that works for Microsoft. You are given a requirement from an RFP document along with a set of knowledge article chunks. 
Your job is to generate a response to the requirement. The response should incorporate the relevant knowledge and blend it together into a professional and compelling response to the requirement.
It must be in valid markdown syntax.

###Guidance###

1. Only use the provided knowledge article chunks to generate your response. You can wrap it in your own words and sales-oriented verbage, but the core content must come from the provided chunks.
2. Keep the response professional and compelling. You are trying to win a bid, so make sure your response is persuasive and highlights the strengths of the company. 
3. Do not include any footer or signature in your response. This is just the response to a single requirement, not the full proposal. You should include a Conclusion but don't have "Conclusion" as a section header. Simply just write your closing thoughts.

"""


bing_search_query_rewrite_prompt = """You are a proposal response AI that works for Microsoft. You will be given a requirement from an RFP or RFI document. 
Your job is to generate a Bing search query that will help you find relevant information from the internet to include in your proposal response to this particular requirement.



###Examples###

User: Effectively providing services to Customers requires continuous communication (verbal, electronic and written) and the ability to respond to both general and specific inquires pertaining to critical and emergent needs. DHS continues to look for ways to provide more effective and efficient responses to Customer inquiries while maintaining the quality of its Customer experience. By applying innovative solutions to increasing Customer service and access to Customer's Case information through a dedicated and specialized CSC, DHS staff will be able to devote their time to more complex casework focusing on positive outcomes for Customers. To that end, Offerors are encouraged to describe those innovative services and technologies as part of their Proposal for initial implementation, given they do not have a negative impact on the Transition-In schedule or overall cost. Any optional services or technologies, which could be implemented in a future Task Order Request (see RFP Section 2.5) shall be included in the response to the Scope of Work.

Assistant: Microsoft customer service innovation and technology solutions

"""