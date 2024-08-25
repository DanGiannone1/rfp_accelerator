import React, { useState } from 'react';
import { FileText, Users, ExternalLink, Briefcase, Star, Zap, ChevronDown, ChevronRight } from 'lucide-react';
import RFPSelector from '../components/rfp/RFPSelector';

const EmployeeMatchingPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [matchingResults, setMatchingResults] = useState([]);
  const [refineSearch, setRefineSearch] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRows, setSelectedRows] = useState([]);
  const [expandedRows, setExpandedRows] = useState({});
  const [enhancedResults, setEnhancedResults] = useState([]);

  const handleRFPSelect = (rfpName) => {
    setSelectedRFP(rfpName);
  };

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
          location: `City ${Math.floor(Math.random() * 100)}`,
          relevantProjects: Math.floor(Math.random() * 10) + 1
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

  const handleEnhanceResumes = async () => {
    const newEnhancedResults = selectedRows.map(resumeName => ({
      name: resumeName,
      enhancedResumeLink: `#${resumeName.replace('.docx', '')}_enhanced`
    }));
    setEnhancedResults(newEnhancedResults);
  };

  const handleRowSelect = (resumeName) => {
    setSelectedRows(prev => 
      prev.includes(resumeName) 
        ? prev.filter(name => name !== resumeName)
        : [...prev, resumeName]
    );
  };

  const handleExpandRow = (resumeName) => {
    setExpandedRows(prev => ({
      ...prev,
      [resumeName]: !prev[resumeName]
    }));
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
            onSelectRFP={handleRFPSelect}
            multiSelect={false}
          />
          <button
            onClick={handleRunMatching}
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300"
          >
            Run Matching
          </button>
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Refine Search
            </h2>
            <textarea
              className="w-full h-24 bg-gray-700 bg-opacity-50 rounded-lg p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Let me know if I need to refine my search"
              value={refineSearch}
              onChange={(e) => setRefineSearch(e.target.value)}
            ></textarea>
          </div>
        </div>

        <div className="flex-1 px-4 flex flex-col">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-grow overflow-auto">
            <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Results
            </h2>
            {isLoading ? (
              <p className="text-gray-400 text-lg">Searching...</p>
            ) : matchingResults.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Select</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Experience Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Job Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Relevant Projects</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Details</th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-700 bg-opacity-40 divide-y divide-gray-600">
                    {matchingResults.map((result) => (
                      <React.Fragment key={result.name}>
                        <tr className="hover:bg-gray-600 transition-colors duration-200">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <input
                              type="checkbox"
                              checked={selectedRows.includes(result.name)}
                              onChange={() => handleRowSelect(result.name)}
                              className="form-checkbox h-5 w-5 text-blue-600 transition duration-150 ease-in-out"
                            />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <a
                              href={result.resumeLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-400 hover:text-blue-300 transition duration-300 flex items-center"
                            >
                              {result.name}
                              <ExternalLink className="ml-2 h-4 w-4" />
                            </a>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-500 bg-opacity-20 text-blue-300">
                              {result.experienceLevel}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-gray-300">{result.jobTitle}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-gray-300">{result.location}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-gray-300">{result.relevantProjects}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => handleExpandRow(result.name)}
                              className="text-gray-400 hover:text-gray-200 transition-colors duration-200"
                            >
                              {expandedRows[result.name] ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                            </button>
                          </td>
                        </tr>
                        {expandedRows[result.name] && (
                          <tr>
                            <td colSpan="7" className="px-6 py-4 whitespace-normal text-gray-400">
                              <p>{result.explanation}</p>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-400 text-lg">Run matching to see results</p>
            )}
          </div>
          
          {matchingResults.length > 0 && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleEnhanceResumes}
                disabled={selectedRows.length === 0}
                className={`bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 flex items-center ${
                  selectedRows.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <Zap className="mr-2" size={20} />
                Enhance Selected Resumes
              </button>
            </div>
          )}

          {enhancedResults.length > 0 && (
            <div className="mt-6 bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg">
              <h3 className="text-xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
                Enhanced Resumes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {enhancedResults.map((result) => (
                  <div key={result.name} className="bg-gray-700 bg-opacity-40 rounded-lg p-4 hover:bg-opacity-60 transition-all duration-300">
                    <a
                      href={result.enhancedResumeLink}
                      className="text-blue-400 hover:text-blue-300 transition duration-300 flex items-center"
                      onClick={(e) => e.preventDefault()} // Prevent default action for now
                    >
                      {result.name}
                      <ExternalLink className="ml-2 h-4 w-4" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmployeeMatchingPage;