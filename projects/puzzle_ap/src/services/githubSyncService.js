const STORAGE_KEY = 'puzzle-sync-settings';

const encodeBase64 = (text) => {
  const bytes = new TextEncoder().encode(text);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
};

const decodeBase64 = (base64) => {
  const binary = atob(base64);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
};

const buildHeaders = (token) => ({
  Accept: 'application/vnd.github+json',
  ...(token ? { Authorization: `Bearer ${token}` } : {})
});

export const loadSyncSettings = () => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return {
      owner: '',
      repo: '',
      path: 'data/puzzles.json',
      branch: 'main',
      token: '',
      autoSync: false
    };
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error('Failed to parse sync settings:', error);
    return {
      owner: '',
      repo: '',
      path: 'data/puzzles.json',
      branch: 'main',
      token: '',
      autoSync: false
    };
  }
};

export const saveSyncSettings = (settings) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
};

const validateSettings = (settings) => {
  if (!settings?.owner || !settings?.repo || !settings?.path) {
    throw new Error('Missing GitHub sync settings.');
  }
};

export const fetchGitHubSnapshot = async (settings) => {
  validateSettings(settings);
  const { owner, repo, path, branch, token } = settings;
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch || 'main'}`;

  const response = await fetch(url, { headers: buildHeaders(token) });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GitHub fetch failed (${response.status})`);
  }

  const data = await response.json();
  if (!data?.content) {
    return null;
  }

  const decoded = decodeBase64(data.content);
  const snapshot = JSON.parse(decoded);

  return {
    snapshot,
    sha: data.sha
  };
};

export const pushGitHubSnapshot = async (settings, snapshot) => {
  validateSettings(settings);
  const { owner, repo, path, branch, token } = settings;
  const existing = await fetchGitHubSnapshot(settings);
  const payload = {
    message: 'Update puzzle snapshot',
    content: encodeBase64(JSON.stringify(snapshot, null, 2)),
    ...(existing?.sha ? { sha: existing.sha } : {}),
    ...(branch ? { branch } : {})
  };

  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/contents/${path}`,
    {
      method: 'PUT',
      headers: buildHeaders(token),
      body: JSON.stringify(payload)
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub push failed (${response.status}): ${errorText}`);
  }

  return response.json();
};
