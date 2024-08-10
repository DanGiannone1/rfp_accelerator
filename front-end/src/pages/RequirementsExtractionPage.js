import React, { useState, useEffect } from 'react';
import { List } from 'lucide-react';
import RFPSelector from '../components/rfp/RFPSelector';
import AgentMode from './AgentMode';
import CopilotMode from './CopilotMode';
import ArtifactDownload from '../components/rfp/ArtifactDownload';

// Simple Toggle Component
const Toggle = ({ checked, onChange, label }) => (
  <div className="flex items-center justify-center mb-4">
    <span className="mr-2 text-gray-300 text-sm">{label}</span>
    <div 
      className={`w-14 h-7 flex items-center rounded-full p-1 cursor-pointer ${
        checked ? 'bg-blue-500' : 'bg-gray-300'
      }`}
      onClick={() => onChange(!checked)}
    >
      <div 
        className={`bg-white w-5 h-5 rounded-full shadow-md transform transition-transform duration-300 ease-in-out ${
          checked ? 'translate-x-7' : ''
        }`}
      />
    </div>
  </div>
);

const RequirementsExtractionPage = () => {
    const [isCopilotMode, setIsCopilotMode] = useState(false);
    const [selectedRFP, setSelectedRFP] = useState(null);
    const [currentSection, setCurrentSection] = useState(0);
    const [extractionProgress, setExtractionProgress] = useState(0);
    const [isExtracting, setIsExtracting] = useState(false);
    const [artifacts, setArtifacts] = useState([]);
  
    useEffect(() => {  
        fetchArtifacts();  
      }, []);  
  
    const fetchArtifacts = async () => {
      try {
        const response = await fetch(`http://localhost:5000/artifacts?rfp=${selectedRFP}&type=requirements`);
        if (!response.ok) {
          throw new Error('Failed to fetch artifacts');
        }
        const data = await response.json();
        setArtifacts(data.map(artifact => ({
          name: artifact.name,
          status: artifact.status || 'READY' // Assuming 'READY' as default status
        })));
      } catch (error) {
        console.error('Error fetching artifacts:', error);
        // Optionally set an error state or show a notification to the user
      }
    };

  const mockSections = [
    { 
      original: "Section 1 text...",
      extracted: [
        { requirement: "Requirement 1", confidence: 0.9 },
        { requirement: "Requirement 2", confidence: 0.7 },
      ]
    },
    // ... more sections
  ];

  const handleRFPSelect = (rfpName) => {
    setSelectedRFP(rfpName);
    setCurrentSection(0);
    setExtractionProgress(0);
    // Here you would start the extraction process
  };

  const handleApproveSection = () => {
    // Here you would save the approved section to the database
    setCurrentSection(currentSection + 1);
    setExtractionProgress(((currentSection + 1) / mockSections.length) * 100);
  };

  const handleStartExtraction = () => {
    if (!selectedRFP) {
      alert("Please select an RFP before starting the extraction process.");
      return;
    }
    setIsExtracting(true);
    // Simulate extraction process
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setExtractionProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setIsExtracting(false);
      }
    }, 500);
  };

  return (
    <div className="flex flex-col h-full pt-4">
      <div className="text-center mb-8">
        <div className="flex justify-center items-center mb-2">
          <List className="text-blue-400 mr-2" size={36} />
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Requirements Extraction
          </h1>
        </div>
        <p className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-400">
          Extract and review RFP requirements
        </p>
      </div>

      <div className="flex flex-1 px-4 pb-16">
        <div className="w-64 pr-4 flex flex-col space-y-4">
          <Toggle
            checked={isCopilotMode}
            onChange={setIsCopilotMode}
            label="Copilot Mode"
          />
          <RFPSelector
            selectedRFPs={selectedRFP}
            onSelectRFP={handleRFPSelect}
            multiSelect={false}
          />
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
            <h3 className="text-lg font-semibold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Extraction Progress
            </h3>
            <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${extractionProgress}%` }}
              ></div>
            </div>
            <p className="text-gray-300">{Math.round(extractionProgress)}% Complete</p>
          </div>
        </div>

        <div className="flex-1 px-4 flex flex-col">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-1 flex flex-col">
            {isCopilotMode ? (
              <CopilotMode 
                selectedRFP={selectedRFP}
                currentSection={currentSection}
                mockSections={mockSections}
                onApproveSection={handleApproveSection}
              />
            ) : (
              <AgentMode 
                selectedRFP={selectedRFP}
                isExtracting={isExtracting}
                onStartExtraction={handleStartExtraction}
              />
            )}
          </div>
        </div>

        <ArtifactDownload downloads={artifacts} />
      </div>
    </div>
  );
};

export default RequirementsExtractionPage;