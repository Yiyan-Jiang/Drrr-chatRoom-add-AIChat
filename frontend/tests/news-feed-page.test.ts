import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { test } from 'node:test'

const source = readFileSync(
  resolve(process.cwd(), 'src/pages/subPage/NewsFeed.tsx'),
  'utf8',
)

test('NewsFeed renders the static news document list instead of a placeholder', () => {
  assert.match(
    source,
    /from\s+['"]@\/features\/news\/newsDocuments['"]/,
    'NewsFeed should read static Markdown documents from the news data module.',
  )

  assert.match(
    source,
    /getAllNewsDocuments\(\)\.then/,
    'NewsFeed should lazily load the static document list.',
  )

  assert.match(source, /useState\(''\)/, 'NewsFeed should track the search query.')
  assert.match(source, /useState\('all'\)/, 'NewsFeed should track the selected category.')
  assert.match(source, /PAGE_SIZE\s*=\s*10/, 'NewsFeed should show at most ten documents per page.')
  assert.match(source, /useState\(1\)/, 'NewsFeed should track the current page.')
  assert.match(source, /filterNewsDocuments\(/, 'NewsFeed should filter documents locally.')
  assert.match(source, /Math\.ceil\(filteredDocuments\.length \/ PAGE_SIZE\)/)
  assert.match(source, /filteredDocuments\.slice\(/)
  assert.match(source, /paginatedDocuments\.map/)
  assert.match(source, /getNewsCategories\(/, 'NewsFeed should render local categories.')
  assert.match(source, /type="search"/, 'NewsFeed should expose a search input.')
  assert.match(source, /setSelectedCategory\(/, 'NewsFeed should allow category changes.')
  assert.match(source, /setCurrentPage\(1\)/, 'NewsFeed should reset pagination when filters change.')
  assert.match(source, /disabled=\{currentPage === 1\}/)
  assert.match(source, /disabled=\{currentPage === totalPages\}/)

  assert.match(
    source,
    /to=\{`\/news\/\$\{document\.slug\}`\}/,
    'Each news card should link to the standalone detail route.',
  )

  assert.match(
    source,
    /<Link[\s\S]*?className="group block rounded border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900\/80"/,
    'The full news card should be clickable, not only the title.',
  )

  assert.doesNotMatch(
    source,
    /h-96/,
    'NewsFeed should no longer be the centered placeholder screen.',
  )
})
