import React from 'react';
import { FileText } from 'lucide-react';

const RFPListItem = ({ rfp }) => (
  <li className="flex items-center p-3 bg-gray-700 bg-opacity-50 rounded-lg transition duration-300 hover:bg-opacity-75">
    <div className="flex items-center space-x-3 flex-grow min-w-0">
      <FileText className="text-blue-400 flex-shrink-0" size={20} />
      <span className="text-gray-200 truncate">{rfp.name}</span>
    </div>
    <span className={`ml-3 px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0 ${
      rfp.status === 'Complete' ? 'bg-green-500 bg-opacity-20 text-green-300' : 
      rfp.status === 'Processing' ? 'bg-yellow-500 bg-opacity-20 text-yellow-300' :
      'bg-red-500 bg-opacity-20 text-red-300'
    }`}>
      {rfp.status === 'Complete' ? 'READY' : rfp.status}
    </span>
  </li>
);

export default RFPListItem;