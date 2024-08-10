import React from 'react';
import { FileText, Check } from 'lucide-react';
import { useRFPList } from './RFPListContext';

const RFPSelector = ({ selectedRFPs, onSelectRFP, multiSelect = false }) => {
  const { rfps, isLoading } = useRFPList();

  const handleSelect = (rfpName) => {
    if (multiSelect) {
      onSelectRFP(prev => 
        prev.includes(rfpName) ? prev.filter(name => name !== rfpName) : [...prev, rfpName]
      );
    } else {
      onSelectRFP(rfpName);
    }
  };

  return (
    <div className="bg-gray-800 bg-opacity-60 rounded-xl p-4 shadow-lg flex flex-col border border-gray-700" style={{ height: '300px' }}>
      <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        Select RFP{multiSelect ? 's' : ''}
      </h2>
      <div className="space-y-2 overflow-y-auto flex-grow pr-2" style={{ maxHeight: 'calc(100% - 40px)' }}>
        {isLoading ? (
          <p className="text-gray-400">Loading RFPs...</p>
        ) : rfps.length === 0 ? (
          <p className="text-gray-400">No RFPs available</p>
        ) : (
          rfps.map(rfp => (
            <button
              key={rfp.name}
              onClick={() => handleSelect(rfp.name)}
              className={`w-full text-left py-2 px-4 rounded-lg transition duration-300 flex items-center justify-between ${
                (multiSelect ? selectedRFPs.includes(rfp.name) : selectedRFPs === rfp.name)
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 bg-opacity-40 hover:bg-opacity-60 text-gray-300 hover:text-white'
              }`}
              title={rfp.name}
            >
              <div className="flex items-center overflow-hidden">
                <FileText size={16} className="mr-2 flex-shrink-0" />
                <span className="truncate">{rfp.name}</span>
              </div>
              {(multiSelect ? selectedRFPs.includes(rfp.name) : selectedRFPs === rfp.name) && (
                <Check size={16} className="flex-shrink-0 ml-2" />
              )}
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default RFPSelector;