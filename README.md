
# 投稿審查管理系統

## 專案介紹

本專案使用 Python FastAPI、PostgreSQL、HTML、CSS
開發投稿審查管理網站。

系統分為「作者」與「編輯」兩種角色，
透過不同權限完成投稿、審查與退回流程。

## 系統功能

### 作者
- 查看自己的投稿清單（類別、標題、審查狀態）
- 新增投稿
- 編輯尚未送出的稿件
- 刪除編輯中的稿件
- 送出投稿：編輯中 → 審查中

### 編輯
- 查看待審查清單
- 查看稿件作者、類別、標題與文章內容
- 通過稿件：審查中 → 已通過
- 退回稿件：審查中 → 編輯中

### 審查狀態
- 編輯中（draft）
- 審查中（reviewing）
- 已通過（approved）

## 使用技術

- Python 3
- FastAPI
- PostgreSQL
- Adminer
- HTML / CSS
- GitHub

## 安裝與執行

### 1. 下載專案

```bash
git clone https://github.com/a20060405/Article-Review-System.git
cd Article-Review-System
```

### 2. 安裝套件

```bash
python3 -m pip install -r requirements.txt
```

### 3. 建立 PostgreSQL 資料庫

建立名為 `article_review` 的資料庫。

使用 Adminer 匯入 `article_review.sql`，
建立 users 與 articles 資料表。

### 4. 設定環境變數

在專案根目錄建立 `.env`：

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=article_review
DB_USER=postgres
DB_PASSWORD=你的資料庫密碼
SESSION_SECRET=自行產生的隨機金鑰
```

SESSION_SECRET 可用以下指令產生：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. 建立測試帳號

```bash
python3 create_users.py
```

### 6. 啟動網站

```bash
python3 -m uvicorn main:app --reload
```

在瀏覽器開啟：

http://127.0.0.1:8000/login

## 測試角色

| 帳號 | 角色 |
|---|---|
| author1 | 作者 |
| editor1 | 編輯 |

本專案採用無密碼角色選擇，
僅供本機課堂作業測試使用。

## 操作流程

1. 選擇作者登入。
2. 新增一篇投稿並儲存為草稿。
3. 送出投稿，狀態變成「審查中」。
4. 切換編輯身分。
5. 查看待審查稿件。
6. 選擇通過或退回。
7. 回到作者身分查看稿件狀態。
