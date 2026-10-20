# 独立发帖页实现计划

> 执行方式：按 subagent-driven-development 技能派发 `gpt-5.6-luna` 实现，主代理审查与执行桌面 E2E。项目约定优先：只做冒烟/E2E。用户本次明确要求每阶段一个 commit，不推送或打包。

**目标：** 将浮动发帖表单迁移到独立桌面编辑页，提供共享 Markdown 实时预览、目录、隐藏滚动条和离开确认。

**架构：** 新页面负责本地表单、发布与导航；帖子列表只提供路由入口。预览复用 `PostMarkdownArticle`，目录取实际渲染标题；目录的局部滚动不修改路由。

**技术栈：** React 19、TypeScript、React Router 7、Tailwind CSS、现有 react-markdown/rehype-pretty-code 与 Axios。

## 任务一：复现与实施

文件：

- 新建 `frontend/src/pages/subPage/PostCompose.tsx`：独立页面、标题正文、发布、站内/关闭提醒。
- 新建 `frontend/src/features/posts/PostComposePreview.tsx`（若需要）：正文容器、实际标题目录和局部滚动；不另写 Markdown 解析器。
- 修改 `frontend/src/components/posts/PostEditor.tsx`：仅保留到 `/posts/new` 的发帖入口，或在列表内直接使用链接并移除已无用途的表单文件。
- 修改 `frontend/src/pages/subPage/PostsFeed.tsx`：删除发帖请求状态，保留列表功能和入口。
- 修改 `frontend/src/routers/index.tsx`：增加带同样守卫的独立路由。
- 按需在新页局部 CSS 添加隐藏滚动条规则，不影响新闻目录。
- 仅在必要时扩展 `PostMarkdownArticle.tsx` 的可选标题/属性能力，保持详情页现状。

步骤：

- [ ] 从本机浏览器打开帖子入口，记录旧浮动窗口/缺少独立页面的失败证据。
- [ ] 核对 React Router 本地安装的 `useBlocker`、`useBeforeUnload` API，并实现离开确认；不要用全局 popstate 拦截。
- [ ] 实现页面与预览目录，保留现有接口及限制；错误处理仅捕获能够显示给用户的请求失败。
- [ ] 目录读取已渲染标题，重复标题有独立定位标识；异步高亮完成后更新，卸载清理观察器。
- [ ] 在输入有内容时提醒离开；成功后解除提醒再跳转；无持久化草稿。
- [ ] 编辑/预览/目录独立滚动且滚动条隐藏，固定底部区域不覆盖正文。
- [ ] 自查差异并运行静态检查，不执行 build 或单元测试。

## 任务二：审查与验收

- [ ] 由主代理审查需求符合性与代码质量，修复发现的问题。
- [ ] 运行 `npm --prefix frontend exec -- tsc -b --noEmit`（如当前项目配置不允许则直接运行 `frontend/node_modules/typescript/bin/tsc -b --noEmit`），以及 `npm --prefix frontend run lint`。
- [ ] 使用已有 Prettier 对本次前端文件进行检查，运行 `git diff --check`。
- [ ] 桌面浏览器 E2E 验证布局、真实渲染、目录/长文/滚动、空输入、提交状态、错误保留、离开确认、刷新、发布后详情。
- [ ] 实际发布链路仅访问本机 Docker API；使用临时账号/帖子并在结束时清理，不接入外部业务服务。
- [ ] 记录实际命令、结果和限制；保留用户已有 Docker 改动，不纳入本次提交，不推送或打包。

## 提交阶段

1. 设计与计划审查通过：`docs: 确定独立发帖页设计与实施计划`。
2. 实现及相关静态检查通过：`feat(posts): 增加独立 Markdown 发帖与实时预览`。
3. 最终测试通过并记录结果：`docs(test): 记录独立发帖页端到端验收结果`；若新增真实 E2E 脚本则使用 `test(posts)` 类型。

每次精确暂存本阶段文件，保留 Husky/lint-staged，不使用 `git add .`，不暂存此前 Docker 修复。
