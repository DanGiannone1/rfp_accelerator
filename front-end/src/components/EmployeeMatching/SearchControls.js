import React from 'react';

const SearchControls = ({ onRunMatching, refineSearch, setRefineSearch }) => {
  return (
    <>
      <button
        onClick={onRunMatching}
        className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300"
      >
        Run Matching
      </button>
      <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
        <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          Refine Search
        </h2>
        <textarea
          className="w-full h-24 bg-gray-700 bg-opacity-50 rounded-lg p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Let me know if I need to refine my search"
          value={refineSearch}
          onChange={(e) => setRefineSearch(e.target.value)}
        ></textarea>
      </div>
    </>
  );
};

export default SearchControls;