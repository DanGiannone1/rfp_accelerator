import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Loader } from 'lucide-react';

const ExperienceSkillsetProfile = ({ rfp, uploadStream, isUploading }) => {
  const [profileContent, setProfileContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (uploadStream) {
      handleStreamingContent();
    } else if (rfp && !isUploading) {
      fetchRFPAnalysis(rfp);
    }
  }, [uploadStream, rfp, isUploading]);

  const handleStreamingContent = () => {
    setIsStreaming(true);
    setProfileContent('');

    const reader = uploadStream.getReader();
    const decoder = new TextDecoder();

    const processText = ({ done, value }) => {
      if (done) {
        setIsStreaming(false);
        return;
      }

      const chunk = decoder.decode(value);
      setProfileContent(prevContent => prevContent + chunk);

      reader.read().then(processText);
    };

    reader.read().then(processText);
  };

  const fetchRFPAnalysis = async (rfpName) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/get-rfp-analysis?rfp_name=${encodeURIComponent(rfpName)}`);
      if (response.ok) {
        const data = await response.json();
        setProfileContent(data.skills_and_experience);
      } else {
        console.error('Failed to fetch RFP analysis');
        setProfileContent('Failed to load RFP analysis. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching RFP analysis:', error);
      setProfileContent('An error occurred while loading RFP analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg h-[calc(100vh-250px)] flex flex-col">
      <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        Experience & Skillset Profile
      </h2>
      <div className="overflow-y-auto flex-grow">
        {(isUploading || isLoading) && !isStreaming ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader className="animate-spin text-blue-500 mx-auto mb-4" size={48} />
              <p className="text-gray-300 text-lg">Loading...</p>
            </div>
          </div>
        ) : profileContent ? (
          <div className="text-gray-300 prose prose-invert max-w-none">
            <ReactMarkdown>{profileContent}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-gray-300">
            Select an RFP or upload a new one to see the extracted experience and skillset profile.
          </p>
        )}
      </div>
    </div>
  );
};

export default ExperienceSkillsetProfile;