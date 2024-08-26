import React, { useState, useEffect } from 'react';
import { List } from 'lucide-react';
import RFPSelector from '../components/rfp/RFPSelector';
import AgentMode from './AgentMode';
import CopilotMode from './CopilotMode';


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

const EnhancedProgressBar = ({ progress }) => (
  <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4 overflow-hidden">
    <div 
      className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out relative"
      style={{ width: `${progress}%` }}
    >
      <div className="absolute top-0 right-0 bottom-0 left-0 bg-blue-400 animate-pulse opacity-75 rounded-full" />
    </div>
  </div>
);

const RequirementsExtractionPage = () => {
  const [isCopilotMode, setIsCopilotMode] = useState(false);
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [currentSection, setCurrentSection] = useState(0);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionMessage, setExtractionMessage] = useState('');
  const [mockSections, setMockSections] = useState([]);

  useEffect(() => {
      if (isExtracting) {
          const interval = setInterval(checkExtractionProgress, 5000);
          return () => clearInterval(interval);
      }
  }, [selectedRFP, isExtracting]);  

  useEffect(() => {
      if (selectedRFP) {
          fetchMockSections(selectedRFP);
      }
  }, [selectedRFP]);

  const handleRFPSelect = async (rfpName) => {
      setSelectedRFP(rfpName);
      setCurrentSection(0);
      setExtractionMessage('');
      
      // Query for progress when an RFP is selected
      try {
          const response = await fetch(`http://localhost:5000/extraction-progress?rfp_name=${rfpName}`);
          const data = await response.json();
          setExtractionProgress(data.progress);
          setIsExtracting(data.progress > 0 && data.progress < 100);
      } catch (error) {
          console.error('Error fetching extraction progress:', error);
      }
  };

  const handleStartExtraction = async () => {
      if (!selectedRFP) {
          alert("Please select an RFP before starting the extraction process.");
          return;
      }
  
      setIsExtracting(true);
      setExtractionMessage('Starting extraction process...');
      try {
          const response = await fetch('http://localhost:5000/start-extraction', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ rfp_name: selectedRFP }),
          });

          const data = await response.json();
          setExtractionMessage(data.message);
      } catch (error) {
          console.error('Error starting extraction:', error);
          setExtractionMessage('An error occurred while starting the extraction process.');
          setIsExtracting(false);
      }
  };

  const checkExtractionProgress = async () => {
      if (!selectedRFP) return;

      try {
          const response = await fetch(`http://localhost:5000/extraction-progress?rfp_name=${selectedRFP}`);
          const data = await response.json();
          setExtractionProgress(data.progress);
          
          if (data.progress >= 100) {
              setIsExtracting(false);
              setExtractionMessage('Extraction completed successfully!');
          }
      } catch (error) {
          console.error('Error checking extraction progress:', error);
      }
  };

  const fetchMockSections = async (rfpName) => {
      // In a real scenario, you would fetch the actual sections from the backend
      // For now, we'll use mock data
      setMockSections([
          { 
              original: "Section 1 text...",
              extracted: [
                  { requirement: "Requirement 1", confidence: 0.9 },
                  { requirement: "Requirement 2", confidence: 0.7 },
              ]
          },
          { 
              original: "Section 2 text...",
              extracted: [
                  { requirement: "Requirement 3", confidence: 0.8 },
                  { requirement: "Requirement 4", confidence: 0.6 },
              ]
          },
      ]);
  };

  const handleApproveSection = () => {
      // In a real scenario, you would save the approved section to the backend
      setCurrentSection(prevSection => {
          const nextSection = prevSection + 1;
          if (nextSection < mockSections.length) {
              return nextSection;
          } else {
              setExtractionMessage('All sections reviewed!');
              return prevSection;
          }
      });
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
                      <EnhancedProgressBar progress={extractionProgress} />
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
                              extractionMessage={extractionMessage}
                              extractionProgress={extractionProgress}
                          />
                      )}
                  </div>
              </div>
          </div>
      </div>
  );
};

export default RequirementsExtractionPage;