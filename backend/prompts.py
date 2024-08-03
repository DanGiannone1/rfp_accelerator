


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

thought_process: This key should contain your thought process. The most important part of your job is capturing the page numbers and section headings correctly. For each logical piece of content, take note of the section heading and page number. You can also comment on which pieces of content you feel are actionable requirements.
content: This key should contain the parsed content. The content MUST be structured in the following manner: <section_name> | <page_number> | <section_number> | <verbatim_content> | <is_requirement>. Each item within a line must be separated by a pipe "|". Try to have one line per subsection you see. If it is a huge subsection you can break it up. 

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
  "thought_process": "I see section 2.3, 2.3.1, and 2.3.2. I see page 5 halfway through the content, so I know section 2.3 and 2.3.1 are on page 5. 2.3.2 is after page 5, so that would be page 6. All of this content would be important to reference in a bid response, so i will indicate it is all requirements.",
  "content": "Responsibilities and Tasks | 5 | 2.3 | This section discussed responsibilities and tasks of the contractor. | yes \n Fulfillment Requirement | 5 | 2.3.1 | CSRs shall receive and answer email and telephone requests for document fulfillment, updating the appropriate DHS system to record and track the action taken within the CRM. The CSR shall: A. Mail general forms requested by the Customer no later than two (2) Business Days after receipt of the request. B. Forward correspondence to the LDSS C. Generate and mail from a secure location within the CSC | yes \n Staffing Plan | 6 | 2.3.2 | The Contractor shall: A. Identify and use accepted call center industry standards B. Deliver a Staffing Plan | yes"
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



section_validator_prompt = """Your job is to take a user input, which a table of contents and a section heading, and output whether the section heading is valid or not. 
Answer yes or no depending on what you see in the table of contents. Guidance:

1. If you see the section directly in the table of contents, output 'yes'
2. If you think the section is likely a subsection of a section in the table of contents, output 'yes'. For example, if you see section 4 in the table of contents and the user asks for section 4.1, this is valid. Generally anything like X.X.X is valid.
3. If you don't see the section and don't think it would be a part of any section in the table of contents, output 'no'

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


