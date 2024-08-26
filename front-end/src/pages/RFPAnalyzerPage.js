import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Loader } from 'lucide-react';
import { useRFPList } from '../components/rfp/RFPListContext';
import ReactMarkdown from 'react-markdown';
import RFPSelector from '../components/rfp/RFPSelector';

const RFPAnalyzerPage = () => {
  const [selectedRFP, setSelectedRFP] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const { rfps } = useRFPList();
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleRFPSelect = (rfpName) => {
    setSelectedRFP(rfpName);
    setChatMessages([]);
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || !selectedRFP) return;

    const userMessage = { role: 'user', content: inputMessage };
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsStreaming(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          rfp_name: selectedRFP
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiMessageContent = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        aiMessageContent += chunk;
        setChatMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === 'assistant') {
            lastMessage.content = aiMessageContent;
          } else {
            newMessages.push({ role: 'assistant', content: aiMessageContent });
          }
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Error:', error);
      setChatMessages(prev => [...prev, { role: 'system', content: 'An error occurred while processing your request.' }]);
    } finally {
      setIsStreaming(false);
    }
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
      <div className="flex flex-1 px-4 pb-16 overflow-hidden">
        <div className="w-64 pr-4 flex flex-col">
        <RFPSelector
            selectedRFPs={selectedRFP}
            onSelectRFP={handleRFPSelect}
            multiSelect={false}
        />
        </div>

        <div className="flex-1 flex flex-col bg-gradient-to-b from-gray-800 to-gray-900 rounded-xl shadow-lg overflow-hidden border border-gray-700">
          <h2 className="text-2xl font-semibold p-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            AI Analysis Chat
          </h2>
          <div className="flex-1 overflow-y-auto px-6" ref={chatContainerRef}>
            {chatMessages.map((msg, index) => (
              <div key={index} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                <span className={`inline-block p-3 rounded-lg shadow-md ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : msg.role === 'system' 
                    ? 'bg-gray-600 text-white' 
                    : 'bg-gray-700 bg-opacity-70 text-white'
                } max-w-[75%]`}>
                  {msg.role === 'user' ? (
                    msg.content
                  ) : (
                    <ReactMarkdown className="prose prose-invert max-w-none">
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </span>
              </div>
            ))}
          </div>
          <div className="p-6 bg-gray-800 bg-opacity-70">
            <div className="flex bg-gray-700 bg-opacity-50 rounded-lg overflow-hidden shadow-inner">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message here..."
                className="flex-1 bg-transparent p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                disabled={isStreaming || !selectedRFP}
              />
              <button
                onClick={handleSendMessage}
                className={`px-4 bg-blue-600 hover:bg-blue-700 transition-colors duration-300 ${
                  (isStreaming || !selectedRFP) ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                disabled={isStreaming || !selectedRFP}
              >
                {isStreaming ? <Loader className="animate-spin" /> : <Send />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RFPAnalyzerPage;