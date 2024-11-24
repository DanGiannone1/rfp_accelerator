# RFP Accelerator - Transform Your Organization's Proposal Process

![RFP Accelerator Main Image](/images/main_screen.png)

Responding to a Request for Proposal (RFP) or Request for Information (RFI) is a common task in a corporate setting. For most organizations, this is currently a cumbersome and time-consuming process involving multiple teams coordinating for weeks or even months at a time. 

Generative AI has the ability to transform the proposal response process from start to finish.


## Overview

The RFP Accelerator is an application that allows various operations to be performed against RFPs, leveraging the power of Generative AI to streamline and enhance the proposal process.



## Features

- Upload - Intelligent, AI-powered document chunking and "RFP at a glance"
- Employee Matching - Find the right employees for a given RFP based on skillset or other attributes
- RFP Analyzer - Ask questions about the RFP
- Requirements Extraction - extract requirements or any other structured data from the RFP
- Response builder - Start building your response to the RFP

![User Journey](/images/user_flow.png)



## Setup

### Prerequisites

Each module of the accelerator requires a different set of Azure services. Below is a breakdown of the prerequisites for each module:

| Module | Required Azure Services |
|--------|-------------------------|
| Upload | - Azure Data Lake Storage<br>- Azure Document Intelligence<br>- Azure OpenAI<br>- Azure Cosmos DB<br>- Managed identity between Document Intelligence and Data Lake Storage |
| Employee Matching | - Azure Data Lake Storage<br>- Azure Document Intelligence<br>- Azure OpenAI<br>- Azure Cosmos DB<br>- Azure AI Search |
| RFP Analyzer | - Azure Cosmos DB<br>- Azure OpenAI |
| Requirements Extraction | - Azure Cosmos DB<br>- Azure OpenAI |
| Response Builder | - Azure Cosmos DB<br>- Azure OpenAI<br>- Azure AI Search (optional)<br>- Bing Search (optional)|

> **Note:** For detailed documentation and setup instructions, please refer to the README file in each module's directory.


### Installation

1. **Clone the repository**
   - Open your terminal or command prompt.
   - Run the following commands to clone the repository and navigate into the project directory:
     ```sh
     git clone https://github.com/your-username/rfp-accelerator.git
     cd rfp-accelerator
     ```

2. **Install dependencies**
   - Ensure you have [Node.js](https://nodejs.org/) installed. You can download and install it from the official website.
   - Install front-end dependencies:
     - Navigate to the `front-end` directory:
       ```sh
       cd front-end
       ```
     - Run the following command to install the necessary Node.js packages:
       ```sh
       npm install
       ```
     - After installation, navigate back to the root directory:
       ```sh
       cd ..
       ```
   - Create a new Python virtual environment and install back-end dependencies:
     - Ensure you have Python installed. You can download and install it from the [official website](https://www.python.org/).
     - If you are using VS Code, you can create a virtual environment using the Command Palette:
       - Open the Command Palette by pressing `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (macOS).
       - Type `Python: Create Environment` and select it.
       - Choose `Venv` as the environment type.
       - Select the Python interpreter you want to use.
       - Select requirements.txt
       - VS Code will create the virtual environment and automatically activate it. 
     - Alternatively, you can create the virtual environment from the command line. Run the following command to create a virtual environment named `venv`:
       ```sh
       python -m venv venv
       ```
     - Activate the virtual environment:
       - On macOS and Linux:
         ```sh
         source venv/bin/activate
         ```
       - On Windows:
         ```sh
         venv\Scripts\activate
         ```
     - Install the required Python packages:
       ```sh
       pip install -r requirements.txt
       ```

3. **Create & Configure Azure Services**

   The following Azure services are required for full functionality:

   - **Azure Cosmos DB**
     - Use the NoSQL API
     - No need to create database or container (application will handle this)
     - If using existing database/container, ensure partition key is set to `"partitionKey"`
   
   - **Azure AI Search**
     - Create with default settings
   
   - **Azure Document Intelligence**
     - Make sure your service can leverage API version 2024-07-31 or later (it is not available yet in some regions)
   
   - **Azure OpenAI**
     - Deploy two models:
       - GPT-4o as primary LLM
       - text-embedding-ada-002 for embeddings
     - Ensure rate limit >100k tokens per minute on deployments
   
   - **Azure Data Lake Storage**
     - Create a Storage Account with hierarchical namespace enabled
     - Create a container named "rfp"
     - If you plan to use Employee Matching, create a container named "resumes" and two folders within that container named "source" and "processed". Upload your employee resumes to the "source" folder and run 
            ```sh
         py scripts/resume-indexing.py
         ```
   
   - **Bing Search Service** (Optional)
     - Required only if you want RFP responses to include web search results

   **Important:** Configure authentication between Document Intelligence and Storage:
   1. Create a managed identity for your Document Intelligence resource
   2. Grant it the "Storage Blob Data Reader" role on your storage account

4. **Configure environment variables**
   - Create a `.env` file in the root directory by copying the example file:
     ```sh
     cp example.env .env
     ```
   - Open the `.env` file and add the necessary environment variables as specified in the `example.env` file.
   - Make sure to restart the terminal window after making changes to the .env file 

### Running the Application Locally

1. Start the front-end:
   - Navigate to the `front-end` directory:
     ```sh
     cd front-end
     ```
   - Run the following command to start the front-end development server:
     ```sh
     npm start
     ```
   - The front-end should now be running at `http://localhost:3000`.

2. Start the back-end:
   - Ensure your virtual environment is activated (see step 2).
   - Run the following command to start the back-end server:
     ```sh
     python backend/app.py
     ```
   - The back-end should now be running at `http://localhost:5000`.
   - The back-end will attempt to authenticate to your Azure resources via the provides keys, but will fall back to DefaultAzureCredential if no key is found or key-based access is disabled due to your organization's policies. If this is the case, make sure to login to azure via installing the Azure CLI and running "az login".

## Usage


## Contributing

We welcome contributions to the RFP Accelerator! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

## Support

Reach out to dangiannone@microsoft.com for questions & support