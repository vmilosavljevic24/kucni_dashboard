from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from datetime import datetime, date
from database import init_db, get_db
from models import NovoHranjenje, Hranjenje, NoviPosao, Posao
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

@app.get("/api/poslovi", response_model=list[Posao])
def get_poslovi():
    """Vraća sve aktivne (nezavršene) poslove, najnoviji prvo."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM poslovi WHERE zavrsen = 0 ORDER BY kreiran DESC"
        )
        redovi = cursor.fetchall()

    return [dict(red) for red in redovi]


@app.post("/api/poslovi", response_model=Posao)
def dodaj_posao(posao: NoviPosao):
    """Dodaje novi posao na listu."""
    vreme_sada = datetime.now().isoformat(timespec="seconds")

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO poslovi (naziv, zavrsen, kreiran) VALUES (?, 0, ?)",
            (posao.naziv, vreme_sada)
        )
        conn.commit()
        novi_id = cursor.lastrowid

    return {"id": novi_id, "naziv": posao.naziv, "zavrsen": 0, "kreiran": vreme_sada, "zavrsen_u": None}


@app.patch("/api/poslovi/{posao_id}/zavrsi")
def zavrsi_posao(posao_id: int):
    """Označava posao kao završen (postavlja zavrsen=1 i beleži vreme)."""
    vreme_sada = datetime.now().isoformat(timespec="seconds")

    with get_db() as conn:
        conn.execute(
            "UPDATE poslovi SET zavrsen = 1, zavrsen_u = ? WHERE id = ?",
            (vreme_sada, posao_id)
        )
        conn.commit()

    return {"poruka": "Posao oznacen kao zavrsen", "id": posao_id}

from models import NovoHranjenje, Hranjenje, NoviPosao, Posao, NoviArtikal, Artikal

@app.get("/api/kupovina", response_model=list[Artikal])
def get_kupovina():
    """Vraća sve artikle - i kupljene i nekupljene (mama vidi ceo spisak)."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM kupovina ORDER BY kupljen ASC, kreiran DESC"
        )
        redovi = cursor.fetchall()

    return [dict(red) for red in redovi]


@app.post("/api/kupovina", response_model=Artikal)
def dodaj_artikal(artikal: NoviArtikal):
    """Dodaje novi artikal na spisak."""
    vreme_sada = datetime.now().isoformat(timespec="seconds")

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO kupovina (artikal, kupljen, kreiran) VALUES (?, 0, ?)",
            (artikal.artikal, vreme_sada)
        )
        conn.commit()
        novi_id = cursor.lastrowid

    return {"id": novi_id, "artikal": artikal.artikal, "kupljen": 0, "kreiran": vreme_sada}


@app.patch("/api/kupovina/{artikal_id}/prekini")
def prekini_artikal(artikal_id: int):
    """Prebacuje status kupljen/nekupljen (toggle) - mama cekira/decekira u prodavnici."""
    with get_db() as conn:
        # Prvo pročitamo trenutni status
        cursor = conn.execute("SELECT kupljen FROM kupovina WHERE id = ?", (artikal_id,))
        red = cursor.fetchone()

        if red is None:
            return {"greska": "Artikal ne postoji"}

        novi_status = 0 if red["kupljen"] == 1 else 1

        conn.execute("UPDATE kupovina SET kupljen = ? WHERE id = ?", (novi_status, artikal_id))
        conn.commit()

    return {"poruka": "Status promenjen", "id": artikal_id, "kupljen": novi_status}


@app.delete("/api/kupovina/{artikal_id}")
def obrisi_artikal(artikal_id: int):
    """Trajno brise artikal sa spiska (npr. pogresno dodat)."""
    with get_db() as conn:
        conn.execute("DELETE FROM kupovina WHERE id = ?", (artikal_id,))
        conn.commit()

    return {"poruka": "Artikal obrisan", "id": artikal_id}

@app.get("/api/hranjenja/status")
def status_henrija():
    """Vraca informaciju o tome kada je Henri poslednji put hranjen i koliko je davno to bilo."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM hranjenja ORDER BY vreme DESC LIMIT 1"
        )
        poslednje = cursor.fetchone()

    if poslednje is None:
        return {"hranjen": False, "poruka": "Henri danas nije hranjen!", "ko": None, "pre_koliko_sati": None}

    vreme_hranjenja = datetime.fromisoformat(poslednje["vreme"])
    proteklo = datetime.now() - vreme_hranjenja
    sati = proteklo.total_seconds() / 3600

    if sati < 4:
        poruka = f"Hranjen pre {round(sati * 60)} min" if sati < 1 else f"Hranjen pre {round(sati, 1)}h"
    else:
        poruka = f"Nije hranjen već {round(sati, 1)}h!"

    return {
        "hranjen": sati < 8,
        "poruka": poruka,
        "ko": poslednje["ko_je_hranio"],
        "pre_koliko_sati": round(sati, 2)
    }

# Servira frontend fajlove (HTML, JS, CSS) - MORA biti poslednje u fajlu
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")    