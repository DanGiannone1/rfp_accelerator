import React, { useState } from 'react';
import { Users } from 'lucide-react';
import RFPSelector from '../components/rfp/RFPSelector';
import SearchControls from '../components/EmployeeMatching/SearchControls';
import ResultsTable from '../components/EmployeeMatching/ResultsTable';
import ActionButtons from '../components/EmployeeMatching/ActionButtons';
import EnhancedResumes from '../components/EmployeeMatching/EnhancedResumes';
import ResumeViewer from '../components/EmployeeMatching/ResumeViewer';

const EmployeeMatchingPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [matchingResults, setMatchingResults] = useState([]);
  const [refineSearch, setRefineSearch] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRows, setSelectedRows] = useState([]);
  const [expandedRows, setExpandedRows] = useState({});
  const [enhancedResults, setEnhancedResults] = useState([]);
  const [pdfData, setPdfData] = useState(null);
  const [isWindowOpen, setIsWindowOpen] = useState(false);

  const handleRunMatching = async () => {
    if (!selectedRFP) {
      alert("Please select an RFP before running the matching process.");
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rfpName: selectedRFP,
          feedback: refineSearch,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setMatchingResults(data.results.map(result => ({
          ...result,
          location: `City ${Math.floor(Math.random() * 100)}`
        })));
      } else {
        alert(data.error || 'An error occurred during the search');
      }
    } catch (error) {
      console.error('Error during search:', error);
      alert('An error occurred during the search');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResumeClick = async (resumeName) => {
    if (!selectedRFP) {
      alert("Please select an RFP before viewing resumes.");
      return;
    }
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/resume?resumeName=' + resumeName, { 
        headers: { 'Access-Control-Allow-Origin': 'http://localhost:3001' }, 
        method: 'GET', 
        responseType: 'arraybuffer'
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setPdfData(url);
      setIsWindowOpen(true);
    } catch (error) {
      console.error('Error fetching document:', error);
      alert('An error occurred while fetching the resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnhanceResumes = async () => {
    const newEnhancedResults = selectedRows.map(resumeName => ({
      name: resumeName,
      enhancedResumeLink: `#${resumeName.replace('.docx', '')}_enhanced`
    }));
    setEnhancedResults(newEnhancedResults);
  };

  const handleDownloadResumes = async () => {
    for (const resumeName of selectedRows) {
      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/download?resumeName=${resumeName}`, {
          method: 'GET',
          headers: {
            'Access-Control-Allow-Origin': 'http://localhost:3001',
          },
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = resumeName;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } catch (error) {
        console.error('Error downloading document:', error);
        alert(`An error occurred while downloading ${resumeName}`);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex flex-col h-full pt-4">
      <div className="text-center mb-8 pb-2">
        <div className="flex justify-center items-center mb-2">
          <Users className="text-blue-400 mr-2" size={36} />
          <h1 className="text-4xl font-bold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Employee Matching
          </h1>
        </div>
        <p className="text-lg font-semibold mt-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-400">
          Find the right people for your proposal
        </p>
      </div>
      <div className="flex flex-1 px-4 pb-16">
        <div className="w-64 pr-4 flex flex-col space-y-4">
          <RFPSelector
            selectedRFPs={selectedRFP}
            onSelectRFP={setSelectedRFP}
            multiSelect={false}
          />
          <SearchControls
            onRunMatching={handleRunMatching}
            refineSearch={refineSearch}
            setRefineSearch={setRefineSearch}
          />
        </div>

        <div className="flex-1 px-4 flex flex-col">
          <ResultsTable
            isLoading={isLoading}
            matchingResults={matchingResults}
            selectedRows={selectedRows}
            setSelectedRows={setSelectedRows}
            expandedRows={expandedRows}
            setExpandedRows={setExpandedRows}
            onResumeClick={handleResumeClick}
          />
          
          <ActionButtons
            selectedRows={selectedRows}
            onEnhanceResumes={handleEnhanceResumes}
            onDownloadResumes={handleDownloadResumes}
          />

          <EnhancedResumes
            enhancedResults={enhancedResults}
            onResumeClick={handleResumeClick}
          />

          <ResumeViewer
            pdfData={pdfData}
            isWindowOpen={isWindowOpen}
            onClose={() => setIsWindowOpen(false)}
          />
        </div>
      </div>
    </div>
  );
};

export default EmployeeMatchingPage;