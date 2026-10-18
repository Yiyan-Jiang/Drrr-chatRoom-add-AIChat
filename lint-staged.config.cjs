/** 为暂存的前端与后端源码配置既有格式化和 ESLint 检查。 */
module.exports = {
  'frontend/**/*.{js,jsx,ts,tsx}': [
    'npm --prefix frontend run format:staged --',
    'npm --prefix frontend run lint:staged --',
  ],
  'frontend/**/*.{css,json,html}': 'npm --prefix frontend run format:staged --',
  'backend/**/*.py': 'python -m ruff format',
}
