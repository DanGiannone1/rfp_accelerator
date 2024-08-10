import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

const CopilotMode = ({ selectedRFP, currentSection, mockSections, onApproveSection }) => (
  <>
    <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
      Section Review
    </h2>
    <div className="flex-1 flex">
      <div className="w-1/2 pr-2">
        <h3 className="text-xl font-semibold mb-2 text-blue-400">Original Text</h3>
        <div className="bg-gray-700 bg-opacity-50 p-4 rounded-lg h-64 overflow-y-auto">
          {selectedRFP ? mockSections[currentSection].original : "Select an RFP to start"}
        </div>
      </div>
      <div className="w-1/2 pl-2">
        <h3 className="text-xl font-semibold mb-2 text-purple-400">Extracted Requirements</h3>
        <div className="bg-gray-700 bg-opacity-50 p-4 rounded-lg h-64 overflow-y-auto">
          {selectedRFP ? (
            mockSections[currentSection].extracted.map((req, index) => (
              <div key={index} className="flex items-center mb-2">
                <span className="flex-grow">{req.requirement}</span>
                {req.confidence > 0.8 ? (
                  <CheckCircle className="text-green-500 ml-2" size={20} />
                ) : (
                  <AlertCircle className="text-yellow-500 ml-2" size={20} />
                )}
              </div>
            ))
          ) : (
            "Select an RFP to view extracted requirements"
          )}
        </div>
      </div>
    </div>
    {selectedRFP && (
      <div className="mt-4 flex justify-end">
        <button
          onClick={onApproveSection}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Approve and Continue
        </button>
      </div>
    )}
  </>
);

export default CopilotMode;