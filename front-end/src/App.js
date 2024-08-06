import React, { useState, useEffect, useCallback } from 'react';
import { Upload } from 'lucide-react';

const App = () => {
  const [activePage, setActivePage] = useState('RFP Upload');
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [availableRFPs, setAvailableRFPs] = useState([]);
  const [isPolling, setIsPolling] = useState(false);

  const pages = ['Main', 'RFP Upload', 'Resume Builder'];

  const fetchRFPs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/available-rfps');
      const data = await response.json();
      setAvailableRFPs(data);
      return data;
    } catch (error) {
      console.error('Error fetching RFPs:', error);
    }
  }, []);

  const pollInProgressRFPs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/in-progress-rfps');
      const data = await response.json();
      setAvailableRFPs(prevRFPs => {
        const updatedRFPs = [...prevRFPs];
        data.forEach(rfp => {
          const index = updatedRFPs.findIndex(item => item.name === rfp.name);
          if (index !== -1) {
            updatedRFPs[index] = rfp;
          } else {
            updatedRFPs.push(rfp);
          }
        });
        return updatedRFPs;
      });
      return data.some(rfp => rfp.status === 'Processing');
    } catch (error) {
      console.error('Error polling in-progress RFPs:', error);
      return false;
    }
  }, []);

  useEffect(() => {
    fetchRFPs();
  }, [fetchRFPs]);

  useEffect(() => {
    let intervalId;
    if (isPolling) {
      intervalId = setInterval(async () => {
        const shouldContinuePolling = await pollInProgressRFPs();
        if (!shouldContinuePolling) {
          setIsPolling(false);
        }
      }, 5000);
    }
    return () => clearInterval(intervalId);
  }, [isPolling, pollInProgressRFPs]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStatus(`Success: ${data.message}`);
        setIsPolling(true);
      } else {
        setUploadStatus(`Error: ${data.error}`);
      }
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 p-5">
        {pages.map((page) => (
          <button
            key={page}
            className={`w-full text-left py-2 px-4 rounded mb-2 ${
              activePage === page ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
            onClick={() => setActivePage(page)}
          >
            {page}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div className="flex-1 p-10">
        {activePage === 'RFP Upload' && (
          <div className="max-w-md mx-auto">
            <h1 className="text-3xl font-bold mb-8">Upload an RFP</h1>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center mb-8">
              <Upload className="mx-auto mb-4" size={48} />
              <p className="mb-4">Drag and drop your RFP file here, or click to select a file</p>
              <input
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                disabled={isUploading}
              />
              <label
                htmlFor="file-upload"
                className={`bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded cursor-pointer ${
                  isUploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isUploading ? 'Uploading...' : 'Upload'}
              </label>
              {uploadStatus && (
                <p className={`mt-4 ${uploadStatus.includes('Error') ? 'text-red-500' : 'text-green-500'}`}>
                  {uploadStatus}
                </p>
              )}
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-xl font-bold mb-4">Available RFPs</h2>
              <ul>
                {availableRFPs.map((rfp, index) => (
                  <li key={index} className="flex justify-between items-center mb-2">
                    <span>{rfp.name}</span>
                    <span className={`px-2 py-1 rounded ${
                      rfp.status === 'Complete' ? 'bg-green-600' : 
                      rfp.status === 'Processing' ? 'bg-yellow-600' :
                      'bg-red-600'
                    }`}>
                      {rfp.status}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        {activePage === 'Main' && <div>Main page content goes here</div>}
        {activePage === 'Resume Builder' && <div>Resume Builder content goes here</div>}
      </div>
    </div>
  );
};

export default App;