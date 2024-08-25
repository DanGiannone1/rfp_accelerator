import React from 'react';
import NewWindow from 'react-new-window';

const ResumeViewer = ({ pdfData, isWindowOpen, onClose }) => {
  if (!pdfData || !isWindowOpen) {
    return null;
  }

  return (
    <NewWindow onUnload={onClose}>
      <div>
        <iframe src={pdfData} width="100%" height="600px" title="Resume Viewer"></iframe>
      </div>
    </NewWindow>
  );
};

export default ResumeViewer;