import React from 'react';

const CurrentRequirementSection = ({ currentRequirement }) => {
  if (!currentRequirement) {
    return (
      <div className="bg-gray-700 rounded-lg p-4 mb-4 shadow-lg">
        <h3 className="text-xl font-semibold mb-2 text-blue-400">Current Requirement</h3>
        <p className="text-gray-400">No requirement selected</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-700 rounded-lg p-4 mb-4 shadow-lg">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-xl font-semibold text-blue-400">
          {currentRequirement.section_name} - {currentRequirement.section_number}
        </h3>
        <span className="text-gray-400">Page {currentRequirement.page_number}</span>
      </div>
      <p className="text-white">{currentRequirement.content}</p>
    </div>
  );
};

export default CurrentRequirementSection;