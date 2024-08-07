import React from 'react';

const Sidebar = ({ pages, activePage, setActivePage }) => {
  return (
    <div className="w-64 bg-gray-800 bg-opacity-50 p-5">
      {pages.map((page) => (
        <button
          key={page}
          className={`w-full text-left py-2 px-4 rounded-lg mb-2 transition duration-300 ${
            activePage === page ? 'bg-blue-600' : 'bg-gray-700 bg-opacity-50 hover:bg-opacity-75'
          }`}
          onClick={() => setActivePage(page)}
        >
          {page}
        </button>
      ))}
    </div>
  );
};

export default Sidebar;