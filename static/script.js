const API_BASE = "";

let selectedCandidateNomor = null;
let currentNIS = localStorage.getItem("nis");

// --------------------------------------------------
// LOAD KANDIDAT
// --------------------------------------------------
async function loadCandidates() {
    const res = await fetch("/api/candidates");
    const data = await res.json();

    let list = document.getElementById("candidatesList");
    if (!list) return;

    list.innerHTML = "";

    data.candidates.forEach(c => {
        list.innerHTML += `
        <div class="candidate-card">
            <img src="/candidate_photo/${c.photo}" class="candidate-photo">
            <h2>Paslon ${c.nomor}</h2>
            <h3>${c.ketua} & ${c.wakil}</h3>

            <div class="visi-misi">
                <h4>Visi</h4>
                <p>${c.visi}</p>

                <h4>Misi</h4>
                <p>${c.misi}</p>
            </div>

            <button class="btn-vote" onclick="selectCandidate(${c.nomor}, 'Paslon ${c.nomor}')">
                Pilih
            </button>
        </div>
        `;
    });
}

// --------------------------------------------------
// PILIH KANDIDAT
// --------------------------------------------------
function selectCandidate(nomor, name) {
    selectedCandidateNomor = nomor;
    document.getElementById("selectedCandidateName").innerText = name;
    document.getElementById("voteModal").classList.add("active");
}

function closeModal() {
    document.getElementById("voteModal").classList.remove("active");
}

// --------------------------------------------------
// KONFIRMASI VOTE
// --------------------------------------------------
async function confirmVote() {
    const res = await fetch(`/api/vote`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nis: currentNIS,
            candidate_id: selectedCandidateNomor
        })
    });

    const data = await res.json();
    alert(data.message);

    if (data.status === "success") {
        window.location.href = "/done";
    }
}

// --------------------------------------------------
// LOGIN HANDLER
// --------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            let nis = document.getElementById("nis").value.trim();
            if (!nis) {
                alert("Masukkan NIS terlebih dahulu!");
                return;
            }

            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nis })
            });

            const data = await res.json();
            alert(data.message);

            if (data.status === "success") {
                localStorage.setItem("nis", nis);
                window.location.href = "/vote";
            }
        });
    }
});

// --------------------------------------------------
// LOGOUT
// --------------------------------------------------
function logout() {
    localStorage.removeItem("nis");
    window.location.href = "/login";
}
