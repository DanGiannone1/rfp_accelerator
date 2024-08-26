import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { useRFPList } from '../components/rfp/RFPListContext';
import ExperienceSkillsetProfile from '../components/rfp/ExperienceSkillsetProfile';
import RFPSelector from '../components/rfp/RFPSelector';

const RFPUploadPage = () => {
  const [isUploading, setIsUploading] = useState(false);
  const { setRFPs } = useRFPList();
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [uploadStream, setUploadStream] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setSelectedRFP(file.name);
    setUploadStream(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadStream(response.body);
        setRFPs(prevRFPs => [
          ...prevRFPs,
          { name: file.name, status: 'Complete' }
        ]);
      } else {
        const errorData = await response.json();
        console.error(`Error: ${errorData.error}`);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectRFP = (rfpName) => {
    setSelectedRFP(rfpName);
    setUploadStream(null); // Clear any existing upload stream
  };

  return (
    <div className="flex flex-col h-screen max-w-7xl mx-auto px-4 py-6 overflow-hidden">
      <div className="flex flex-1 gap-4 overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden pr-4">
          <div className="flex-1 overflow-hidden mb-6">
            <ExperienceSkillsetProfile 
              rfp={selectedRFP} 
              uploadStream={uploadStream} 
              isUploading={isUploading}
            />
          </div>
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Upload an RFP
            </h2>
            <div className="border-2 border-dashed border-gray-600 rounded-xl p-6 text-center">
              <Upload className="mx-auto mb-4 text-blue-400" size={36} />
              <p className="mb-4 text-gray-300 text-sm">Drag and drop your RFP file here, or click to select a file</p>
              <input
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                disabled={isUploading}
              />
              <label
                htmlFor="file-upload"
                className={`bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-4 rounded-full cursor-pointer transition duration-300 text-sm ${
                  isUploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isUploading ? 'Uploading...' : 'Upload'}
              </label>
            </div>
          </div>
        </div>
        <div className="w-64 flex-shrink-0">
          <RFPSelector
            selectedRFPs={selectedRFP}
            onSelectRFP={handleSelectRFP}
            multiSelect={false}
          />
        </div>
      </div>
    </div>
  );
};

export default RFPUploadPage;