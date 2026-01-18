import { useState, useEffect } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Fab,
  Box,
  Container,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
  Stack,
  FormControlLabel,
  Switch
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ExtensionIcon from '@mui/icons-material/Extension';
import theme from './theme';
import PuzzleList from './components/PuzzleList/PuzzleList';
import PuzzleForm from './components/PuzzleForm/PuzzleForm';
import PuzzleDetail from './components/PuzzleDetail/PuzzleDetail';
import { useIndexedDB } from './hooks/useIndexedDB';
import { exportData, importData } from './services/db';
import {
  loadSyncSettings,
  saveSyncSettings,
  fetchGitHubSnapshot,
  pushGitHubSnapshot
} from './services/githubSyncService';

function App() {
  const {
    puzzles,
    loading,
    error,
    storageInfo,
    createPuzzle,
    modifyPuzzle,
    removePuzzle,
    loadPuzzles,
    search,
    updateStorageInfo
  } = useIndexedDB();

  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedPuzzle, setSelectedPuzzle] = useState(null);
  const [editPuzzle, setEditPuzzle] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [puzzleToDelete, setPuzzleToDelete] = useState(null);
  const [syncDialogOpen, setSyncDialogOpen] = useState(false);
  const [syncSettings, setSyncSettings] = useState(loadSyncSettings());
  const [syncing, setSyncing] = useState(false);
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const isSyncConfigured = Boolean(
    syncSettings?.owner && syncSettings?.repo && syncSettings?.path
  );

  // Check storage usage on mount and show warning if high
  useEffect(() => {
    if (storageInfo && parseFloat(storageInfo.percentUsed) > 80) {
      setNotification({
        open: true,
        message: `Storage is ${storageInfo.percentUsed}% full. Consider syncing your data.`,
        severity: 'warning'
      });
    }
  }, [storageInfo]);

  useEffect(() => {
    const hydrateFromRepo = async () => {
      if (!syncSettings?.autoSync || !isSyncConfigured) return;
      setSyncing(true);
      try {
        const result = await fetchGitHubSnapshot(syncSettings);
        if (result?.snapshot) {
          await importData(result.snapshot);
          await loadPuzzles();
          setNotification({
            open: true,
            message: 'Pulled puzzles from your repo.',
            severity: 'success'
          });
        }
      } catch (error) {
        console.error('Sync pull failed:', error);
        setNotification({
          open: true,
          message: 'Failed to pull puzzles from repo.',
          severity: 'error'
        });
      } finally {
        setSyncing(false);
      }
    };

    hydrateFromRepo();
  }, [loadPuzzles, syncSettings]);

  const handleOpenForm = () => {
    setEditPuzzle(null);
    setFormOpen(true);
  };

  const handleCloseForm = () => {
    setFormOpen(false);
    setEditPuzzle(null);
  };

  const handleSavePuzzle = async (puzzleData) => {
    const success = editPuzzle
      ? await modifyPuzzle(puzzleData)
      : await createPuzzle(puzzleData);

    if (success) {
      setNotification({
        open: true,
        message: editPuzzle ? 'Puzzle updated!' : 'Puzzle added!',
        severity: 'success'
      });
      setDetailOpen(false);
      updateStorageInfo();
      if (syncSettings?.autoSync && isSyncConfigured) {
        handlePushToRepo();
      }
    } else {
      setNotification({
        open: true,
        message: 'Failed to save puzzle',
        severity: 'error'
      });
    }
  };

  const handlePuzzleClick = (puzzle) => {
    setSelectedPuzzle(puzzle);
    setDetailOpen(true);
  };

  const handleEditPuzzle = (puzzle) => {
    setEditPuzzle(puzzle);
    setDetailOpen(false);
    setFormOpen(true);
  };

  const handleDeleteClick = (puzzleId) => {
    setPuzzleToDelete(puzzleId);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (puzzleToDelete) {
      const success = await removePuzzle(puzzleToDelete);
      if (success) {
        setNotification({
          open: true,
          message: 'Puzzle deleted',
          severity: 'info'
        });
        setDetailOpen(false);
      } else {
        setNotification({
          open: true,
          message: 'Failed to delete puzzle',
          severity: 'error'
        });
      }
    }
    setDeleteConfirmOpen(false);
    setPuzzleToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmOpen(false);
    setPuzzleToDelete(null);
  };

  const handleSearch = (searchTerm) => {
    search(searchTerm);
  };

  const handleSyncDialogOpen = () => setSyncDialogOpen(true);

  const handleSyncDialogClose = () => setSyncDialogOpen(false);

  const handleSyncSettingsChange = (field) => (event) => {
    const value = field === 'autoSync' ? event.target.checked : event.target.value;
    setSyncSettings((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveSyncSettings = () => {
    saveSyncSettings(syncSettings);
    setSyncDialogOpen(false);
    setNotification({
      open: true,
      message: 'Sync settings saved.',
      severity: 'success'
    });
  };

  const handlePullFromRepo = async () => {
    if (!isSyncConfigured) {
      setNotification({
        open: true,
        message: 'Add your repo settings before syncing.',
        severity: 'warning'
      });
      return;
    }
    setSyncing(true);
    try {
      const result = await fetchGitHubSnapshot(syncSettings);
      if (result?.snapshot) {
        await importData(result.snapshot);
        await loadPuzzles();
        setNotification({
          open: true,
          message: 'Pulled puzzles from your repo.',
          severity: 'success'
        });
      } else {
        setNotification({
          open: true,
          message: 'No snapshot found in the repo yet.',
          severity: 'info'
        });
      }
    } catch (error) {
      console.error('Sync pull failed:', error);
      setNotification({
        open: true,
        message: 'Failed to pull puzzles from repo.',
        severity: 'error'
      });
    } finally {
      setSyncing(false);
    }
  };

  const handlePushToRepo = async () => {
    if (!isSyncConfigured) {
      setNotification({
        open: true,
        message: 'Add your repo settings before syncing.',
        severity: 'warning'
      });
      return;
    }
    setSyncing(true);
    try {
      const snapshot = await exportData();
      await pushGitHubSnapshot(syncSettings, snapshot);
      setNotification({
        open: true,
        message: 'Pushed puzzles to your repo.',
        severity: 'success'
      });
    } catch (error) {
      console.error('Sync push failed:', error);
      setNotification({
        open: true,
        message: 'Failed to push puzzles to repo.',
        severity: 'error'
      });
    } finally {
      setSyncing(false);
    }
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Container
              maxWidth="lg"
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                py: 1.5
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 44,
                  height: 44,
                  borderRadius: '14px',
                  bgcolor: 'rgba(255, 255, 255, 0.18)'
                }}
              >
                <ExtensionIcon sx={{ fontSize: 26, color: 'common.white' }} />
              </Box>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="div" sx={{ fontWeight: 700 }}>
                  Sunday Night Puzzles
                </Typography>
                <Typography variant="subtitle2" sx={{ opacity: 0.85 }}>
                  Capture cozy puzzle nights and track your finished builds.
                </Typography>
              </Box>
            </Container>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            bgcolor: 'background.default',
            backgroundImage:
              'radial-gradient(circle at top, rgba(47, 60, 126, 0.08), transparent 45%)'
          }}
        >
          <PuzzleList
            puzzles={puzzles}
            loading={loading}
            error={error}
            onPuzzleClick={handlePuzzleClick}
            onSearch={handleSearch}
            onSyncSettings={handleSyncDialogOpen}
            onPullFromRepo={handlePullFromRepo}
            onPushToRepo={handlePushToRepo}
            syncing={syncing}
          />
        </Box>

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add"
          onClick={handleOpenForm}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
          }}
        >
          <AddIcon />
        </Fab>

        {/* Puzzle Form Dialog */}
        <PuzzleForm
          open={formOpen}
          onClose={handleCloseForm}
          onSave={handleSavePuzzle}
          editPuzzle={editPuzzle}
        />

        {/* Puzzle Detail Dialog */}
        <PuzzleDetail
          puzzle={selectedPuzzle}
          open={detailOpen}
          onClose={() => setDetailOpen(false)}
          onEdit={handleEditPuzzle}
          onDelete={handleDeleteClick}
        />

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteConfirmOpen}
          onClose={handleDeleteCancel}
        >
          <DialogTitle>Delete Puzzle?</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete this puzzle? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel}>Cancel</Button>
            <Button onClick={handleDeleteConfirm} color="error" autoFocus>
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog open={syncDialogOpen} onClose={handleSyncDialogClose} maxWidth="sm" fullWidth>
          <DialogTitle>Sync across browsers</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="GitHub Owner"
                value={syncSettings?.owner || ''}
                onChange={handleSyncSettingsChange('owner')}
                placeholder="your-org-or-username"
              />
              <TextField
                label="Repository"
                value={syncSettings?.repo || ''}
                onChange={handleSyncSettingsChange('repo')}
                placeholder="puzzle-data-repo"
              />
              <TextField
                label="File path"
                value={syncSettings?.path || ''}
                onChange={handleSyncSettingsChange('path')}
                placeholder="data/puzzles.json"
                helperText="This file will be created/updated in your repo."
              />
              <TextField
                label="Branch"
                value={syncSettings?.branch || 'main'}
                onChange={handleSyncSettingsChange('branch')}
                placeholder="main"
              />
              <TextField
                label="GitHub token"
                type="password"
                value={syncSettings?.token || ''}
                onChange={handleSyncSettingsChange('token')}
                placeholder="ghp_..."
                helperText="Stored locally in this browser to push updates."
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={!!syncSettings?.autoSync}
                    onChange={handleSyncSettingsChange('autoSync')}
                  />
                }
                label="Auto-sync on save"
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleSyncDialogClose}>Cancel</Button>
            <Button onClick={handleSaveSyncSettings} variant="contained">
              Save settings
            </Button>
          </DialogActions>
        </Dialog>

        {/* Notification Snackbar */}
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
      </Box>
    </ThemeProvider>
  );
}

export default App;
