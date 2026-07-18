from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from datetime import datetime, date
from database import init_db, get_db
from models import NovoHranjenje, Hranjenje

app = FastAPI(title="Pametni Porodični Dashboard")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/status")
def status():
    return {"poruka": "Dashboard backend radi!"}


@app.get("/api/hranjenja", response_model=list[Hranjenje])
def get_hranjenja():
    """Vraća sva hranjenja za danas, najnovije prvo."""
    danas = date.today().isoformat()  # npr. "2026-07-14"

    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM hranjenja WHERE vreme LIKE ? ORDER BY vreme DESC",
            (f"{danas}%",)
        )
        redovi = cursor.fetchall()

    return [dict(red) for red in redovi]


@app.post("/api/hranjenja", response_model=Hranjenje)
def dodaj_hranjenje(hranjenje: NovoHranjenje):
    """Beleži novo hranjenje sa trenutnim vremenom."""
    vreme_sada = datetime.now().isoformat(timespec="seconds")
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO hranjenja (ko_je_hranio, vreme) VALUES (?, ?)",
            (hranjenje.ko_je_hranio, vreme_sada)
        )
        conn.commit()
        novi_id = cursor.lastrowid

    return {"id": novi_id, "ko_je_hranio": hranjenje.ko_je_hranio, "vreme": vreme_sada}

# Servira frontend fajlove (HTML, JS, CSS) - MORA biti poslednje u fajlu
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")    