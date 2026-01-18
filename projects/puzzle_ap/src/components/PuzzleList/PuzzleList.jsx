import {
  Grid,
  Container,
  Box,
  Typography,
  CircularProgress,
  TextField,
  InputAdornment,
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExtensionIcon from '@mui/icons-material/Extension';
import PuzzleCard from './PuzzleCard';

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
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box sx={{ mb: 3 }}>
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
          sx={{ maxWidth: 500 }}
        />
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
        <Grid container spacing={3}>
          {puzzles.map((puzzle) => (
            <Grid item xs={12} sm={6} md={4} key={puzzle.id}>
              <PuzzleCard puzzle={puzzle} onClick={onPuzzleClick} />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default PuzzleList;
