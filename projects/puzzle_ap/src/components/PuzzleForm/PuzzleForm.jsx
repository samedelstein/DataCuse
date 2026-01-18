import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Stack,
  Box,
  CircularProgress,
  useMediaQuery,
  useTheme,
  IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { v4 as uuidv4 } from 'uuid';
import PhotoCapture from './PhotoCapture';
import { processAndStoreImage, blobToDataURL } from '../../services/imageService';
import { getImage } from '../../services/db';

const PuzzleForm = ({ open, onClose, onSave, editPuzzle = null }) => {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const [formData, setFormData] = useState({
    name: '',
    dateCompleted: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [imageFile, setImageFile] = useState(null);
  const [existingImagePreview, setExistingImagePreview] = useState(null);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (editPuzzle) {
      setFormData({
        name: editPuzzle.name,
        dateCompleted: editPuzzle.dateCompleted.split('T')[0],
        notes: editPuzzle.notes || ''
      });

      // Load existing image
      if (editPuzzle.imageId) {
        loadExistingImage(editPuzzle.imageId);
      }
    } else {
      resetForm();
    }
  }, [editPuzzle, open]);

  const loadExistingImage = async (imageId) => {
    try {
      const image = await getImage(imageId);
      if (image && image.blob) {
        const url = await blobToDataURL(image.blob);
        setExistingImagePreview(url);
      }
    } catch (error) {
      console.error('Error loading image:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      dateCompleted: new Date().toISOString().split('T')[0],
      notes: ''
    });
    setImageFile(null);
    setExistingImagePreview(null);
    setErrors({});
  };

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value
    });
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: null
      });
    }
  };

  const handleImageCapture = (file) => {
    setImageFile(file);
    if (errors.image) {
      setErrors({
        ...errors,
        image: null
      });
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Puzzle name is required';
    }

    if (!formData.dateCompleted) {
      newErrors.dateCompleted = 'Completion date is required';
    }

    if (!editPuzzle && !imageFile) {
      newErrors.image = 'Please add a photo of your puzzle';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setSaving(true);
    try {
      let imageId = editPuzzle?.imageId;

      // Process new image if provided
      if (imageFile) {
        imageId = await processAndStoreImage(imageFile);
      }

      const puzzleData = {
        id: editPuzzle?.id || uuidv4(),
        name: formData.name.trim(),
        dateCompleted: new Date(formData.dateCompleted).toISOString(),
        notes: formData.notes.trim(),
        imageId,
        createdAt: editPuzzle?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await onSave(puzzleData);
      handleClose();
    } catch (error) {
      console.error('Error saving puzzle:', error);
      setErrors({ submit: 'Failed to save puzzle. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (!saving) {
      resetForm();
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      fullScreen={fullScreen}
    >
      <DialogTitle>
        {editPuzzle ? 'Edit Puzzle' : 'Add New Puzzle'}
        <IconButton
          onClick={handleClose}
          disabled={saving}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <PhotoCapture
            onImageCapture={handleImageCapture}
            initialImage={existingImagePreview}
          />
          {errors.image && (
            <Box sx={{ color: 'error.main', fontSize: '0.875rem' }}>
              {errors.image}
            </Box>
          )}

          <TextField
            label="Puzzle Name"
            value={formData.name}
            onChange={handleChange('name')}
            error={!!errors.name}
            helperText={errors.name}
            required
            autoFocus={!fullScreen}
          />

          <TextField
            label="Completion Date"
            type="date"
            value={formData.dateCompleted}
            onChange={handleChange('dateCompleted')}
            error={!!errors.dateCompleted}
            helperText={errors.dateCompleted}
            InputLabelProps={{
              shrink: true,
            }}
            required
          />

          <TextField
            label="Notes"
            value={formData.notes}
            onChange={handleChange('notes')}
            multiline
            rows={4}
            placeholder="Add any notes or feedback about this puzzle..."
          />

          {errors.submit && (
            <Box sx={{ color: 'error.main', fontSize: '0.875rem' }}>
              {errors.submit}
            </Box>
          )}
        </Stack>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={saving}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={saving}
          startIcon={saving && <CircularProgress size={20} />}
        >
          {saving ? 'Saving...' : editPuzzle ? 'Update' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PuzzleForm;
