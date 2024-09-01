import React, { useState, useEffect } from 'react';
import { FileText, ChevronRight, ChevronLeft, Loader } from 'lucide-react';
import RFPSelector from '../components/rfp/RFPSelector';
import ReactMarkdown from 'react-markdown';

const ResponseBuilderPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [currentRequirement, setCurrentRequirement] = useState(0);
  const [requirements, setRequirements] = useState([]);
  const [generatedResponse, setGeneratedResponse] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiInstruction, setAiInstruction] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRFPSelect = (rfpName) => {
    setSelectedRFP(rfpName);
    setCurrentRequirement(0);
    setGeneratedResponse('');
    setError(null);
    fetchRequirements(rfpName);
  };

  const fetchRequirements = async (rfpName) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/get-requirements?rfp_name=${rfpName}`);
      if (!response.ok) {
        throw new Error('Failed to fetch requirements');
      }
      const data = await response.json();
      setRequirements(data.requirements);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching requirements:', error);
      setError('Failed to fetch requirements. Please try again.');
      setIsLoading(false);
    }
  };

  const handleGenerateResponse = async () => {
    if (!selectedRFP || !requirements[currentRequirement]) return;

    setIsGenerating(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/respond-to-requirement', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requirement: requirements[currentRequirement]?.content,
          user_message: aiInstruction,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let generatedContent = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        generatedContent += chunk;
        setGeneratedResponse(generatedContent);
      }
    } catch (error) {
      console.error('Error generating response:', error);
      setError('Failed to generate response. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNextRequirement = () => {
    if (currentRequirement < requirements.length - 1) {
      setCurrentRequirement(currentRequirement + 1);
      setGeneratedResponse('');
    }
  };

  const handlePreviousRequirement = () => {
    if (currentRequirement > 0) {
      setCurrentRequirement(currentRequirement - 1);
      setGeneratedResponse('');
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <div className="text-center mb-8 pt-4">
        <div className="flex justify-center items-center mb-2">
          <FileText className="text-blue-400 mr-2" size={36} />
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Response Builder
          </h1>
        </div>
        <p className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-400">
          Generate and refine responses to RFP requirements
        </p>
      </div>

      <div className="flex flex-1 px-4 pb-4 overflow-hidden">
        <div className="w-64 pr-4 flex flex-col space-y-4 overflow-y-auto">
          <RFPSelector
            selectedRFPs={selectedRFP}
            onSelectRFP={handleRFPSelect}
            multiSelect={false}
          />
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-3 text-blue-400">
              What do you want to tell the AI?
            </h2>
            <textarea
              className="w-full h-24 bg-gray-700 bg-opacity-50 rounded-lg p-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={aiInstruction}
              onChange={(e) => setAiInstruction(e.target.value)}
              placeholder="Enter instructions for the AI..."
            ></textarea>
          </div>
        </div>

        <div className="flex-1 px-4 flex flex-col overflow-hidden">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-1 flex flex-col overflow-hidden">
            <h2 className="text-2xl font-semibold mb-4 text-blue-400">
              Requirement Response
            </h2>
            {isLoading ? (
              <div className="flex-1 flex items-center justify-center">
                <Loader className="animate-spin text-blue-400" size={48} />
              </div>
            ) : error ? (
              <div className="flex-1 flex items-center justify-center text-red-400">
                {error}
              </div>
            ) : (
              <>
                <div className="mb-4 bg-gray-700 bg-opacity-50 p-4 rounded-lg">
                  <h3 className="text-xl font-semibold mb-2 text-blue-400">Current Requirement</h3>
                  {selectedRFP && requirements[currentRequirement] ? (
                    <p className="text-white">
                      <strong>Section Name:</strong> {requirements[currentRequirement].section_name}<br />
                      <strong>Page Number:</strong> {requirements[currentRequirement].page_number}<br />
                      <strong>Section Number:</strong> {requirements[currentRequirement].section_number}<br />
                      <strong>Content:</strong> {requirements[currentRequirement].content}
                    </p>
                  ) : (
                    <p className="text-gray-400">Select an RFP to view requirements</p>
                  )}
                </div>
                <div className="flex-1 bg-gray-700 bg-opacity-50 p-4 rounded-lg mb-4 overflow-y-auto">
                  <h3 className="text-xl font-semibold mb-2 text-purple-400">Generated Response</h3>
                  {generatedResponse ? (
                    <ReactMarkdown 
                      className="prose prose-invert max-w-none"
                      components={{
                        h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
                        h2: ({node, ...props}) => <h2 className="text-xl font-bold mt-3 mb-2" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-lg font-bold mt-2 mb-1" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-2" {...props} />,
                        li: ({node, ...props}) => <li className="mb-1" {...props} />,
                        a: ({node, ...props}) => <a className="text-blue-400 hover:underline" {...props} />,
                        code: ({node, inline, ...props}) => 
                          inline ? (
                            <code className="bg-gray-800 rounded px-1" {...props} />
                          ) : (
                            <code className="block bg-gray-800 rounded p-2 my-2 overflow-x-auto" {...props} />
                          ),
                      }}
                    >
                      {generatedResponse}
                    </ReactMarkdown>
                  ) : (
                    <p className="text-gray-400">
                      {selectedRFP ? "Click \"Generate Response\" to create a response." : "Select an RFP to generate responses"}
                    </p>
                  )}
                </div>
                <div className="flex justify-between items-center mt-4">
                  <button
                    onClick={handlePreviousRequirement}
                    disabled={!selectedRFP || currentRequirement === 0 || isGenerating}
                    className={`flex items-center ${
                      !selectedRFP || currentRequirement === 0 || isGenerating
                        ? 'text-gray-500 cursor-not-allowed'
                        : 'text-blue-400 hover:text-blue-300'
                    }`}
                  >
                    <ChevronLeft size={20} />
                    Previous
                  </button>
                  <button
                    onClick={handleGenerateResponse}
                    disabled={isGenerating || !selectedRFP || !requirements.length}
                    className={`bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ${
                      isGenerating || !selectedRFP || !requirements.length ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {isGenerating ? (
                      <>
                        <Loader className="animate-spin mr-2 inline" size={20} />
                        Generating...
                      </>
                    ) : (
                      'Generate Response'
                    )}
                  </button>
                  <button
                    onClick={handleNextRequirement}
                    disabled={!selectedRFP || currentRequirement === requirements.length - 1 || isGenerating}
                    className={`flex items-center ${
                      !selectedRFP || currentRequirement === requirements.length - 1 || isGenerating
                        ? 'text-gray-500 cursor-not-allowed'
                        : 'text-blue-400 hover:text-blue-300'
                    }`}
                  >
                    Next
                    <ChevronRight size={20} />
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseBuilderPage;