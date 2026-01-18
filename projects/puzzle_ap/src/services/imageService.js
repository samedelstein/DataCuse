import imageCompression from 'browser-image-compression';
import { v4 as uuidv4 } from 'uuid';
import { addImage } from './db';

// Compression options
const FULL_IMAGE_OPTIONS = {
  maxSizeMB: 0.5,
  maxWidthOrHeight: 1024,
  useWebWorker: true,
  fileType: 'image/jpeg',
  initialQuality: 0.8
};

const THUMBNAIL_OPTIONS = {
  maxSizeMB: 0.1,
  maxWidthOrHeight: 256,
  useWebWorker: true,
  fileType: 'image/jpeg',
  initialQuality: 0.7
};

/**
 * Process and store an image file
 * @param {File|Blob} file - The image file to process
 * @returns {Promise<string>} - The image ID
 */
export const processAndStoreImage = async (file) => {
  try {
    // Compress the full image
    const compressedFile = await imageCompression(file, FULL_IMAGE_OPTIONS);

    // Create thumbnail
    const thumbnailFile = await imageCompression(file, THUMBNAIL_OPTIONS);

    // Convert to blobs
    const fullBlob = new Blob([compressedFile], { type: 'image/jpeg' });
    const thumbnailBlob = new Blob([thumbnailFile], { type: 'image/jpeg' });

    // Create image record
    const imageId = uuidv4();
    const imageRecord = {
      id: imageId,
      blob: fullBlob,
      thumbnail: thumbnailBlob,
      mimeType: 'image/jpeg',
      size: fullBlob.size,
      createdAt: new Date().toISOString()
    };

    // Store in IndexedDB
    await addImage(imageRecord);

    return imageId;
  } catch (error) {
    console.error('Error processing image:', error);
    throw new Error('Failed to process image');
  }
};

/**
 * Capture image from video stream
 * @param {HTMLVideoElement} videoElement - The video element
 * @returns {Promise<Blob>} - The captured image as a blob
 */
export const captureImageFromVideo = async (videoElement) => {
  return new Promise((resolve, reject) => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;

      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to capture image'));
          }
        },
        'image/jpeg',
        0.9
      );
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Convert blob to data URL for display
 * @param {Blob} blob - The blob to convert
 * @returns {Promise<string>} - Data URL
 */
export const blobToDataURL = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

/**
 * Validate image file
 * @param {File} file - The file to validate
 * @returns {boolean} - Whether the file is valid
 */
export const validateImageFile = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!validTypes.includes(file.type)) {
    throw new Error('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
  }

  if (file.size > maxSize) {
    throw new Error('File too large. Maximum size is 10MB.');
  }

  return true;
};

/**
 * Request camera permissions
 * @returns {Promise<MediaStream>} - The camera stream
 */
export const requestCameraPermission = async () => {
  try {
    const constraints = {
      video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      }
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    return stream;
  } catch (error) {
    console.error('Camera permission denied:', error);
    throw new Error('Camera access denied. Please allow camera access in your browser settings.');
  }
};

/**
 * Check if camera is available
 * @returns {boolean} - Whether camera API is available
 */
export const isCameraAvailable = () => {
  return !!(
    navigator.mediaDevices &&
    navigator.mediaDevices.getUserMedia
  );
};

/**
 * Stop camera stream
 * @param {MediaStream} stream - The stream to stop
 */
export const stopCameraStream = (stream) => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
};
