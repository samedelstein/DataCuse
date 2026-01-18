import { Box, Typography, Paper, Stack } from '@mui/material';
import { formatPuzzleDate, getPuzzleDateSortValue } from '../../services/dateUtils';

const PuzzleTimeline = ({ puzzles }) => {
  const sortedPuzzles = [...puzzles].sort(
    (a, b) => getPuzzleDateSortValue(a.dateCompleted) - getPuzzleDateSortValue(b.dateCompleted)
  );

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, md: 4 },
        borderRadius: 3,
        border: '1px solid rgba(47, 60, 126, 0.12)',
        bgcolor: 'rgba(255, 255, 255, 0.9)'
      }}
    >
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
        Completion timeline
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Follow every puzzle finish in order, from your first build to the latest.
      </Typography>

      <Stack spacing={3}>
        {sortedPuzzles.map((puzzle, index) => (
          <Box key={puzzle.id} sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
              <Box
                sx={{
                  width: 14,
                  height: 14,
                  bgcolor: 'primary.main',
                  borderRadius: '50%',
                  mt: 0.5,
                  zIndex: 1
                }}
              />
              {index !== sortedPuzzles.length - 1 && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 18,
                    width: 2,
                    height: 'calc(100% - 12px)',
                    bgcolor: 'divider'
                  }}
                />
              )}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                {formatPuzzleDate(puzzle.dateCompleted, 'MMMM d, yyyy')}
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {puzzle.name}
              </Typography>
              {puzzle.notes && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {puzzle.notes}
                </Typography>
              )}
            </Box>
          </Box>
        ))}
      </Stack>
    </Paper>
  );
};

export default PuzzleTimeline;
