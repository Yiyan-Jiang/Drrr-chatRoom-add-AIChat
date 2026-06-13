---
title: 新闻流实施记录
date: 2026-06-07
author: admin
category: engineering
tags: react,vite
---

第一阶段采用 React/Vite 的静态导入方案，不直接引入 VitePress。

<!-- more -->

## 技术选择

`import.meta.glob` 会在构建期收集 Markdown 文件，React 页面只消费已经整理好的文档数组。

## 数据字段

每篇文章会包含：

1. slug
2. title
3. date
4. excerpt
5. headings

## 风险

从旧博客迁移文章时，需要先修正乱码和图片路径。
