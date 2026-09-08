const API_BASE = '/api';

export async function analyzeScreenplay({ file, text, baseRegion, projectName }) {
  const formData = new FormData();

  if (file) {
    formData.append('file', file);
  }
  if (text) {
    formData.append('text', text);
  }
  formData.append('base_region', baseRegion || 'Kathmandu Valley');
  formData.append('project_name', projectName || 'Untitled Project');

  const resp = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `Server error: ${resp.status}`);
  }

  return resp.json();
}

export async function healthCheck() {
  const resp = await fetch(`${API_BASE}/health`);
  return resp.json();
}
