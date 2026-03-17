import React from 'react';
import { Box, Typography, Button } from '@mui/material';

const DocumentViewer = ({ document }) => {
  if (!document) return null;

  const renderDocumentContent = () => {
    const fileType = document.fileType || document.type || document.contentType || '';

    if (fileType.includes('image')) {
      return (
        <Box sx={{ textAlign: 'center' }}>
          <img
            src={document.url || document.filePath}
            alt={document.name}
            style={{ maxWidth: '100%', maxHeight: '500px' }}
          />
        </Box>
      );
    } else if (fileType.includes('pdf')) {
      return (
        <Box sx={{ height: '500px', width: '100%' }}>
          <iframe
            src={document.url || document.filePath}
            title={document.name}
            width="100%"
            height="100%"
            style={{ border: 'none' }}
          />
        </Box>
      );
    } else {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1">
            Preview not available for this file type.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            href={document.url || document.filePath}
            target="_blank"
            sx={{ mt: 2 }}
          >
            Download Document
          </Button>
        </Box>
      );
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {renderDocumentContent()}

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2">
          Document Information:
        </Typography>
        <Typography variant="body2">
          Type: {document.documentType || 'Not specified'}
        </Typography>
        <Typography variant="body2">
          Uploaded: {document.uploadDate ? new Date(document.uploadDate).toLocaleString() : 'Unknown'}
        </Typography>
      </Box>
    </Box>
  );
};

export default DocumentViewer;
