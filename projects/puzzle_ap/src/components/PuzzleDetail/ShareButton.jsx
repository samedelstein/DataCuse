import { useState } from 'react';
import {
  Button,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import ShareIcon from '@mui/icons-material/Share';
import DownloadIcon from '@mui/icons-material/Download';
import {
  generateShareGraphic,
  sharePuzzle,
  isSharingSupported
} from '../../services/shareService';

const ShareButton = ({ puzzle, imageUrl }) => {
  const [generating, setGenerating] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleShare = async () => {
    if (!imageUrl) {
      setNotification({
        open: true,
        message: 'Image not loaded yet',
        severity: 'error'
      });
      return;
    }

    setGenerating(true);
    try {
      // Generate the share graphic
      const shareBlob = await generateShareGraphic(puzzle, imageUrl);

      // Share or download
      const shared = await sharePuzzle(puzzle, shareBlob);

      if (shared) {
        setNotification({
          open: true,
          message: 'Shared successfully!',
          severity: 'success'
        });
      } else {
        setNotification({
          open: true,
          message: 'Image downloaded to your device',
          severity: 'info'
        });
      }
    } catch (error) {
      console.error('Error generating share graphic:', error);
      setNotification({
        open: true,
        message: 'Failed to generate share image',
        severity: 'error'
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const isShareAvailable = isSharingSupported();

  return (
    <>
      <Button
        startIcon={generating ? <CircularProgress size={20} /> : (isShareAvailable ? <ShareIcon /> : <DownloadIcon />)}
        onClick={handleShare}
        disabled={generating || !imageUrl}
      >
        {generating ? 'Generating...' : (isShareAvailable ? 'Share' : 'Download')}
      </Button>

      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default ShareButton;
