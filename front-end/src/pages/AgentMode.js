import React from 'react';
import { Loader } from 'lucide-react';

const Spinner = () => (
  <div className="flex items-center justify-center">
    <Loader className="animate-spin text-blue-400" size={36} />
  </div>
);

const ExtractionMessage = ({ message }) => (
  <div className="mt-4 p-3 bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-lg">
    <p className="text-yellow-400 text-center">{message}</p>
  </div>
);

const AgentMode = ({ selectedRFP, isExtracting, onStartExtraction, extractionMessage, extractionProgress }) => (
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
      <Spinner />
    )}
    {extractionMessage && <ExtractionMessage message={extractionMessage} />}
  </div>
);

export default AgentMode;