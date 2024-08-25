import React from 'react';
import { Zap, Download } from 'lucide-react';

const ActionButtons = ({ selectedRows, onEnhanceResumes, onDownloadResumes }) => {
  const isDisabled = selectedRows.length === 0;

  return (
    <div className="mt-4 flex justify-end space-x-4 mb-4">
      <button
        onClick={onEnhanceResumes}
        disabled={isDisabled}
        className={`bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 flex items-center ${
          isDisabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <Zap className="mr-2" size={20} />
        Enhance Selected Resumes
      </button>
      <button
        onClick={onDownloadResumes}
        disabled={isDisabled}
        className={`bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 flex items-center ${
          isDisabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <Download className="mr-2" size={20} />
        Download
      </button>
    </div>
  );
};

export default ActionButtons;