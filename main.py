import os
import re
import html
import time
import sqlite3
import secrets
import logging
import uvicorn
from collections import defaultdict
import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("autotrade")

ADMIN_KEY = os.environ.get("ADMIN_KEY", "")          # ключ входа в /admin
BOT = os.environ.get("BOT_TOKEN", "")                # Telegram необязателен
CHAT = os.environ.get("CHAT_ID", "")

if len(ADMIN_KEY) < 12:
    raise SystemExit("ADMIN_KEY слишком короткий: нужно минимум 12 символов")

# ---------- база ----------
def db():
    c = sqlite3.connect("data.db", timeout=10)
    c.row_factory = sqlite3.Row
    return c

with db() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY, vacancy TEXT, name TEXT, phone TEXT,
        city TEXT, schedule TEXT, done INT DEFAULT 0, ts DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY, name TEXT, rating INT, text TEXT,
        ok INT DEFAULT 0, ts DEFAULT CURRENT_TIMESTAMP)""")   # ok: 0 ждёт, 1 опубликован, -1 скрыт
    c.execute("CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT)")
    try:
        c.execute("ALTER TABLE applications ADD COLUMN done INT DEFAULT 0")
    except sqlite3.OperationalError:
        pass

# ---------- режим техработ ----------
def _get(k, d=""):
    with db() as c:
        r = c.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    return r["v"] if r else d

MAINT = {"on": _get("maint_on", "0") == "1", "message": _get("maint_msg", "")}

MAINT_PAGE = """<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="robots" content="noindex">
<title>Технические работы — АВТОТРЕЙД</title>
<style>
:root{--bg:#f3f4f7;--card:#fff;--tx:#12151b;--mu:#667085;--bd:#e3e6ec;--ac:#ff7a1a;--ac2:#ffb347;--r:18px;--sh:0 10px 30px rgba(20,24,40,.08)}
@media (prefers-color-scheme:dark){:root{--bg:#0d0f13;--card:#171a20;--tx:#eef0f4;--mu:#97a0b0;--bd:#262b34;--sh:0 10px 30px rgba(0,0,0,.35);color-scheme:dark}}
*{box-sizing:border-box}html,body{max-width:100%;overflow-x:clip}
body{margin:0;min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;background:var(--bg);color:var(--tx);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.w{max-width:1040px;margin:0 auto;padding:0 18px;width:100%}
nav{position:sticky;top:0;z-index:50;background:rgba(11,13,17,.8);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid rgba(255,255,255,.07);color:#fff;padding-top:env(safe-area-inset-top,0px)}
nav .w{display:flex;justify-content:space-between;align-items:center;height:58px}
nav b{font-size:19px;letter-spacing:.6px}nav b i{color:var(--ac);font-style:normal}
nav span{font-size:14px;color:#c9cfd9}
.hero{position:relative;overflow:hidden;isolation:isolate;background:#0b0d11;color:#fff;padding:56px 0 100px;border-radius:0 0 32px 32px;text-align:center}
.hero:before{content:"";position:absolute;inset:0;z-index:-1;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse at 50% 30%,#000,transparent 72%);mask-image:radial-gradient(ellipse at 50% 30%,#000,transparent 72%)}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.42;animation:fl 12s ease-in-out infinite alternate;z-index:-1}
.b1{width:340px;height:340px;background:#ff7a1a;left:-90px;top:-110px}.b2{width:300px;height:300px;background:#2f6bff;right:-70px;bottom:-110px;animation-delay:-5s}
@keyframes fl{to{transform:translate(50px,36px) scale(1.18)}}
.gears{position:relative;width:130px;height:100px;margin:0 auto 14px;filter:drop-shadow(0 0 20px rgba(255,122,26,.45))}
.gears svg{position:absolute;fill:none;stroke:var(--ac);stroke-width:3;stroke-linejoin:round}
.g1{left:0;top:0;width:78px;height:78px;animation:rot 8s linear infinite}
.g2{right:0;bottom:0;width:58px;height:58px;stroke:var(--ac2)!important;animation:rot 6s linear infinite reverse}
@keyframes rot{to{transform:rotate(360deg)}}
.hero h1{font-size:clamp(30px,7vw,48px);line-height:1.1;letter-spacing:-.02em;font-weight:800;margin:0 0 14px}
.hero h1 span{background:linear-gradient(90deg,var(--ac),var(--ac2));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:#c3cad6;max-width:520px;margin:0 auto;font-size:17px}
.box{margin-top:-50px;position:relative;z-index:2;background:var(--card);border:1px solid var(--bd);border-radius:var(--r);padding:24px 22px;box-shadow:var(--sh);text-align:center;max-width:560px;margin-left:auto;margin-right:auto}
.box p{margin:0;color:var(--mu)}
.msg{margin:0 0 16px;padding:12px 16px;border-radius:14px;color:var(--tx);font-weight:600;background:rgba(255,122,26,.12);border:1px solid rgba(255,122,26,.35)}
.bar{height:6px;margin:20px 0 12px;border-radius:99px;background:var(--bd);overflow:hidden}
.bar i{display:block;width:35%;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--ac),var(--ac2));animation:m 1.6s ease-in-out infinite}
@keyframes m{0%{margin-left:-35%}100%{margin-left:100%}}
.box small{font-size:13px;color:var(--mu)}
footer{margin-top:auto;padding-top:64px}
footer div{background:#0b0d11;color:#97a0b0;text-align:center;padding:30px 18px;border-radius:32px 32px 0 0}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>
<nav><div class="w"><b>АВТО<i>ТРЕЙД</i></b><span>Вахта на месторождениях</span></div></nav>
<section class="hero"><div class="blob b1"></div><div class="blob b2"></div>
<div class="w">
<div class="gears"><svg class="g1" viewBox="0 0 64 64"><path d="M28 4h8l2 8 6 3 7-4 6 6-4 7 3 6 8 2v8l-8 2-3 6 4 7-6 6-7-4-6 3-2 8h-8l-2-8-6-3-7 4-6-6 4-7-3-6-8-2v-8l8-2 3-6-4-7 6-6 7 4 6-3z"/><circle cx="32" cy="32" r="9"/></svg><svg class="g2" viewBox="0 0 64 64"><path d="M28 4h8l2 8 6 3 7-4 6 6-4 7 3 6 8 2v8l-8 2-3 6 4 7-6 6-7-4-6 3-2 8h-8l-2-8-6-3-7 4-6-6 4-7-3-6-8-2v-8l8-2 3-6-4-7 6-6 7 4 6-3z"/><circle cx="32" cy="32" r="9"/></svg></div>
<h1>Технические <span>работы</span></h1>
<p>Мы обновляем сайт, чтобы он работал лучше.</p>
</div></section>
<main class="w"><div class="box">
{extra}
<p>Скоро всё заработает. Приносим извинения за неудобства, загляните чуть позже.</p>
<div class="bar"><i></i></div>
<small>Страница обновится сама, когда сайт снова будет доступен</small>
</div></main>
<footer><div>© ООО «АВТОТРЕЙД» · Автотранспортное предприятие</div></footer>
<script>
setInterval(function(){fetch("/",{cache:"no-store"}).then(function(r){if(r.status!==503)location.reload()}).catch(function(){})},20000);
</script>
</body></html>"""

# ---------- защита от спама ----------
hits = defaultdict(list)

def client_ip(r: Request):
    xf = r.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return xf or (r.client.host if r.client else "?")

def limited(ip, key, n, sec):
    """True, если с этого IP за sec секунд уже было n обращений."""
    now = time.time()
    k = (ip, key)
    hits[k] = [t for t in hits[k] if now - t < sec]
    if len(hits[k]) >= n:
        return True
    hits[k].append(now)
    return False

def check_admin(r: Request):
    given = r.headers.get("x-admin-key", "").encode()
    if not secrets.compare_digest(given, ADMIN_KEY.encode()):
        if limited(client_ip(r), "badkey", 10, 600):
            raise HTTPException(429, "too many attempts")
        raise HTTPException(403, "forbidden")

# ---------- Telegram (необязательное уведомление) ----------
async def notify(text):
    if not (BOT and CHAT):
        return
    try:
        async with httpx.AsyncClient(timeout=10) as h:
            r = await h.post(f"https://api.telegram.org/bot{BOT}/sendMessage",
                             json={"chat_id": CHAT, "text": text})
        if r.status_code != 200:
            log.warning("telegram status %s", r.status_code)
    except Exception as e:
        log.warning("telegram failed: %s", getattr(e, '__class__', {}).__name__ if hasattr(e, '__class__') else str(e))

# ---------- модели ----------
class Apply(BaseModel):
    vacancy: str = Field(max_length=120)
    name: str = Field(min_length=2, max_length=60)
    phone: str = Field(min_length=10, max_length=20)
    city: str = Field(min_length=2, max_length=60)
    schedule: str = Field(max_length=20)
    website: str = Field(default="", max_length=100)   # скрытое поле-ловушка для ботов

class Review(BaseModel):
    name: str = Field(default="Аноним", max_length=40)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=5, max_length=500)

class Maint(BaseModel):
    on: bool
    message: str = Field(default="", max_length=200)

class Flag(BaseModel):
    value: int = Field(ge=-1, le=1)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.middleware("http")
async def maintenance(request: Request, call_next):
    if MAINT["on"]:
        p = request.url.path
        if not (p == "/admin" or p.startswith("/api/admin")):   # админка работает всегда
            h = {"Retry-After": "3600", "Cache-Control": "no-store"}
            if p.startswith("/api/"):
                return JSONResponse({"detail": "maintenance"}, status_code=503, headers=h)
            m = MAINT["message"].strip()
            extra = f'<div class="msg">{html.escape(m)}</div>' if m else ""
            return HTMLResponse(MAINT_PAGE.replace("{extra}", extra), status_code=503, headers=h)
    return await call_next(request)

# ---------- публичные запросы сайта ----------
@app.post("/api/apply")
async def apply(a: Apply, request: Request, bg: BackgroundTasks):
    if a.website:                      # заполнила ловушка: молча «принимаем» и выбрасываем
        return {"ok": True}
    if len(re.sub(r"\D", "", a.phone)) < 10:
        raise HTTPException(422, "phone")
    if limited(client_ip(request), "apply", 5, 600):
        raise HTTPException(429, "too many")
    with db() as c:
        c.execute("INSERT INTO applications(vacancy,name,phone,city,schedule) VALUES(?,?,?,?,?)",
                  (a.vacancy, a.name, a.phone, a.city, a.
                   schedule))
    bg.add_task(notify, f"📩 Новый отклик\nВакансия: {a.vacancy}\nИмя: {a.name}\n"
                        f"Телефон: {a.phone}\nГород: {a.city}\nГрафик: {a.schedule}")
    return {"ok": True}

@app.post("/api/reviews")
async def add_review(r: Review, request: Request, bg: BackgroundTasks):
    if limited(client_ip(request), "review", 3, 600):
        raise HTTPException(429, "too many")
    with db() as c:
        c.execute("INSERT INTO reviews(name,rating,text) VALUES(?,?,?)", (r.name, r.rating, r.text))
    bg.add_task(notify, f"⭐️ Новый отзыв ({r.rating}/5) от {r.name}\n{r.text}\n\nМодерация: страница /admin на сайте")
    return {"ok": True}

@app.get("/api/reviews")
def public_reviews():
    with db() as c:
        rows = c.execute("SELECT name,rating,text FROM reviews WHERE ok=1 ORDER BY id DESC LIMIT 50")
        return [dict(x) for x in rows]

# ---------- админка ----------
@app.get("/admin")
def admin_page():
    return FileResponse("admin.html")

@app.get("/api/admin/data")
def admin_data(request: Request):
    check_admin(request)
    with db() as c:
        apps = [dict(x) for x in c.execute("SELECT * FROM applications ORDER BY id DESC LIMIT 1000")]
        revs = [dict(x) for x in c.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 300")]
    return {"applications": apps, "reviews": revs, "maintenance": MAINT}

@app.post("/api/admin/applications/{aid}")
def admin_app(aid: int, f: Flag, request: Request):
    check_admin(request)
    with db() as c:
        c.execute("UPDATE applications SET done=? WHERE id=?", (1 if f.value == 1 else 0, aid))
    return {"ok": True}

@app.post("/api/admin/reviews/{rid}")
def admin_review(rid: int, f: Flag, request: Request):
    check_admin(request)
    with db() as c:
        c.execute("UPDATE reviews SET ok=? WHERE id=?", (f.value, rid))
    return {"ok": True}

@app.post("/api/admin/maintenance")
def admin_maint(m: Maint, request: Request):
    check_admin(request)
    MAINT["on"], MAINT["message"] = m.on, m.message
    with db() as c:
        c.execute("INSERT OR REPLACE INTO settings(k,v) VALUES('maint_on',?)", ("1" if m.on else "0",))
        c.execute("INSERT OR REPLACE INTO settings(k,v) VALUES('maint_msg',?)", (m.message,))
    return {"ok": True}

app.mount("/", StaticFiles(directory="site", html=True), name="site")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
