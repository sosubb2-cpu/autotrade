import os, re, time, sqlite3, secrets, logging
from collections import defaultdict
import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("autotrade")

ADMIN_KEY = os.environ["ADMIN_KEY"]          # ключ входа в /admin
BOT = os.environ.get("BOT_TOKEN", "")        # Telegram необязателен
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
    try:
        c.execute("ALTER TABLE applications ADD COLUMN done INT DEFAULT 0")
    except sqlite3.OperationalError:
        pass

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
        log.warning("telegram failed: %s", e.__class__.__name__)   # токен в лог не пишем

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

class Flag(BaseModel):
    value: int = Field(ge=-1, le=1)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

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
                  (a.vacancy, a.name, a.phone, a.city, a.schedule))
    bg.add_task(notify, f"📩 Новый отклик\nВакансия: {a.vacancy}\nИмя: {a.name}\n"
                        f"Телефон: {a.phone}\nГород: {a.city}\nГрафик: {a.schedule}")
    return {"ok": True}

@app.post("/api/reviews")
async def add_review(r: Review, request: Request, bg: BackgroundTasks):
    if limited(client_ip(request), "review", 3, 600):
        raise HTTPException(429, "too many")
    with db() as c:
        c.execute("INSERT INTO reviews(name,rating,text) VALUES(?,?,?)", (r.name, r.rating, r.text))
    bg.add_task(notify, f"⭐ Новый отзыв ({r.rating}/5) от {r.name}\n{r.text}\n\nМодерация: страница /admin на сайте")
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
    return {"applications": apps, "reviews": revs}

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

app.mount("/", StaticFiles(directory="site", html=True), name="site")   # всегда в самом конце
