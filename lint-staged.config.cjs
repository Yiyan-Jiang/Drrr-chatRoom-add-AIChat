module.exports = {
  'frontend/src/**/*.{js,jsx,ts,tsx}': (files) => {
    const relativeFiles = files.map((file) => file.replace(/^frontend[\\/]/, ''))

    return `npm --prefix frontend run lint:staged -- ${relativeFiles.join(' ')}`
  },
}
