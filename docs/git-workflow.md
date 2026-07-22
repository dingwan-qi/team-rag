# Git 分支工作流

## 分支

- `main`：稳定版本。
- `develop`：集成分支。
- `feature/ui-webui`：成员 1。
- `feature/document-ingestion`：成员 2。
- `feature/native-advanced-rag`：成员 3。
- `feature/graphrag`：成员 4。
- `feature/agentic-integration`：成员 5。

## 初始化仓库

```bash
git init -b main
git add .
git commit -m "chore: initialize teamrag project"
git checkout -b develop
```

## 成员创建功能分支

```bash
git checkout develop
git pull origin develop
git checkout -b feature/ui-webui
```

## 提交与推送

```bash
pytest -q
ruff check .
git add .
git commit -m "feat: implement webui chat page"
git push -u origin feature/ui-webui
```

## Pull Request 规则

- feature 分支只能向 `develop` 提 PR。
- PR 必须包含功能说明、测试方法、修改文件和风险说明。
- 至少一名成员 Review。
- CI 必须通过。
- 禁止直接向 `main` force push。
- 五名成员提交的是 `handoff/` 中已完成的文件，不需要重新开发。

## 发布到 main

```bash
git checkout develop
git pull origin develop
pytest -q
ruff check .
git checkout main
git merge --no-ff develop
git tag v0.1.0
git push origin main --tags
```
