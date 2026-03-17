import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, Button, Divider, Chip,
  Stepper, Step, StepLabel, Dialog, DialogActions,
  DialogContent, DialogContentText, DialogTitle, TextField,
  List, ListItem, ListItemIcon, ListItemText
} from '@mui/material';
import {
  Person, CalendarToday, LocationOn, Assignment,
  Description, AttachFile, Check, Close, Comment
} from '@mui/icons-material';
import { fetchApplicationById, updateApplicationStatus } from '../../services/adminService';
import DocumentViewer from '../../components/admin/DocumentViewer';

const statusSteps = ['Submitted', 'In Review', 'Pending Documents', 'Approved'];

const ApplicationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [actionType, setActionType] = useState('');
  const [comment, setComment] = useState('');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false);

  useEffect(() => {
    const loadApplication = async () => {
      try {
        const data = await fetchApplicationById(id);
        setApplication(data);
      } catch (error) {
        console.error("Failed to load application:", error);
      } finally {
        setLoading(false);
      }
    };

    loadApplication();
  }, [id]);

  const handleStatusUpdate = async () => {
    try {
      await updateApplicationStatus(id, actionType, comment);
      // Refresh application data
      const updatedApplication = await fetchApplicationById(id);
      setApplication(updatedApplication);
      setDialogOpen(false);
      setComment('');
    } catch (error) {
      console.error("Failed to update application status:", error);
    }
  };

  const openStatusDialog = (type) => {
    setActionType(type);
    setDialogOpen(true);
  };

  const viewDocument = (document) => {
    setSelectedDocument(document);
    setDocumentDialogOpen(true);
  };

  if (loading) {
    return <Box sx={{ p: 3 }}>Loading application details...</Box>;
  }

  if (!application) {
    return <Box sx={{ p: 3 }}>Application not found</Box>;
  }

  const getStepIndex = (status) => {
    switch (status) {
      case 'submitted': return 0;
      case 'in_review': return 1;
      case 'pending_documents': return 1;
      case 'approved': return 3;
      case 'rejected': return -1;
      default: return 0;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Application #{application.id}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            onClick={() => navigate('/admin/applications')}
            sx={{ mr: 1 }}
          >
            Back to List
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate(`/admin/applications/${id}/edit`)}
          >
            Edit Application
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>Application Status</Typography>
          {application.status === 'rejected' ? (
            <Chip
              label="REJECTED"
              color="error"
              icon={<Close />}
              sx={{ fontSize: '1rem', py: 1 }}
            />
          ) : (
            <Stepper activeStep={getStepIndex(application.status)} alternativeLabel>
              {statusSteps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          )}
        </Box>

        <Box sx={{ mt: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Check />}
            onClick={() => openStatusDialog('approve')}
            disabled={application.status === 'approved' || application.status === 'rejected'}
          >
            Approve Application
          </Button>
          <Button
            variant="contained"
            color="error"
            startIcon={<Close />}
            onClick={() => openStatusDialog('reject')}
            disabled={application.status === 'approved' || application.status === 'rejected'}
          >
            Reject Application
          </Button>
          <Button
            variant="contained"
            color="warning"
            startIcon={<Comment />}
            onClick={() => openStatusDialog('request_documents')}
            disabled={application.status === 'approved' || application.status === 'rejected'}
          >
            Request Documents
          </Button>
          <Button
            variant="contained"
            color="info"
            startIcon={<Assignment />}
            onClick={() => openStatusDialog('in_review')}
            disabled={application.status !== 'submitted'}
          >
            Mark In Review
          </Button>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Applicant Information</Typography>
            <List>
              <ListItem>
                <ListItemIcon><Person /></ListItemIcon>
                <ListItemText
                  primary="Full Name"
                  secondary={`${application.firstName} ${application.middleName || ''} ${application.lastName}`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CalendarToday /></ListItemIcon>
                <ListItemText
                  primary="Date of Birth"
                  secondary={new Date(application.dateOfBirth).toLocaleDateString()}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><LocationOn /></ListItemIcon>
                <ListItemText
                  primary="Address"
                  secondary={`${application.address}, ${application.city}, ${application.state} ${application.zipCode}`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><Description /></ListItemIcon>
                <ListItemText
                  primary="Application Date"
                  secondary={new Date(application.submissionDate).toLocaleDateString()}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Documents</Typography>
            {application.documents && application.documents.length > 0 ? (
              <List>
                {application.documents.map(doc => (
                  <ListItem
                    key={doc.id}
                    sx={{ cursor: 'pointer' }}
                    onClick={() => viewDocument(doc)}
                  >
                    <ListItemIcon><AttachFile /></ListItemIcon>
                    <ListItemText
                      primary={doc.name}
                      secondary={`Uploaded on ${new Date(doc.uploadDate).toLocaleDateString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body1">No documents uploaded</Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Activity Log</Typography>
            {application.activityLog && application.activityLog.length > 0 ? (
              <List>
                {application.activityLog.map((log, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={log.action}
                        secondary={`By ${log.user} on ${new Date(log.timestamp).toLocaleString()}`}
                      />
                    </ListItem>
                    {log.comment && (
                      <ListItem sx={{ pl: 4 }}>
                        <ListItemText
                          secondary={`Comment: ${log.comment}`}
                        />
                      </ListItem>
                    )}
                    {index < application.activityLog.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Typography variant="body1">No activity recorded</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Status Change Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>
          {actionType === 'approve' ? 'Approve Application' :
           actionType === 'reject' ? 'Reject Application' :
           actionType === 'request_documents' ? 'Request Additional Documents' :
           'Update Application Status'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {actionType === 'approve' ? 'Are you sure you want to approve this passport application?' :
             actionType === 'reject' ? 'Please provide a reason for rejecting this application:' :
             actionType === 'request_documents' ? 'Please specify which documents are required:' :
             'Update the status of this application:'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Comment"
            fullWidth
            variant="outlined"
            multiline
            rows={4}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            required={actionType === 'reject' || actionType === 'request_documents'}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleStatusUpdate}
            color={actionType === 'approve' ? 'primary' : actionType === 'reject' ? 'error' : 'primary'}
            variant="contained"
            disabled={(actionType === 'reject' || actionType === 'request_documents') && !comment}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Viewer Dialog */}
      <Dialog
        open={documentDialogOpen}
        onClose={() => setDocumentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{selectedDocument?.name}</DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <DocumentViewer document={selectedDocument} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDocumentDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApplicationDetail;
