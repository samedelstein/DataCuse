import {
  Grid,
  Container,
  Box,
  Typography,
  CircularProgress,
  TextField,
  InputAdornment,
  Alert,
  Paper
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExtensionIcon from '@mui/icons-material/Extension';
import PuzzleCard from './PuzzleCard';
import PuzzleTimeline from './PuzzleTimeline';

const PuzzleList = ({ puzzles, loading, error, onPuzzleClick, onSearch }) => {
  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          justifyContent: 'space-between',
          gap: 3,
          mb: 4
        }}
      >
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Your puzzle gallery
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Keep every finished puzzle with a photo, date, and story.
          </Typography>
        </Box>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            alignSelf: { md: 'center' },
            bgcolor: 'rgba(255,255,255,0.8)',
            border: '1px solid rgba(47, 60, 126, 0.12)',
            minWidth: { xs: '100%', md: 320 }
          }}
        >
          <TextField
            placeholder="Search puzzles..."
            onChange={(e) => onSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ bgcolor: 'common.white' }}
          />
        </Paper>
      </Box>

      {puzzles.length === 0 ? (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="50vh"
          textAlign="center"
        >
          <ExtensionIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" gutterBottom color="text.secondary">
            No puzzles yet
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Add your first completed puzzle using the + button below
          </Typography>
        </Box>
      ) : (
        <>
          <Grid container spacing={3}>
            {puzzles.map((puzzle) => (
              <Grid item xs={12} sm={6} md={4} key={puzzle.id}>
                <PuzzleCard puzzle={puzzle} onClick={onPuzzleClick} />
              </Grid>
            ))}
          </Grid>
          <Box sx={{ mt: 4 }}>
            <PuzzleTimeline puzzles={puzzles} />
          </Box>
        </>
      )}
    </Container>
  );
};

export default PuzzleList;
