import React from 'react';
import { ExternalLink, ChevronDown, ChevronRight } from 'lucide-react';

const ResultsTable = ({ isLoading, matchingResults, selectedRows, setSelectedRows, expandedRows, setExpandedRows, onResumeClick }) => {
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
    <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-grow overflow-auto mb-4">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Years of Experience</th>
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
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          onResumeClick(result.name);
                        }}
                        className="text-blue-400 hover:text-blue-300 transition duration-300 flex items-center"
                      >
                        {result.name}
                        <ExternalLink className="ml-2 h-4 w-4" />
                      </a>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-3 py-1 inline-flex text-sm leading-5 font-medium rounded-full bg-gradient-to-r from-blue-400 to-purple-500 text-white">
                        {result.experienceLevel} years
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
  );
};

export default ResultsTable;