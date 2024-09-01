import React from 'react';

const CurrentRequirementSection = ({ currentRequirement }) => {
  if (!currentRequirement) {
    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2 text-blue-400">Current Requirement</h3>
        <p className="text-gray-400">No requirement selected</p>
      </div>
    );
  }

  return (
    <div className="mb-4">
      <h3 className="text-lg font-semibold mb-2 text-blue-400">Current Requirement</h3>
      <div className="space-y-2 text-white">
        <p><strong>Section Name:</strong> {currentRequirement.section_name}</p>
        <p><strong>Page Number:</strong> {currentRequirement.page_number}</p>
        <p><strong>Section Number:</strong> {currentRequirement.section_number}</p>
        <p><strong>Content:</strong> {currentRequirement.content}</p>
      </div>
    </div>
  );
};

export default CurrentRequirementSection;