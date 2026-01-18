import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Stack,
  Divider,
  CircularProgress
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ShareIcon from '@mui/icons-material/Share';
import { format } from 'date-fns';
import { getImage } from '../../services/db';
import { blobToDataURL } from '../../services/imageService';
import ShareButton from './ShareButton';

const PuzzleDetail = ({ puzzle, open, onClose, onEdit, onDelete }) => {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showShareButton, setShowShareButton] = useState(false);

  useEffect(() => {
    const loadImage = async () => {
      if (puzzle?.imageId) {
        try {
          setLoading(true);
          const image = await getImage(puzzle.imageId);
          if (image && image.blob) {
            const url = await blobToDataURL(image.blob);
            setImageUrl(url);
          }
        } catch (error) {
          console.error('Error loading image:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    if (open && puzzle) {
      loadImage();
    }
  }, [puzzle, open]);

  if (!puzzle) return null;

  const formattedDate = format(new Date(puzzle.dateCompleted), 'MMMM d, yyyy');

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          maxHeight: '90vh'
        }
      }}
    >
      <IconButton
        onClick={onClose}
        sx={{
          position: 'absolute',
          right: 8,
          top: 8,
          bgcolor: 'background.paper',
          zIndex: 1,
          '&:hover': {
            bgcolor: 'background.paper'
          }
        }}
      >
        <CloseIcon />
      </IconButton>

      <DialogContent sx={{ p: 0 }}>
        {loading ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="400px"
          >
            <CircularProgress />
          </Box>
        ) : (
          <>
            {imageUrl && (
              <Box
                component="img"
                src={imageUrl}
                alt={puzzle.name}
                sx={{
                  width: '100%',
                  height: 'auto',
                  maxHeight: '60vh',
                  objectFit: 'contain',
                  bgcolor: 'grey.100'
                }}
              />
            )}

            <Box sx={{ p: 3 }}>
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                {puzzle.name}
              </Typography>

              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Completed on {formattedDate}
              </Typography>

              {puzzle.notes && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body1" paragraph>
                    {puzzle.notes}
                  </Typography>
                </>
              )}
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2, justifyContent: 'space-between' }}>
        <Button
          startIcon={<DeleteIcon />}
          color="error"
          onClick={() => onDelete(puzzle.id)}
        >
          Delete
        </Button>

        <Stack direction="row" spacing={1}>
          {showShareButton ? (
            <ShareButton puzzle={puzzle} imageUrl={imageUrl} />
          ) : (
            <Button
              startIcon={<ShareIcon />}
              onClick={() => setShowShareButton(true)}
            >
              Share
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            onClick={() => onEdit(puzzle)}
          >
            Edit
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};

export default PuzzleDetail;
