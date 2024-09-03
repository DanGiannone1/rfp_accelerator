import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, ChevronLeft, ChevronRight, Loader } from 'lucide-react';

const RequirementCard = ({ requirement, onToggle }) => {
  return (
    <div className="bg-gray-700 rounded-lg p-4 mb-4 shadow-lg transition-all duration-300 hover:shadow-xl">
      <div className="flex justify-between items-center mb-2">
        <span className="font-semibold text-blue-300">
          {requirement.section_name} - {requirement.section_number}
        </span>
        <span className="text-gray-400">Page {requirement.page_number}</span>
      </div>
      <p className="text-white mb-4">{requirement.content}</p>
      <div className="flex items-center justify-end">
        <div className="flex space-x-2">
          <button
            onClick={() => onToggle('no')}
            className={`p-2 rounded-full transition-colors duration-300 group relative ${
              requirement.is_requirement === 'no'
                ? 'bg-red-500 text-white'
                : 'bg-gray-600 text-gray-300 hover:bg-red-400'
            }`}
          >
            <XCircle size={24} />
            <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs font-bold text-white bg-gray-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              This is not a requirement
            </span>
          </button>
          <button
            onClick={() => onToggle('yes')}
            className={`p-2 rounded-full transition-colors duration-300 group relative ${
              requirement.is_requirement === 'yes'
                ? 'bg-green-500 text-white'
                : 'bg-gray-600 text-gray-300 hover:bg-green-400'
            }`}
          >
            <CheckCircle size={24} />
            <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs font-bold text-white bg-gray-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              This is a requirement
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};

const CopilotMode = ({ selectedRFP, currentSection, onApproveSection, extractionProgress, reviewProgress, onUpdateProgress }) => {
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [showSuccessIndicator, setShowSuccessIndicator] = useState(false);
  const [isSectionReviewed, setIsSectionReviewed] = useState(false);

  useEffect(() => {
    if (selectedRFP) {
      fetchSections(selectedRFP);
    }
  }, [selectedRFP]);

  useEffect(() => {
    if (sections[currentSection]) {
      setIsSectionReviewed(sections[currentSection].reviewed || false);
    }
  }, [currentSection, sections]);

  const fetchSections = async (rfpName) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/get-rfp-sections?rfp_name=${rfpName}`);
      if (!response.ok) {
        throw new Error('Failed to fetch RFP sections');
      }
      const data = await response.json();
      setSections(data.sections);
      onApproveSection(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleRequirement = (reqIndex, newStatus) => {
    setSections(prevSections => {
      const newSections = [...prevSections];
      const section = {...newSections[currentSection]};
      const requirement = {...section.requirements[reqIndex], is_requirement: newStatus};
      section.requirements[reqIndex] = requirement;
      newSections[currentSection] = section;
      return newSections;
    });
  };

  const handleApproveAndContinue = async () => {
    setIsUpdating(true);
    try {
      const updatedRequirements = {
        analysis: "Requirements updated by user",
        output: sections[currentSection].requirements.map(req => ({
          section_name: req.section_name,
          page_number: req.page_number,
          section_number: req.section_number,
          content: req.content,
          is_requirement: req.is_requirement
        }))
      };

      const response = await fetch('http://localhost:5000/update-requirements', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rfp_name: selectedRFP,
          section_id: sections[currentSection].section_id,
          requirements: updatedRequirements,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update requirements');
      }

      // Fetch updated progress
      await onUpdateProgress();

      setShowSuccessIndicator(true);
      setTimeout(() => {
        setShowSuccessIndicator(false);
      }, 5000);

      // Mark the current section as reviewed
      setSections(prevSections => {
        const newSections = [...prevSections];
        newSections[currentSection] = {...newSections[currentSection], reviewed: true};
        return newSections;
      });
      setIsSectionReviewed(true);

      // Move to the next section
      onApproveSection(currentSection + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handlePreviousSection = () => {
    if (currentSection > 0) {
      onApproveSection(currentSection - 1);
    }
  };

  const handleNextSection = () => {
    if (currentSection < sections.length - 1) {
      onApproveSection(currentSection + 1);
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;
  if (error) return <div className="text-center py-10 text-red-500">Error: {error}</div>;
  if (!sections.length) return <div className="text-center py-10">No sections available</div>;

  const currentSectionData = sections[currentSection] || {};

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-2xl font-semibold mb-2 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        Section Review: {currentSectionData.section_id || 'Unknown Section'}
      </h2>
      <div className="flex flex-1">
        <div className="w-1/2 pr-4">
          <h3 className="text-xl font-semibold mb-2 text-blue-400 sticky top-0 bg-gray-800 py-2 z-10">Original Text</h3>
          <div className="h-[calc(100vh-420px)] overflow-y-auto pr-2 bg-gray-700 rounded-lg">
            <div className="p-4 whitespace-pre-wrap">
              {currentSectionData.content || 'No content available'}
            </div>
          </div>
        </div>
        <div className="w-1/2 pl-4">
          <h3 className="text-xl font-semibold mb-2 text-purple-400 sticky top-0 bg-gray-800 py-2 z-10">Extracted Requirements</h3>
          <div className="h-[calc(100vh-420px)] overflow-y-auto pr-2">
            {currentSectionData.requirements && currentSectionData.requirements.length > 0 ? (
              currentSectionData.requirements.map((req, index) => (
                <RequirementCard
                  key={index}
                  requirement={req}
                  onToggle={(newStatus) => toggleRequirement(index, newStatus)}
                />
              ))
            ) : (
              <div className="text-center py-10 text-gray-400">No requirements extracted</div>
            )}
          </div>
        </div>
      </div>
      <div className="flex justify-between items-center bg-gray-800 p-3 rounded-lg">
        <button
          onClick={handlePreviousSection}
          disabled={currentSection === 0}
          className="flex items-center text-blue-400 hover:text-blue-300 disabled:text-gray-600 disabled:cursor-not-allowed"
        >
          <ChevronLeft size={20} />
          <span className="ml-1">Previous</span>
        </button>
        <div className="flex items-center">
          {showSuccessIndicator ? (
            <>
              <CheckCircle className="text-green-500 mr-2" size={20} />
              <span className="text-green-300 text-sm">Previous section updated successfully!</span>
            </>
          ) : isSectionReviewed ? (
            <>
              <CheckCircle className="text-green-500 mr-2" size={20} />
              <span className="text-green-300 text-sm">Section Validated</span>
            </>
          ) : (
            <>
              <AlertCircle className="text-yellow-500 mr-2" size={20} />
              <span className="text-gray-300 text-sm">Validate the requirements</span>
            </>
          )}
        </div>
        <button
          onClick={handleNextSection}
          disabled={currentSection === sections.length - 1}
          className="flex items-center text-blue-400 hover:text-blue-300 disabled:text-gray-600 disabled:cursor-not-allowed"
        >
          <span className="mr-1">Next</span>
          <ChevronRight size={20} />
        </button>
      </div>
      <div className="mt-2 flex justify-center items-center">
        <button
          onClick={handleApproveAndContinue}
          disabled={currentSection === sections.length - 1 || isUpdating}
          className={`
            bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded
            disabled:opacity-50 transition-colors duration-300 flex items-center
            ${isUpdating ? 'cursor-not-allowed' : ''}
          `}
        >
          {isUpdating ? (
            <>
              <Loader className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              Updating...
            </>
          ) : (
            'Approve and Continue'
          )}
        </button>
      </div>
      {error && (
        <div className="mt-2 text-red-500 text-center">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default CopilotMode;