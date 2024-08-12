import React from 'react';
import { Download, List } from 'lucide-react';

const DownloadsBar = ({ downloads }) => (
    <div className="w-64 pl-4">
    <div className="bg-gray-800 bg-opacity-50 rounded-xl p-4 shadow-lg">
      <h2 className="text-xl font-semibold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        Downloads
      </h2>
      <div className="space-y-2">
        {downloads.map((download, index) => (
          <div key={index} className="flex items-center justify-between p-2 bg-gray-700 bg-opacity-50 rounded-lg">
            <div className="flex items-center mr-2 overflow-hidden">
              <List className="text-blue-400 mr-2 flex-shrink-0" size={16} />
              <span className="text-sm text-gray-300 truncate">{download.name}</span>
            </div>
            <div className="flex items-center flex-shrink-0">
              <span className="text-xs font-semibold bg-green-500 bg-opacity-20 text-green-300 px-2 py-1 rounded-full mr-2">
                {download.status}
              </span>
              <Download className="text-blue-400 cursor-pointer" size={16} />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

export default DownloadsBar;

