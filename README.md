# RFP Accelerator - Transform Your Organization's Proposal Process

Responding to a Request for Proposal (RFP) or Request for Information (RFI) is a common task in a corporate setting. For most organizations, this is currently a cumbersome and time-consuming process involving multiple teams coordinating for weeks or even months at a time. 

Generative AI has the ability to transform the proposal response process from start to finish.


## Overview

The RFP Accelerator is an application that allows various operations to be performed against RFPs, leveraging the power of Generative AI to streamline and enhance the proposal process.

![RFP Accelerator Main Image](/images/main_ui.png)

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
| Upload | - Azure Blob Storage<br>- Azure Document Intelligence<br>- Azure OpenAI<br>- Azure Cosmos DB<br>- Managed identity between Document Intelligence and Blob Storage |
| Employee Matching | - Azure Blob Storage<br>- Azure Document Intelligence<br>- Azure OpenAI<br>- Azure Cosmos DB<br>- Azure AI Search |
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
     - Run the following command to create a virtual environment named `venv`:
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

3. **Configure environment variables**
   - Create a `.env` file in the root directory by copying the example file:
     ```sh
     cp example.env .env
     ```
   - Open the `.env` file in a text editor and add the necessary environment variables as specified in the `example.env` file.

### Running the Application

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

## Usage

[Add instructions on how to use the RFP Accelerator, including any API endpoints or user interface guidance.]

## Contributing

We welcome contributions to the RFP Accelerator! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

## Support