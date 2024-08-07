import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children, pages, activePage, setActivePage }) => {
  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Sidebar pages={pages} activePage={activePage} setActivePage={setActivePage} />
      <div className="flex-1 p-10">
        {children}
      </div>
    </div>
  );
};

export default Layout;