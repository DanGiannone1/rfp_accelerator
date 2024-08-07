import React, { useState } from 'react';
import Layout from './components/layout/Layout';
import RFPUploadPage from './pages/RFPUploadPage';
import EmployeeMatchingPage from './pages/EmployeeMatchingPage';

const App = () => {
  const [activePage, setActivePage] = useState('RFP Upload');

  const pages = ['Main', 'RFP Upload', 'Employee Matching'];

  const renderActivePage = () => {
    switch (activePage) {
      case 'RFP Upload':
        return <RFPUploadPage />;
      case 'Main':
        return <div>Main page content goes here</div>;
      case 'Employee Matching':
        return <EmployeeMatchingPage />;
      default:
        return null;
    }
  };

  return (
    <Layout pages={pages} activePage={activePage} setActivePage={setActivePage}>
      {renderActivePage()}
    </Layout>
  );
};

export default App;