import { useState, useEffect } from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  CardActionArea,
  Typography,
  Box,
  Skeleton
} from '@mui/material';
import { format } from 'date-fns';
import { getImage } from '../../services/db';
import { blobToDataURL } from '../../services/imageService';

const PuzzleCard = ({ puzzle, onClick }) => {
  const [thumbnailUrl, setThumbnailUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadThumbnail = async () => {
      try {
        if (puzzle.imageId) {
          const image = await getImage(puzzle.imageId);
          if (image && image.thumbnail) {
            const url = await blobToDataURL(image.thumbnail);
            setThumbnailUrl(url);
          }
        }
      } catch (error) {
        console.error('Error loading thumbnail:', error);
      } finally {
        setLoading(false);
      }
    };

    loadThumbnail();
  }, [puzzle.imageId]);

  const formattedDate = format(new Date(puzzle.dateCompleted), 'MMM d, yyyy');

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardActionArea onClick={() => onClick(puzzle)} sx={{ flexGrow: 1 }}>
        {loading ? (
          <Skeleton variant="rectangular" height={200} />
        ) : (
          <CardMedia
            component="img"
            height="200"
            image={thumbnailUrl || '/placeholder.jpg'}
            alt={puzzle.name}
            sx={{
              objectFit: 'cover',
              backgroundColor: '#f0f0f0'
            }}
          />
        )}
        <CardContent>
          <Typography
            gutterBottom
            variant="h6"
            component="div"
            noWrap
            sx={{ fontWeight: 600 }}
          >
            {puzzle.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formattedDate}
          </Typography>
          {puzzle.notes && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mt: 1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {puzzle.notes}
            </Typography>
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

export default PuzzleCard;
