
import os
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

app = FastAPI(title="Editorial Studio 投稿審查系統")

secret = os.getenv("SESSION_SECRET")
if not secret:
    raise RuntimeError("請先在 .env 設定 SESSION_SECRET")

app.add_middleware(
    SessionMiddleware,
    secret_key=secret,
    same_site="lax",
    https_only=False
)

templates = Jinja2Templates(directory="templates")


def redirect(url="/"):
    return RedirectResponse(url, status_code=303)


def get_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, role FROM users WHERE id=%s",
                (user_id,)
            )
            row = cur.fetchone()

    if row:
        return dict(id=row[0], username=row[1], role=row[2])
    return None


def require_role(request, role):
    user = get_user(request)
    if not user:
        raise HTTPException(401, "請先登入")
    if user["role"] != role:
        raise HTTPException(403, "沒有操作權限")
    return user


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.post("/login")
def login(request: Request, username: str = Form(...)):
    # 本機課堂展示：選擇測試帳號，不使用密碼
    if username not in ("author1", "editor1"):
        raise HTTPException(400, "無效的測試帳號")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM users WHERE username=%s",
                (username,)
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(404, "測試帳號不存在")

    request.session.clear()
    request.session["user_id"] = row[0]
    return redirect()


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/login")


@app.get("/")
def dashboard(request: Request):
    user = get_user(request)
    if not user:
        return redirect("/login")

    with get_connection() as conn:
        with conn.cursor() as cur:
            if user["role"] == "author":
                cur.execute("""
                    SELECT id, category, title, content, status,
                           created_at
                    FROM articles
                    WHERE author_id=%s
                    ORDER BY id DESC
                """, (user["id"],))
            else:
                cur.execute("""
                    SELECT a.id, a.category, a.title, a.content,
                           a.status, a.created_at, u.username
                    FROM articles a
                    JOIN users u ON a.author_id=u.id
                    WHERE a.status='reviewing'
                    ORDER BY a.id DESC
                """)

            rows = cur.fetchall()

    articles = []
    for r in rows:
        articles.append({
            "id": r[0],
            "category": r[1],
            "title": r[2],
            "content": r[3],
            "status": r[4],
            "created_at": r[5],
            "author": r[6] if len(r) > 6 else user["username"]
        })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user, "articles": articles}
    )


@app.post("/articles/create")
def create_article(
    request: Request,
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    user = require_role(request, "author")

    category = category.strip()
    title = title.strip()
    content = content.strip()

    if not category or not title or not content:
        raise HTTPException(400, "所有欄位都必須填寫")

    if len(category) > 100 or len(title) > 200:
        raise HTTPException(400, "類別或標題過長")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO articles
                    (author_id, category, title, content, status)
                VALUES (%s, %s, %s, %s, 'draft')
            """, (user["id"], category, title, content))

    return redirect()


@app.post("/articles/{article_id}/update")
def update_article(
    article_id: int,
    request: Request,
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    user = require_role(request, "author")

    category = category.strip()
    title = title.strip()
    content = content.strip()

    if not category or not title or not content:
        raise HTTPException(400, "所有欄位都必須填寫")

    if len(category) > 100 or len(title) > 200:
        raise HTTPException(400, "類別或標題過長")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET category=%s, title=%s, content=%s,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND author_id=%s AND status='draft'
            """, (category, title, content, article_id, user["id"]))
            if cur.rowcount == 0:
                raise HTTPException(403, "只能編輯自己的草稿")

    return redirect()


@app.post("/articles/{article_id}/delete")
def delete_article(article_id: int, request: Request):
    user = require_role(request, "author")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM articles
                WHERE id=%s AND author_id=%s AND status='draft'
            """, (article_id, user["id"]))
            if cur.rowcount == 0:
                raise HTTPException(403, "只能刪除自己的草稿")

    return redirect()


@app.post("/articles/{article_id}/submit")
def submit_article(article_id: int, request: Request):
    user = require_role(request, "author")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET status='reviewing',
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND author_id=%s AND status='draft'
            """, (article_id, user["id"]))
            if cur.rowcount == 0:
                raise HTTPException(403, "只有自己的草稿可以送審")

    return redirect()


@app.post("/articles/{article_id}/approve")
def approve_article(article_id: int, request: Request):
    require_role(request, "editor")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET status='approved',
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND status='reviewing'
            """, (article_id,))
            if cur.rowcount == 0:
                raise HTTPException(409, "稿件已不在審查中")

    return redirect()


@app.post("/articles/{article_id}/return")
def return_article(article_id: int, request: Request):
    require_role(request, "editor")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET status='draft',
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND status='reviewing'
            """, (article_id,))
            if cur.rowcount == 0:
                raise HTTPException(409, "稿件已不在審查中")

    return redirect()
