import React from 'react';

const AgentMode = ({ selectedRFP, isExtracting, onStartExtraction }) => (
  <div className="flex-1 flex flex-col items-center justify-center">
    <p className="text-gray-300 mb-4">
      The AI agent will automatically extract requirements from all sections.
    </p>
    {!isExtracting ? (
      <button
        onClick={onStartExtraction}
        className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-6 rounded-full transition duration-300"
        disabled={!selectedRFP}
      >
        {selectedRFP ? "Start Extraction" : "Select an RFP to start"}
      </button>
    ) : (
      <p className="text-yellow-400">Extraction in progress...</p>
    )}
  </div>
);

export default AgentMode;