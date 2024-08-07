import React from 'react';
import { FileText, Users, BarChart } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, description, onClick }) => (
  <div 
    className="bg-gray-800 bg-opacity-50 rounded-xl p-6 shadow-lg transition-all duration-300 hover:bg-opacity-70 hover:shadow-xl cursor-pointer"
    onClick={onClick}
  >
    <Icon className="text-blue-400 mb-4" size={48} />
    <h2 className="text-2xl font-semibold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
      {title}
    </h2>
    <p className="text-gray-300">{description}</p>
  </div>
);

const MainPage = ({ setActivePage }) => {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-5xl font-bold mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        Proposal AI
      </h1>
      <p className="text-xl text-center text-gray-300 mb-12">
        Streamline your proposal process with the power of advanced AI agents.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <FeatureCard
          icon={FileText}
          title="RFP Upload"
          description="Upload your RFPs to get started. Performs advanced sectioning and analysis that will form the foundation for the rest of the proposal process."
          onClick={() => setActivePage('RFP Upload')}
        />
        <FeatureCard
          icon={Users}
          title="Employee Matching"
          description="Match your employees' skills and experience with the right RFPs to increase your proposal success rate."
          onClick={() => setActivePage('Employee Matching')}
        />
        <FeatureCard
          icon={BarChart}
          title="Analytics"
          description="Gain insights into your proposal process with detailed analytics and performance metrics."
          onClick={() => setActivePage('Analytics')}
        />
      </div>
    </div>
  );
};

export default MainPage;