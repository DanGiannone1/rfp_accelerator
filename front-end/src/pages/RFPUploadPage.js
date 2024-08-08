import React, { useState, useEffect, useCallback } from 'react';
import { Upload } from 'lucide-react';
import RFPListItem from '../components/rfp/RFPListItem';
import { useRFPList } from '../components/rfp/RFPListContext';

const RFPUploadPage = () => {
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const { rfps, setRFPs, isLoading } = useRFPList();

  const pollInProgressRFPs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/in-progress-rfps');
      const data = await response.json();
      setRFPs(prevRFPs => {
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
  }, [setRFPs]);

  useEffect(() => {
    let intervalId;
    if (isPolling) {
      intervalId = setInterval(async () => {
        const shouldContinuePolling = await pollInProgressRFPs();
        if (!shouldContinuePolling) {
          setIsPolling(false);
          setUploadStatus('');
        }
      }, 5000);
    }
    return () => clearInterval(intervalId);
  }, [isPolling, pollInProgressRFPs]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('RFP Ingestion process started. This can take anywhere from 2 to 15 minutes.');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStatus(`${data.message}`);
        setIsPolling(true);
        
        setRFPs(prevRFPs => [
          ...prevRFPs,
          { name: file.name, status: 'Processing' }
        ]);
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
    <div className="max-w-md mx-auto">
      <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Upload an RFP</h1>
      <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center mb-8 bg-gray-800 bg-opacity-50 shadow-lg">
        <Upload className="mx-auto mb-4 text-blue-400" size={48} />
        <p className="mb-4 text-gray-300">Drag and drop your RFP file here, or click to select a file</p>
        <input
          type="file"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
          disabled={isUploading}
        />
        <label
          htmlFor="file-upload"
          className={`bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-6 rounded-full cursor-pointer transition duration-300 ${
            isUploading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </label>
        {uploadStatus && (
          <p className={`mt-4 ${
            uploadStatus.includes('Error') ? 'text-red-400' : 
            uploadStatus.includes('RFP Ingestion') ? 'text-yellow-400' :
            'text-green-400'
          }`}>
            {uploadStatus}
          </p>
        )}
      </div>
      <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg">
        <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Available RFPs</h2>
        {isLoading ? (
          <p className="text-gray-300">Loading RFPs...</p>
        ) : (
          <ul className="space-y-2">
            {rfps.map((rfp, index) => (
              <RFPListItem key={index} rfp={rfp} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default RFPUploadPage;