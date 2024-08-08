import React, { useState } from 'react';
import Layout from './components/layout/Layout';
import MainPage from './pages/MainPage';
import RFPUploadPage from './pages/RFPUploadPage';
import EmployeeMatchingPage from './pages/EmployeeMatchingPage';
import { RFPListProvider } from './components/rfp/RFPListContext';
import RFPAnalyzerPage from './pages/RFPAnalyzerPage';
import RequirementsExtractionPage from './pages/RequirementsExtractionPage';
import ResponseBuilderPage from './pages/ResponseBuilderPage';

const App = () => {
  const [activePage, setActivePage] = useState('Main');

  const pages = ['Main', 'RFP Upload', 'Employee Matching', 'RFP Analyzer', 'Requirements Extraction', 'Response Builder'];

  const renderActivePage = () => {
    switch (activePage) {
      case 'Main':
        return <MainPage setActivePage={setActivePage} />;
      case 'RFP Upload':
        return <RFPUploadPage />;
      case 'Employee Matching':
          return <EmployeeMatchingPage />;
      case 'RFP Analyzer':
          return <RFPAnalyzerPage />;
      case 'Requirements Extraction':
          return <RequirementsExtractionPage/>;
      case 'Response Builder':
        return <ResponseBuilderPage />;
      default:
        return null;
    }
  };

  return (
    <RFPListProvider>
      <Layout pages={pages} activePage={activePage} setActivePage={setActivePage}>
        {renderActivePage()}
      </Layout>
    </RFPListProvider>
  );
};

export default App;