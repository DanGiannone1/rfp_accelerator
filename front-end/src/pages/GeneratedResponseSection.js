import React from 'react';
import ReactMarkdown from 'react-markdown';

const GeneratedResponseSection = ({ generatedResponse }) => {
  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold mb-2 text-purple-400">Generated Response</h3>
      <div className="bg-gray-700 bg-opacity-50 rounded-lg p-4 h-64 overflow-y-auto">
        {generatedResponse ? (
          <ReactMarkdown className="prose prose-invert max-w-none">
            {generatedResponse}
          </ReactMarkdown>
        ) : (
          <p className="text-gray-400">Click "Generate Response" to create a response.</p>
        )}
      </div>
    </div>
  );
};

export default GeneratedResponseSection;