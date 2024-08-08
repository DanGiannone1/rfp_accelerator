import React, { useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';

const RFPAnalyzerPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  const rfps = [
    { id: 1, name: 'RFP1' },
    { id: 2, name: 'RFP2' },
    { id: 3, name: 'RFP3' },
  ];

  const handleRFPSelect = (rfpId) => {
    setSelectedRFP(rfpId);
    // Here you would typically load the initial analysis for the selected RFP
    setChatMessages([{ role: 'system', content: `Initial analysis for RFP ${rfpId}` }]);
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    setChatMessages([...chatMessages, { role: 'user', content: inputMessage }]);
    setInputMessage('');

    // Here you would typically send the message to your backend AI and get a response
    // For now, we'll just simulate a response
    setTimeout(() => {
      setChatMessages(prev => [...prev, { role: 'assistant', content: `Response to: ${inputMessage}` }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full pt-4">
      <div className="text-center mb-8 pb-2">
        <div className="flex justify-center items-center mb-2">
          <MessageSquare className="text-blue-400 mr-2" size={36} />
          <h1 className="text-4xl font-bold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            RFP Analyzer
          </h1>
        </div>
        <p className="text-lg font-semibold mt-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-400">
          Analyze your RFPs with AI-powered insights
        </p>
      </div>
      <div className="flex flex-1 px-4 pb-16">
        {/* Left sidebar with Select RFP */}
        <div className="w-64 pr-4">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Select RFP
            </h2>
            <div className="space-y-2">
              {rfps.map(rfp => (
                <button
                  key={rfp.id}
                  onClick={() => handleRFPSelect(rfp.id)}
                  className={`w-full text-left py-2 px-4 rounded-lg transition duration-300 ${
                    selectedRFP === rfp.id ? 'bg-blue-600' : 'bg-gray-700 bg-opacity-50 hover:bg-opacity-75'
                  }`}
                >
                  {rfp.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main content area with Chat */}
        <div className="flex-1 px-4 flex flex-col">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg flex-1 flex flex-col">
            <h2 className="text-2xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              AI Analysis Chat
            </h2>
            <div className="flex-1 overflow-y-auto mb-4">
              {chatMessages.map((msg, index) => (
                <div key={index} className={`mb-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <span className={`inline-block p-2 rounded-lg ${
                    msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'
                  }`}>
                    {msg.content}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message here..."
                className="flex-1 bg-gray-700 bg-opacity-50 rounded-l-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSendMessage}
                className="bg-blue-600 hover:bg-blue-700 rounded-r-lg p-2"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RFPAnalyzerPage;