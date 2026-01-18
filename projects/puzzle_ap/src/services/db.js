import { openDB } from 'idb';
import { getPuzzleDateSortValue } from './dateUtils';

const DB_NAME = 'puzzle-tracker-db';
const DB_VERSION = 1;

// Initialize and open the database
export const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db, oldVersion, newVersion, transaction) {
      // Create puzzles store
      if (!db.objectStoreNames.contains('puzzles')) {
        const puzzleStore = db.createObjectStore('puzzles', {
          keyPath: 'id'
        });
        puzzleStore.createIndex('dateCompleted', 'dateCompleted');
        puzzleStore.createIndex('name', 'name');
        puzzleStore.createIndex('createdAt', 'createdAt');
      }

      // Create images store
      if (!db.objectStoreNames.contains('images')) {
        const imageStore = db.createObjectStore('images', {
          keyPath: 'id'
        });
        imageStore.createIndex('createdAt', 'createdAt');
      }

      // Create metadata store
      if (!db.objectStoreNames.contains('metadata')) {
        db.createObjectStore('metadata', {
          keyPath: 'key'
        });
      }
    }
  });
};

// Puzzle CRUD operations
export const addPuzzle = async (puzzle) => {
  const db = await initDB();
  const id = await db.add('puzzles', puzzle);
  return id;
};

export const getPuzzle = async (id) => {
  const db = await initDB();
  return db.get('puzzles', id);
};

export const getAllPuzzles = async () => {
  const db = await initDB();
  const puzzles = await db.getAll('puzzles');
  // Sort by date completed (most recent first)
  return puzzles.sort((a, b) =>
    getPuzzleDateSortValue(b.dateCompleted) - getPuzzleDateSortValue(a.dateCompleted)
  );
};

export const updatePuzzle = async (puzzle) => {
  const db = await initDB();
  puzzle.updatedAt = new Date().toISOString();
  return db.put('puzzles', puzzle);
};

export const deletePuzzle = async (id) => {
  const db = await initDB();
  // Get the puzzle to find the imageId
  const puzzle = await db.get('puzzles', id);
  if (puzzle && puzzle.imageId) {
    // Delete the associated image
    await deleteImage(puzzle.imageId);
  }
  return db.delete('puzzles', id);
};

export const searchPuzzles = async (searchTerm) => {
  const db = await initDB();
  const allPuzzles = await db.getAll('puzzles');
  const term = searchTerm.toLowerCase();
  return allPuzzles.filter(puzzle =>
    puzzle.name.toLowerCase().includes(term) ||
    (puzzle.notes && puzzle.notes.toLowerCase().includes(term))
  );
};

// Image CRUD operations
export const addImage = async (image) => {
  const db = await initDB();
  const id = await db.add('images', image);
  return id;
};

export const getImage = async (id) => {
  const db = await initDB();
  return db.get('images', id);
};

export const deleteImage = async (id) => {
  const db = await initDB();
  return db.delete('images', id);
};

// Metadata operations
export const setMetadata = async (key, value) => {
  const db = await initDB();
  return db.put('metadata', {
    key,
    value,
    updatedAt: new Date().toISOString()
  });
};

export const getMetadata = async (key) => {
  const db = await initDB();
  const item = await db.get('metadata', key);
  return item ? item.value : null;
};

// Storage estimation
export const getStorageEstimate = async () => {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    const estimate = await navigator.storage.estimate();
    const usage = estimate.usage || 0;
    const quota = estimate.quota || 0;
    const percentUsed = quota > 0 ? (usage / quota) * 100 : 0;

    return {
      usage,
      quota,
      percentUsed: percentUsed.toFixed(2),
      usageMB: (usage / (1024 * 1024)).toFixed(2),
      quotaMB: (quota / (1024 * 1024)).toFixed(2)
    };
  }
  return null;
};

// Export/Import functionality
export const exportData = async () => {
  const db = await initDB();
  const puzzles = await db.getAll('puzzles');
  const images = await db.getAll('images');

  // Convert blobs to base64 for JSON export
  const imagesWithBase64 = await Promise.all(
    images.map(async (img) => ({
      ...img,
      blob: await blobToBase64(img.blob),
      thumbnail: await blobToBase64(img.thumbnail)
    }))
  );

  return {
    puzzles,
    images: imagesWithBase64,
    exportDate: new Date().toISOString(),
    version: DB_VERSION
  };
};

export const importData = async (data) => {
  const db = await initDB();

  // Clear existing data
  await db.clear('puzzles');
  await db.clear('images');

  // Import images
  for (const img of data.images) {
    await db.add('images', {
      ...img,
      blob: await base64ToBlob(img.blob, img.mimeType),
      thumbnail: await base64ToBlob(img.thumbnail, img.mimeType)
    });
  }

  // Import puzzles
  for (const puzzle of data.puzzles) {
    await db.add('puzzles', puzzle);
  }
};

// Helper functions
const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

const base64ToBlob = async (base64, mimeType) => {
  const response = await fetch(base64);
  return response.blob();
};
