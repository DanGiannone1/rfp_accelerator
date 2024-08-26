# RFP Accelerator - Transform Your Organization's Proposal Process

Responding to a Request for Proposal (RFP) or Request for Information (RFI) is a common task in a corporate setting. For most organizations, this is currently a cumbersome and time-consuming process involving multiple teams coordinating for weeks or even months at a time. 

Generative AI has the ability to transform the proposal response process from start to finish.

![RFP Accelerator Main Image](/images/main_v2.png)

## Overview

The RFP Accelerator provides a set of APIs and an associated front-end application that allows various operations to be performed against RFPs, leveraging the power of Generative AI to streamline and enhance the proposal process.

## Features

- Upload - Intelligent, AI-powered document chunking and "RFP at a glance"
- Employee Matching - Find the right employees for a given RFP based on skillset or other attributes
- RFP Analyzer - Ask questions about the RFP
- Requirements Extraction - extract requirements or any other structured data from the RFP
- Response builder - Start building your response to the RFP

## Setup

### Prerequisites

Each module of the accelerator has a different set of prerequisite services. 

1. Upload - Azure Blob Storage, Azure Document Intelligence, Azure OpenAI, Azure Cosmos DB, managed identity between Doc Intelligence and Blob Storage. 
2. Employee Matching - Azure Blob Storage, Azure Document Intelligence, Azure OpenAI, Azure Cosmos DB, Azure AI Search
3. RFP Analyzer - Azure Cosmos DB, Azure OpenAI
4. Requirements Extraction - Azure Cosmos DB, Azure OpenAI 
5. Response Builder - Azure Cosmos DB, Azure OpenAI, Azure AI Search

See the readme of each module for detailed documentation and setup instructions. 

### Installation

1. **Clone the repository**
   ```
   git clone https://github.com/your-username/rfp-accelerator.git
   cd rfp-accelerator
   ```

2. **Install dependencies**
   - Ensure you have [Node.js](https://nodejs.org/) installed.
   - Install front-end dependencies:
     ```
     npm install
     ```
   - Create a new Python virtual environment and install back-end dependencies:
     ```
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     pip install -r requirements.txt
     ```

3. **Configure environment variables**
   - Create a `.env` file in the root directory.
   - Add the necessary environment variables as specified in `.env.example`.

### Running the Application

1. Start the front-end:
   ```
   npm start
   ```

2. Start the back-end:
   ```
   python app.py
   ```

## Usage

[Add instructions on how to use the RFP Accelerator, including any API endpoints or user interface guidance.]

## Contributing

We welcome contributions to the RFP Accelerator! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License



## Support

