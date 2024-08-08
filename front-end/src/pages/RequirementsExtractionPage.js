import React, { useState } from 'react';
import { List, CheckCircle, AlertCircle } from 'lucide-react';

const RequirementsExtractionPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [currentSection, setCurrentSection] = useState(0);
  const [extractionProgress, setExtractionProgress] = useState(0);

  // Mock data - replace with actual data from your backend
  const rfps = [
    { id: 1, name: 'RFP1' },
    { id: 2, name: 'RFP2' },
    { id: 3, name: 'RFP3' },
  ];

  const mockSections = [
    { 
      original: "Section 1 text...",
      extracted: [
        { requirement: "Requirement 1", confidence: 0.9 },
        { requirement: "Requirement 2", confidence: 0.7 },
      ]
    },
    // ... more sections
  ];

  const handleRFPSelect = (rfpId) => {
    setSelectedRFP(rfpId);
    setCurrentSection(0);
    setExtractionProgress(0);
    // Here you would start the extraction process
  };

  const handleApproveSection = () => {
    // Here you would save the approved section to the database
    setCurrentSection(currentSection + 1);
    setExtractionProgress(((currentSection + 1) / mockSections.length) * 100);
  };

  return (
    <div className="flex flex-col h-full pt-4">
      <div className="text-center mb-8">
        <div className="flex justify-center items-center mb-2">
          <List className="text-blue-400 mr-2" size={36} />
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Requirements Extraction
          </h1>
        </div>
        <p className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-400">
          Extract and review RFP requirements
        </p>
      </div>

      <div className="flex flex-1 px-4 pb-16">
        {/* Left sidebar */}
        <div className="w-64 pr-4">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
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
          {selectedRFP && (
            <div className="mt-4 bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
              <h3 className="text-lg font-semibold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                Extraction Progress
              </h3>
              <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full" 
                  style={{ width: `${extractionProgress}%` }}
                ></div>
              </div>
              <p className="text-gray-300">{Math.round(extractionProgress)}% Complete</p>
            </div>
          )}
        </div>

        {/* Main content area */}
        {selectedRFP && (
          <div className="flex-1 px-4 flex flex-col">
            <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-1 flex flex-col">
              <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                Section Review
              </h2>
              <div className="flex-1 flex">
                <div className="w-1/2 pr-2">
                  <h3 className="text-xl font-semibold mb-2 text-blue-400">Original Text</h3>
                  <div className="bg-gray-700 bg-opacity-50 p-4 rounded-lg h-64 overflow-y-auto">
                    {mockSections[currentSection].original}
                  </div>
                </div>
                <div className="w-1/2 pl-2">
                  <h3 className="text-xl font-semibold mb-2 text-purple-400">Extracted Requirements</h3>
                  <div className="bg-gray-700 bg-opacity-50 p-4 rounded-lg h-64 overflow-y-auto">
                    {mockSections[currentSection].extracted.map((req, index) => (
                      <div key={index} className="flex items-center mb-2">
                        <span className="flex-grow">{req.requirement}</span>
                        {req.confidence > 0.8 ? (
                          <CheckCircle className="text-green-500 ml-2" size={20} />
                        ) : (
                          <AlertCircle className="text-yellow-500 ml-2" size={20} />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleApproveSection}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  Approve and Continue
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RequirementsExtractionPage;