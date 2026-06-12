---
title: 静态新闻流上线准备
date: 2026-06-09
author: admin
category: announcement
tags: news,markdown
---

新闻流将从占位页面改成静态 Markdown 文档区，先支持文章列表、摘要和详情页。

<!-- more -->

## 为什么改成静态文档

当前新闻流页面还没有真实数据源。静态 Markdown 可以先把公告、更新日志和说明文档沉淀下来，不依赖后端接口。

## 第一阶段范围

- 建立文档数据模型
- 解析 frontmatter
- 提取摘要和标题目录
- 按日期排序

### 后续能力

详情页会继续补 Markdown 渲染、标题跳转、上一篇和下一篇导航。
