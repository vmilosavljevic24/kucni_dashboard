const CLANOVI_PORODICE = ["Vasa", "Ana", "Jole"];
const API_URL = "/api";

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

// Pokreni sve kad se stranica učita
iscrtajDugmice();
ucitajHranjenja();