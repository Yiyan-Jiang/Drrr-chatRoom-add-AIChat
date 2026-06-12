import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  buildNewsDocument,
  buildNewsDocuments,
  filterNewsDocuments,
  getAdjacentNewsDocuments,
  getNewsCategories,
  getNewsDocumentBySlug,
  parseNewsMarkdown,
  slugifyHeading,
} from '../src/features/news/newsDocumentsCore.js'

const firstArticle = `---
title: First News
date: 2026-06-09
author: admin
category: announcement
tags: release,docs
---

This is the excerpt.

<!-- more -->

## Main Heading

Article body.

### Nested Heading

More body.
`

const secondArticle = `---
title: Second News
date: 2026-06-08
---

Second excerpt.

## Second Heading
`

test('parses frontmatter, excerpt, body, tags, and headings from markdown', () => {
  const parsed = parseNewsMarkdown(firstArticle)

  assert.equal(parsed.frontmatter.title, 'First News')
  assert.equal(parsed.frontmatter.date, '2026-06-09')
  assert.equal(parsed.frontmatter.author, 'admin')
  assert.equal(parsed.frontmatter.category, 'announcement')
  assert.deepEqual(parsed.frontmatter.tags, ['release', 'docs'])
  assert.equal(parsed.excerpt, 'This is the excerpt.')
  assert.match(parsed.body, /## Main Heading/)
  assert.deepEqual(parsed.headings, [
    { id: 'main-heading', level: 2, text: 'Main Heading' },
    { id: 'nested-heading', level: 3, text: 'Nested Heading' },
  ])
})

test('uses the first paragraph as excerpt when the more marker is missing', () => {
  const parsed = parseNewsMarkdown(secondArticle)

  assert.equal(parsed.excerpt, 'Second excerpt.')
})

test('builds documents with file slugs and sensible defaults', () => {
  const document = buildNewsDocument(
    '../content/news/first-news.md',
    firstArticle,
  )

  assert.equal(document.slug, 'first-news')
  assert.equal(document.title, 'First News')
  assert.equal(document.author, 'admin')
  assert.equal(document.category, 'announcement')
  assert.deepEqual(document.tags, ['release', 'docs'])
  assert.equal(document.excerpt, 'This is the excerpt.')
})

test('builds sorted documents and computes previous and next documents', () => {
  const documents = buildNewsDocuments({
    '../content/news/second-news.md': secondArticle,
    '../content/news/first-news.md': firstArticle,
  })

  assert.deepEqual(
    documents.map((document) => document.slug),
    ['first-news', 'second-news'],
  )

  const adjacent = getAdjacentNewsDocuments(documents, 'first-news')

  assert.equal(adjacent.previous, null)
  assert.equal(adjacent.next?.slug, 'second-news')
  assert.equal(getNewsDocumentBySlug(documents, 'second-news')?.title, 'Second News')
  assert.equal(getNewsDocumentBySlug(documents, 'missing-news'), null)
})

test('slugifies Chinese and duplicate headings into stable ids', () => {
  assert.equal(slugifyHeading('标题 跳转'), '标题-跳转')

  const parsed = parseNewsMarkdown(`---
title: Duplicate
date: 2026-06-09
---

## Repeat
## Repeat
`)

  assert.deepEqual(parsed.headings, [
    { id: 'repeat', level: 2, text: 'Repeat' },
    { id: 'repeat-2', level: 2, text: 'Repeat' },
  ])
})

test('normalizes markdown-decorated headings before building anchor ids', () => {
  const parsed = parseNewsMarkdown(`---
title: Decorated
date: 2026-06-09
---

### 1. **URL form** (common case)
### 2. \`useEffect\`: side effects
### Component<span style='color:red'>instance</span> state
`)

  assert.deepEqual(parsed.headings, [
    { id: '1-url-form-common-case', level: 3, text: '1. URL form (common case)' },
    { id: '2-useeffect-side-effects', level: 3, text: '2. useEffect: side effects' },
    { id: 'componentinstance-state', level: 3, text: 'Componentinstance state' },
  ])
})

test('filters documents by query and category', () => {
  const documents = buildNewsDocuments({
    '../content/news/second-news.md': secondArticle,
    '../content/news/first-news.md': firstArticle,
  })

  assert.deepEqual(getNewsCategories(documents), ['announcement'])
  assert.deepEqual(
    filterNewsDocuments(documents, { query: 'nested', category: 'all' }).map(
      (document) => document.slug,
    ),
    ['first-news'],
  )
  assert.deepEqual(
    filterNewsDocuments(documents, { query: 'docs', category: 'announcement' }).map(
      (document) => document.slug,
    ),
    ['first-news'],
  )
  assert.deepEqual(
    filterNewsDocuments(documents, { query: 'docs', category: 'missing' }),
    [],
  )
})
