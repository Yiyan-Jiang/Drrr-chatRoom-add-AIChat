# 好友搜索验收记录

日期：2026-10-22。

## 行为与范围

- Home 右侧好友栏支持按昵称或用户名进行包含匹配，忽略大小写和关键词首尾空白。
- 回车或“搜索”提交查询，查询覆盖当前账号的全部好友，先筛选再分页。
- 新查询回到第一页；“×”清空输入并恢复完整列表第一页。
- 加载中、无匹配和加载失败分别显示提示；失败后可以使用相同关键词重新搜索。
- 好友栏收起、展开时保留搜索状态；搜索结果仍可进入真实私聊页面。

## 静态检查

在 `frontend` 目录执行，均退出 `0`：

```powershell
.\node_modules\.bin\tsc.cmd -b --noEmit
.\node_modules\.bin\eslint.cmd src/api/friends.ts src/components/layout/RightSidebar/RightSidebar.tsx
.\node_modules\.bin\prettier.cmd --check src/api/friends.ts src/components/layout/RightSidebar/RightSidebar.tsx
```

在仓库根目录执行 `ruff format --check backend/normal_system/repositories/friend.py backend/normal_system/routers/friend.py`，退出 `0`。

`ruff check` 没有全部通过：两个 Python 文件共有 10 条既有问题（2 条导入排序、8 条 `Depends` 默认参数规则）。已将当前诊断与 `HEAD` 逐文件比较，规则、消息和数量一致，本次未新增诊断。没有为本次搜索修改无关代码或禁用规则。

## 真实服务冒烟与浏览器 E2E

- 执行 `npm run test:smoke`。新增断言在实现前因“无匹配搜索仍返回好友”失败；实现后全部业务场景通过，测试资源已清理。
- 通过本机 Docker 的真实门禁、注册、登录、好友申请和接受接口准备一个主账号、九个好友及一个非好友账号。
- 本机 Edge 在 1440 × 1000 视口从真实登录页进入 Home，验证原列表第二页的好友可通过搜索找到；同时验证大小写、首尾空格、中文昵称、用户名和字面 `%` 匹配。
- 搜索命中的九个好友仍按八条分页；切换关键词与清空后回到第一页。非好友用户名和不存在的关键词均显示“没有匹配的好友”。
- 仅在 HTTP 边界模拟 503，界面显示失败且不展示旧结果；恢复真实接口后相同关键词可重新查询。
- 搜索后收起、展开保留结果，点击好友可以进入对应私聊页面。没有浏览器脚本异常。
- 浏览器 E2E 的全部临时账号通过真实删除接口清理，并逐个读回 404；好友关系随账号清理。

未运行单元测试，未构建打包。浏览器验收不包含移动端。
