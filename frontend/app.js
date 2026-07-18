const CLANOVI_PORODICE = ["Vasa", "Ana", "Jole"];
const API_URL = "/api";

// --- Prebacivanje tabova ---
function prikaziTab(imeTaba) {
    // Sakrij sve sekcije, pa prikaži samo izabranu
    document.querySelectorAll(".tab-sadrzaj").forEach(sekcija => {
        sekcija.classList.add("hidden");
    });
    document.getElementById(`tab-${imeTaba}`).classList.remove("hidden");

    // Vizuelno oznaci aktivno dugme (plavo), ostala vrati na normalno
    document.querySelectorAll(".tab-dugme").forEach(dugme => {
        if (dugme.dataset.tab === imeTaba) {
            dugme.classList.add("bg-blue-500", "text-white");
            dugme.classList.remove("text-gray-500");
        } else {
            dugme.classList.remove("bg-blue-500", "text-white");
            dugme.classList.add("text-gray-500");
        }
    });
}

// Svako dugme sa klasom .tab-dugme (i gore i dole) reaguje na klik
document.querySelectorAll(".tab-dugme").forEach(dugme => {
    dugme.addEventListener("click", () => prikaziTab(dugme.dataset.tab));
});

// Pri učitavanju stranice, prikazi Henri tab kao pocetni
prikaziTab("henri");
// Kreira dugmiće za svakog člana porodice
function iscrtajDugmice() {
    const kontejner = document.getElementById("dugmici-clanovi");
    kontejner.innerHTML = "";

    CLANOVI_PORODICE.forEach(ime => {
        const dugme = document.createElement("button");
        dugme.textContent = ime;
        dugme.className = "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600";
        dugme.addEventListener("click", () => nahraniHenrija(ime));
        kontejner.appendChild(dugme);
    });
}

// Šalje POST zahtev kad neko klikne svoje ime
async function nahraniHenrija(ime) {
    await fetch(`${API_URL}/hranjenja`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ko_je_hranio: ime })
    });

    ucitajHranjenja(); // osveži tabelu odmah nakon dodavanja
    ucitajStatusHenrija(); // osveži status hranjenja
}

// Učitava i prikazuje listu hranjenja
async function ucitajHranjenja() {
    const odgovor = await fetch(`${API_URL}/hranjenja`);
    const podaci = await odgovor.json();

    const tabela = document.getElementById("tabela-hranjenja");
    tabela.innerHTML = "";

    podaci.forEach(zapis => {
        const red = document.createElement("tr");
        red.innerHTML = `
            <td class="py-1">${zapis.ko_je_hranio}</td>
            <td class="py-1">${zapis.vreme.split("T")[1]}</td>
        `;
        tabela.appendChild(red);
    });
}

// Učitava i prikazuje aktivne poslove
async function ucitajPoslove() {
    const odgovor = await fetch(`${API_URL}/poslovi`);
    const poslovi = await odgovor.json();

    const lista = document.getElementById("lista-poslova");
    lista.innerHTML = "";

    poslovi.forEach(posao => {
        const stavka = document.createElement("li");
        stavka.className = "flex items-center justify-between border-b pb-2";
        stavka.innerHTML = `
            <span>${posao.naziv}</span>
            <button class="text-sm px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
                Gotovo
            </button>
        `;

        // Dugme "Gotovo" - vezujemo event ovde, ne u innerHTML (lakše za rad sa posao.id)
        stavka.querySelector("button").addEventListener("click", () => zavrsiPosao(posao.id));

        lista.appendChild(stavka);
    });
}

// Dodaje novi posao
async function dodajPosao() {
    const input = document.getElementById("input-novi-posao");
    const naziv = input.value.trim();

    if (!naziv) return; // ne šalji prazan unos

    await fetch(`${API_URL}/poslovi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ naziv: naziv })
    });

    input.value = ""; // očisti input posle dodavanja
    ucitajPoslove();
}

// Označava posao kao završen
async function zavrsiPosao(id) {
    await fetch(`${API_URL}/poslovi/${id}/zavrsi`, {
        method: "PATCH"
    });

    ucitajPoslove(); // osveži listu - završeni posao nestaje sa liste
}

// Event listeneri
document.getElementById("dugme-dodaj-posao").addEventListener("click", dodajPosao);
document.getElementById("input-novi-posao").addEventListener("keydown", (e) => {
    if (e.key === "Enter") dodajPosao();
});
// Učitava i prikazuje spisak za kupovinu
async function ucitajKupovinu() {
    const odgovor = await fetch(`${API_URL}/kupovina`);
    const artikli = await odgovor.json();

    const lista = document.getElementById("lista-kupovina");
    lista.innerHTML = "";

    artikli.forEach(stavkaPodaci => {
        const stavka = document.createElement("li");
        stavka.className = "flex items-center justify-between border-b pb-2";

        // Precrtan tekst ako je vec kupljen
        const stilTeksta = stavkaPodaci.kupljen ? "line-through text-gray-400" : "";

        stavka.innerHTML = `
            <label class="flex items-center gap-2 flex-1">
                <input type="checkbox" ${stavkaPodaci.kupljen ? "checked" : ""}>
                <span class="${stilTeksta}">${stavkaPodaci.artikal}</span>
            </label>
            <button class="text-sm px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600">
                Obriši
            </button>
        `;

        stavka.querySelector("input[type=checkbox]").addEventListener("change", () => prekiniArtikal(stavkaPodaci.id));
        stavka.querySelector("button").addEventListener("click", () => obrisiArtikal(stavkaPodaci.id));

        lista.appendChild(stavka);
    });
}

// Dodaje novi artikal
async function dodajArtikal() {
    const input = document.getElementById("input-novi-artikal");
    const naziv = input.value.trim();

    if (!naziv) return;

    await fetch(`${API_URL}/kupovina`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artikal: naziv })
    });

    input.value = "";
    ucitajKupovinu();
}

// Menja status kupljeno/nekupljeno
async function prekiniArtikal(id) {
    await fetch(`${API_URL}/kupovina/${id}/prekini`, { method: "PATCH" });
    ucitajKupovinu();
}

// Briše artikal
async function obrisiArtikal(id) {
    await fetch(`${API_URL}/kupovina/${id}`, { method: "DELETE" });
    ucitajKupovinu();
}

// Event listeneri
document.getElementById("dugme-dodaj-artikal").addEventListener("click", dodajArtikal);
document.getElementById("input-novi-artikal").addEventListener("keydown", (e) => {
    if (e.key === "Enter") dodajArtikal();
});

async function ucitajStatusHenrija() {
    const odgovor = await fetch(`${API_URL}/hranjenja/status`);
    const status = await odgovor.json();

    const box = document.getElementById("status-henri");
    box.textContent = status.ko ? `${status.poruka} (${status.ko})` : status.poruka;

    // Boja zavisi od toga koliko je davno hranjen
    box.classList.remove("bg-green-500", "bg-yellow-500", "bg-red-500");

    if (status.pre_koliko_sati === null || status.pre_koliko_sati >= 8) {
        box.classList.add("bg-red-500");
    } else if (status.pre_koliko_sati >= 4) {
        box.classList.add("bg-yellow-500");
    } else {
        box.classList.add("bg-green-500");
    }
}
// Pokreni pri učitavanju
ucitajKupovinu();
// Pokreni pri učitavanju
ucitajPoslove();
// Pokreni sve kad se stranica učita
iscrtajDugmice();
ucitajHranjenja();
ucitajStatusHenrija();