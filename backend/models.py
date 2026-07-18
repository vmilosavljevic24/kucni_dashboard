from pydantic import BaseModel

class NovoHranjenje(BaseModel):
    """Podaci koje frontend šalje kad neko označi da je nahranio Henrija."""
    ko_je_hranio: str


class Hranjenje(BaseModel):
    """Podaci koje backend vraća - jedan zapis o hranjenju."""
    id: int
    ko_je_hranio: str
    vreme: str

class NoviPosao(BaseModel):
    """Podaci koje frontend šalje kad se dodaje novi posao."""
    naziv: str


class Posao(BaseModel):
    """Podaci koje backend vraća za jedan posao."""
    id: int
    naziv: str
    zavrsen: int
    kreiran: str
    zavrsen_u: str | None = None