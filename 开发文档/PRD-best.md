# 产品需求与最佳实践摘录

## 不再部署到 Vercel
- 部署策略：本地/自有服务器为主，容器化（Docker）可选。
- 分发策略：通过 GitHub 管理源代码与版本，不依赖 Serverless。

## 文档一致性
- README 需包含：首次推送与后续推送命令、运行方式、文件限制与下载策略。
- 与以下规范保持一致：处理规范.md、批量下载说明.md、上传限制改进总结.md、文件夹优化说明.md、项目上下文.md、优化总结.md。

## 操作指引（摘要）
- 首次推送：`git init` → `git add .` → `git commit` → `git branch -M main` → `git remote add origin` → `git push -u origin main`。
- 后续推送：`git add .` → `git commit` → `git push`；变更远程：`git remote set-url origin`。