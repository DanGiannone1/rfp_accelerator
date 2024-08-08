import React, { useState } from 'react';
import { FileText, ChevronRight, ChevronLeft } from 'lucide-react';

const ResponseBuilderPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [currentRequirement, setCurrentRequirement] = useState(0);
  const [generatedResponse, setGeneratedResponse] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiInstruction, setAiInstruction] = useState('');

  // Mock data - replace with actual data from your backend
  const rfps = [
    { id: 1, name: 'RFP1' },
    { id: 2, name: 'RFP2' },
    { id: 3, name: 'RFP3' },
  ];

  const mockRequirements = [
    { id: 1, text: "The system must be able to handle 1000 concurrent users." },
    { id: 2, text: "Data must be encrypted at rest and in transit." },
    { id: 3, text: "The solution should integrate with our existing CRM system." },
  ];

  const handleRFPSelect = (rfpId) => {
    setSelectedRFP(rfpId);
    setCurrentRequirement(0);
    setGeneratedResponse('');
  };

  const handleGenerateResponse = () => {
    setIsGenerating(true);
    // Simulate API call to generate response
    setTimeout(() => {
      setGeneratedResponse(`Here's our proposed solution for the requirement: "${mockRequirements[currentRequirement].text}"...`);
      setIsGenerating(false);
    }, 2000);
  };

  const handleNextRequirement = () => {
    if (currentRequirement < mockRequirements.length - 1) {
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
    <div className="flex flex-col h-full pt-4">
      <div className="text-center mb-8">
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

      <div className="flex flex-1 px-4 pb-16">
        {/* Left sidebar */}
        <div className="w-64 pr-4">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg mb-4">
            <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Select RFP
            </h2>
            <div className="space-y-2">
              {rfps.map(rfp => (
                <button
                  key={rfp.id}
                  onClick={() => handleRFPSelect(rfp.id)}
                  className={`w-full text-left py-2 px-4 rounded-lg transition duration-300 ${
                    selectedRFP === rfp.id ? 'bg-blue-600' : 'bg-gray-700 bg-opacity-50 hover:bg-opacity-75'
                  }`}
                >
                  {rfp.name}
                </button>
              ))}
            </div>
          </div>
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              What do you want to tell the AI?
            </h2>
            <textarea
              className="w-full h-24 bg-gray-700 bg-opacity-50 rounded-lg p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={aiInstruction}
              onChange={(e) => setAiInstruction(e.target.value)}
              placeholder="Enter instructions for the AI..."
            ></textarea>
          </div>
        </div>

        {/* Main content area */}
        {selectedRFP && (
          <div className="flex-1 px-4 flex flex-col">
            <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-1 flex flex-col">
              <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                Requirement Response
              </h2>
              <div className="mb-4 bg-gray-700 bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-xl font-semibold mb-2 text-blue-400">Current Requirement</h3>
                <p>{mockRequirements[currentRequirement].text}</p>
              </div>
              <div className="flex-1 bg-gray-700 bg-opacity-50 p-4 rounded-lg mb-4">
                <h3 className="text-xl font-semibold mb-2 text-purple-400">Generated Response</h3>
                {generatedResponse ? (
                  <p>{generatedResponse}</p>
                ) : (
                  <p className="text-gray-400">Click "Generate Response" to create a response.</p>
                )}
              </div>
              <div className="flex justify-between items-center">
                <button
                  onClick={handlePreviousRequirement}
                  disabled={currentRequirement === 0}
                  className={`flex items-center ${
                    currentRequirement === 0 ? 'text-gray-500 cursor-not-allowed' : 'text-blue-400 hover:text-blue-300'
                  }`}
                >
                  <ChevronLeft size={20} />
                  Previous
                </button>
                <button
                  onClick={handleGenerateResponse}
                  disabled={isGenerating}
                  className={`bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600 text-white font-bold py-2 px-4 rounded ${
                    isGenerating ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isGenerating ? 'Generating...' : 'Generate Response'}
                </button>
                <button
                  onClick={handleNextRequirement}
                  disabled={currentRequirement === mockRequirements.length - 1}
                  className={`flex items-center ${
                    currentRequirement === mockRequirements.length - 1 ? 'text-gray-500 cursor-not-allowed' : 'text-blue-400 hover:text-blue-300'
                  }`}
                >
                  Next
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponseBuilderPage;