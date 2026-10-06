module.exports = {
  'frontend/**/*.{js,jsx,ts,tsx}': [
    'npm --prefix frontend run format:staged --',
    'npm --prefix frontend run lint:staged --',
  ],
  'frontend/**/*.{css,json,html}': 'npm --prefix frontend run format:staged --',
  'backend/**/*.py': 'python -m ruff format',
}
