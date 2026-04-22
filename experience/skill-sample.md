# Skill: Sample Development Workflow

## 🔧 Git Branch Cleanup
**日期：** 2026-04-22
**情境：** 開發完成後需要清理本地已併入 main 的分支。
**解法：**
- 使用 `git branch --merged | grep -v "\*" | xargs -n 1 git branch -d`
- **關鍵檔案/路徑：** repo-root
**keywords：** git, cleanup, branch-management

## 🔧 Python Environment Refresh
**日期：** 2026-04-22
**情境：** 依賴庫更新後虛擬環境出現衝突。
**解法：**
- 刪除 `.venv` 或 `__pycache__`
- 執行 `pip install --no-cache-dir -r requirements.txt`
**keywords：** python, pip, venv, cache
