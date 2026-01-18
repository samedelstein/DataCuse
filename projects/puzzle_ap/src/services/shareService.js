/**
 * Generate a shareable image graphic for a puzzle
 * @param {Object} puzzle - The puzzle data
 * @param {string} imageDataUrl - Data URL of the puzzle image
 * @returns {Promise<Blob>} - The generated share graphic as a blob
 */
export const generateShareGraphic = async (puzzle, imageDataUrl) => {
  return new Promise((resolve, reject) => {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Set canvas size (Instagram-friendly square)
      canvas.width = 1080;
      canvas.height = 1080;

      // Draw gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, '#2f3c7e');
      gradient.addColorStop(1, '#f2c14e');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Load and draw the puzzle image
      const img = new Image();
      img.onload = () => {
        // Calculate dimensions to fit image with padding
        const padding = 100;
        const maxImageSize = canvas.width - (padding * 2);

        let imgWidth = img.width;
        let imgHeight = img.height;

        // Scale image to fit
        const scale = Math.min(
          maxImageSize / imgWidth,
          maxImageSize / imgHeight
        );

        imgWidth *= scale;
        imgHeight *= scale;

        // Center the image
        const x = (canvas.width - imgWidth) / 2;
        const y = (canvas.height - imgHeight) / 2;

        // Draw white background for image
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 20;
        ctx.shadowOffsetY = 10;
        ctx.fillRect(x - 20, y - 20, imgWidth + 40, imgHeight + 40);

        // Reset shadow
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetY = 0;

        // Draw the image
        ctx.drawImage(img, x, y, imgWidth, imgHeight);

        // Draw puzzle name at top
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 48px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Add text shadow for better readability
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.shadowBlur = 10;

        ctx.fillText(puzzle.name, canvas.width / 2, 60);

        // Draw completion date
        const dateStr = new Date(puzzle.dateCompleted).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
        ctx.font = '32px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillText(`Completed: ${dateStr}`, canvas.width / 2, canvas.height - 120);

        // Draw app branding
        ctx.font = '24px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillText('Sunday Night Puzzles', canvas.width / 2, canvas.height - 60);

        // Convert canvas to blob
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to generate share graphic'));
            }
          },
          'image/png',
          0.95
        );
      };

      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };

      img.src = imageDataUrl;
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Share a puzzle using the Web Share API or fallback to download
 * @param {Object} puzzle - The puzzle data
 * @param {Blob} imageBlob - The share graphic blob
 * @returns {Promise<boolean>} - Whether the share was successful
 */
export const sharePuzzle = async (puzzle, imageBlob) => {
  const shareData = {
    title: 'Sunday Night Puzzles',
    text: `Just completed: ${puzzle.name}!`,
  };

  // Check if Web Share API is available and supports files
  if (navigator.share && navigator.canShare) {
    try {
      const file = new File([imageBlob], `${puzzle.name}.png`, {
        type: 'image/png'
      });

      const canShareFile = navigator.canShare({ files: [file] });

      if (canShareFile) {
        await navigator.share({
          ...shareData,
          files: [file]
        });
        return true;
      }
    } catch (error) {
      // User cancelled or share failed
      if (error.name !== 'AbortError') {
        console.error('Share failed:', error);
      }
      // Fall through to download fallback
    }
  }

  // Fallback: Download the image
  downloadImage(imageBlob, `${puzzle.name}.png`);
  return false;
};

/**
 * Download a blob as a file
 * @param {Blob} blob - The blob to download
 * @param {string} filename - The filename
 */
const downloadImage = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

/**
 * Check if sharing is supported
 * @returns {boolean} - Whether Web Share API is available
 */
export const isSharingSupported = () => {
  return !!(navigator.share);
};
