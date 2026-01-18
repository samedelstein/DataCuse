import { useState, useEffect, useCallback } from 'react';
import {
  getAllPuzzles,
  addPuzzle,
  updatePuzzle,
  deletePuzzle,
  getPuzzle,
  searchPuzzles,
  getStorageEstimate
} from '../services/db';

export const useIndexedDB = () => {
  const [puzzles, setPuzzles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [storageInfo, setStorageInfo] = useState(null);

  // Load all puzzles
  const loadPuzzles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const allPuzzles = await getAllPuzzles();
      setPuzzles(allPuzzles);
    } catch (err) {
      console.error('Error loading puzzles:', err);
      setError('Failed to load puzzles');
    } finally {
      setLoading(false);
    }
  }, []);

  // Add a new puzzle
  const createPuzzle = useCallback(async (puzzleData) => {
    try {
      setError(null);
      await addPuzzle(puzzleData);
      await loadPuzzles();
      await updateStorageInfo();
      return true;
    } catch (err) {
      console.error('Error creating puzzle:', err);
      setError('Failed to create puzzle');
      return false;
    }
  }, [loadPuzzles]);

  // Update an existing puzzle
  const modifyPuzzle = useCallback(async (puzzleData) => {
    try {
      setError(null);
      await updatePuzzle(puzzleData);
      await loadPuzzles();
      return true;
    } catch (err) {
      console.error('Error updating puzzle:', err);
      setError('Failed to update puzzle');
      return false;
    }
  }, [loadPuzzles]);

  // Delete a puzzle
  const removePuzzle = useCallback(async (id) => {
    try {
      setError(null);
      await deletePuzzle(id);
      await loadPuzzles();
      await updateStorageInfo();
      return true;
    } catch (err) {
      console.error('Error deleting puzzle:', err);
      setError('Failed to delete puzzle');
      return false;
    }
  }, [loadPuzzles]);

  // Get a single puzzle
  const fetchPuzzle = useCallback(async (id) => {
    try {
      setError(null);
      return await getPuzzle(id);
    } catch (err) {
      console.error('Error fetching puzzle:', err);
      setError('Failed to fetch puzzle');
      return null;
    }
  }, []);

  // Search puzzles
  const search = useCallback(async (searchTerm) => {
    try {
      setError(null);
      if (!searchTerm || searchTerm.trim() === '') {
        await loadPuzzles();
        return;
      }
      const results = await searchPuzzles(searchTerm);
      setPuzzles(results);
    } catch (err) {
      console.error('Error searching puzzles:', err);
      setError('Failed to search puzzles');
    }
  }, [loadPuzzles]);

  // Update storage information
  const updateStorageInfo = useCallback(async () => {
    try {
      const info = await getStorageEstimate();
      setStorageInfo(info);
    } catch (err) {
      console.error('Error getting storage info:', err);
    }
  }, []);

  // Load puzzles on mount
  useEffect(() => {
    loadPuzzles();
    updateStorageInfo();
  }, [loadPuzzles, updateStorageInfo]);

  return {
    puzzles,
    loading,
    error,
    storageInfo,
    loadPuzzles,
    createPuzzle,
    modifyPuzzle,
    removePuzzle,
    fetchPuzzle,
    search,
    updateStorageInfo
  };
};
