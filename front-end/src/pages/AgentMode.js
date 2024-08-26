import React from 'react';
import { Loader, CheckCircle } from 'lucide-react';

const Spinner = () => (
  <div className="flex items-center justify-center">
    <Loader className="animate-spin text-blue-400" size={36} />
  </div>
);

const ExtractionMessage = ({ message, isSuccess }) => (
  <div className={`mt-4 p-4 rounded-lg flex items-center justify-center transition-all duration-300 ${
    isSuccess 
      ? 'bg-green-600 bg-opacity-20 border border-green-500 text-green-400 animate-pulse'
      : 'bg-yellow-900 bg-opacity-20 border border-yellow-700 text-yellow-400'
  }`}>
    {isSuccess && <CheckCircle className="mr-2" size={24} />}
    <p className="text-center font-semibold">{message}</p>
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
        className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-6 rounded-full transition duration-300 transform hover:scale-105"
        disabled={!selectedRFP}
      >
        {selectedRFP ? "Start Extraction" : "Select an RFP to start"}
      </button>
    ) : (
      <Spinner />
    )}
    {extractionMessage && (
      <ExtractionMessage 
        message={extractionMessage} 
        isSuccess={extractionMessage.toLowerCase().includes('completed successfully')}
      />
    )}
    {isExtracting && (
      <p className="text-gray-300 mt-4">
        Extraction in progress: {Math.round(extractionProgress)}% complete
      </p>
    )}
  </div>
);

export default AgentMode;