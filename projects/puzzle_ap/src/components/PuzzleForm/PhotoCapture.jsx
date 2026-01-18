import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  IconButton,
  Paper,
  Typography,
  Stack
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';
import {
  isCameraAvailable,
  requestCameraPermission,
  captureImageFromVideo,
  stopCameraStream,
  validateImageFile,
  blobToDataURL
} from '../../services/imageService';

const PhotoCapture = ({ onImageCapture, initialImage }) => {
  const [cameraActive, setCameraActive] = useState(false);
  const [stream, setStream] = useState(null);
  const [preview, setPreview] = useState(initialImage || null);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  const hasCameraSupport = isCameraAvailable();

  useEffect(() => {
    return () => {
      if (stream) {
        stopCameraStream(stream);
      }
    };
  }, [stream]);

  const startCamera = async () => {
    try {
      setError(null);
      const mediaStream = await requestCameraPermission();
      setStream(mediaStream);
      setCameraActive(true);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stopCameraStream(stream);
      setStream(null);
    }
    setCameraActive(false);
  };

  const capturePhoto = async () => {
    try {
      if (videoRef.current && stream) {
        const blob = await captureImageFromVideo(videoRef.current);
        const dataUrl = await blobToDataURL(blob);
        setPreview(dataUrl);
        onImageCapture(blob);
        stopCamera();
      }
    } catch (err) {
      setError('Failed to capture photo');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      validateImageFile(file);
      const dataUrl = await blobToDataURL(file);
      setPreview(dataUrl);
      onImageCapture(file);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const clearImage = () => {
    setPreview(null);
    onImageCapture(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (cameraActive) {
    return (
      <Paper elevation={0} sx={{ p: 2, bgcolor: 'black', borderRadius: 2 }}>
        <Box sx={{ position: 'relative' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%',
              height: 'auto',
              borderRadius: 8,
              display: 'block'
            }}
          />
          <Stack
            direction="row"
            spacing={2}
            justifyContent="center"
            sx={{ mt: 2 }}
          >
            <Button
              variant="contained"
              color="primary"
              startIcon={<PhotoCameraIcon />}
              onClick={capturePhoto}
              size="large"
            >
              Capture
            </Button>
            <Button
              variant="outlined"
              onClick={stopCamera}
              sx={{ color: 'white', borderColor: 'white' }}
            >
              Cancel
            </Button>
          </Stack>
        </Box>
      </Paper>
    );
  }

  if (preview) {
    return (
      <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
        <Box sx={{ position: 'relative' }}>
          <img
            src={preview}
            alt="Preview"
            style={{
              width: '100%',
              height: 'auto',
              borderRadius: 8,
              display: 'block'
            }}
          />
          <IconButton
            onClick={clearImage}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              bgcolor: 'background.paper',
              '&:hover': { bgcolor: 'background.paper' }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={0}
      sx={{
        p: 4,
        bgcolor: 'grey.100',
        borderRadius: 2,
        border: '2px dashed',
        borderColor: 'grey.300'
      }}
    >
      <Stack spacing={2} alignItems="center">
        <CameraAltIcon sx={{ fontSize: 60, color: 'text.secondary' }} />
        <Typography variant="h6" color="text.secondary">
          Add a photo of your puzzle
        </Typography>

        <Stack direction="row" spacing={2}>
          {hasCameraSupport && (
            <Button
              variant="contained"
              startIcon={<PhotoCameraIcon />}
              onClick={startCamera}
            >
              Take Photo
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={() => fileInputRef.current?.click()}
          >
            Upload Photo
          </Button>
        </Stack>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />

        {error && (
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        )}
      </Stack>
    </Paper>
  );
};

export default PhotoCapture;
