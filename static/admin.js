// static/admin.js
const API_BASE = window.location.origin;

function qs(s){ return document.querySelector(s); }
function qsa(s){ return [...document.querySelectorAll(s)]; }
function showToast(msg){ alert(msg); }

// ----- NAV -----
qsa('.nav-btn').forEach(btn=>{
    btn.addEventListener('click', ()=>{
        qsa('.nav-btn').forEach(b=>b.classList.remove('active'));
        btn.classList.add('active');

        qsa('.tab').forEach(t=>t.classList.remove('active'));
        document.getElementById(btn.dataset.target).classList.add('active');

        if(btn.dataset.target === "tab-voters") loadVoters();
        if(btn.dataset.target === "tab-kandidat") loadCandidates();
        if(btn.dataset.target === "tab-statistik") loadStatistik();
    });
});

// IMPORT EXCEL
let previewRows = [];
const excelFile = qs('#excelFile');

qs('#btnParseExcel').addEventListener('click', ()=>{
    const file = excelFile.files[0];
    if(!file) return showToast("Pilih file Excel dulu");

    const reader = new FileReader();
    reader.onload = (e)=>{
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, {type:'array'});
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const json = XLSX.utils.sheet_to_json(sheet, {header:1, defval:""});

        previewRows = [];
        const tbody = qs('#previewTable tbody');
        tbody.innerHTML = "";

        json.forEach((r,i)=>{
            if(i === 0) return;
            if(!r || r.length < 2) return;

            const nis = (r[0] || "").toString().trim();
            const nama = (r[1] || "").toString().trim();
            const kelas = (r[2] || "").toString().trim();

            if(!nis || !nama) return;

            previewRows.push([nis, nama, kelas]);

            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${nis}</td><td>${nama}</td><td>${kelas}</td>`;
            tbody.appendChild(tr);
        });

        if(previewRows.length === 0) return showToast("Tidak ada baris valid.");

        qs('#previewWrap').style.display = "block";
        showToast("Preview siap. Tekan Upload ke Server");
    };
    reader.readAsArrayBuffer(file);
});

qs('#btnUploadExcel').addEventListener('click', async ()=>{
    if(previewRows.length === 0) return showToast("Belum ada data preview.");

    const res = await fetch(`${API_BASE}/admin/upload_students`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({students: previewRows})
    });

    const j = await res.json();
    if(res.ok){
        showToast(`Sukses: ${j.inserted} siswa ditambahkan`);
        qs('#previewWrap').style.display = "none";
        previewRows = [];
    } else {
        showToast("Error: " + j.message);
    }
});

// DATA VOTERS
let voterPage = 1;
let voterSearch = "";

async function loadVoters(){
    const res = await fetch(`${API_BASE}/admin/voters?page=${voterPage}&search=${encodeURIComponent(voterSearch)}`);
    const data = await res.json();

    const tbody = qs("#tableVoters tbody");
    tbody.innerHTML = "";

    data.items.forEach(v=>{
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${v.nis}</td>
            <td>${v.name}</td>
            <td>${v.class_name || "-"}</td>
            <td>${v.has_voted ? "✔" : "✘"}</td>
        `;
        tbody.appendChild(tr);
    });

    qs("#pageInfo").innerText = `Halaman ${data.page} / ${data.total_pages}`;
}

qs("#btnSearchVoter").addEventListener('click', ()=>{
    voterSearch = qs("#searchVoter").value.trim();
    voterPage = 1;
    loadVoters();
});

qs("#prevVoter").addEventListener('click', ()=>{
    if(voterPage > 1){
        voterPage--;
        loadVoters();
    }
});

qs("#nextVoter").addEventListener('click', ()=>{
    voterPage++;
    loadVoters();
});

// KANDIDAT
let selectedCandidateID = null;

async function loadCandidates(){
    const res = await fetch(`${API_BASE}/admin/candidates`);
    const data = await res.json();
    const tbody = qs('#tableCandidates tbody');
    tbody.innerHTML = "";

    data.forEach(c=>{
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${c.nomor}</td>
            <td>${c.ketua}</td>
            <td>${c.wakil}</td>
            <td>
                <button onclick="selectCandidate(${c.id})">Edit</button>
                <button onclick="deleteCandidate(${c.id})">Hapus</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

window.selectCandidate = async (id)=>{
    selectedCandidateID = id;
    const res = await fetch(`${API_BASE}/admin/candidates`);
    const data = await res.json();
    const c = data.find(x=>x.id === id);

    if(!c) return;

    qs('#k_nomor').value = c.nomor;
    qs('#k_ketua').value = c.ketua;
    qs('#k_wakil').value = c.wakil;
    qs('#k_visi').value = c.visi;
    qs('#k_misi').value = c.misi;

    if(c.photo){
        qs('#previewFoto').src = `${API_BASE}/candidate_photo/${c.photo}`;
        qs('#previewFoto').style.display = "block";
    } else {
        qs('#previewFoto').style.display = "none";
    }

    qsa('.nav-btn').forEach(b=>b.classList.remove('active'));
    document.querySelector('[data-target="tab-kandidat"]').classList.add('active');
    qsa('.tab').forEach(t=>t.classList.remove('active'));
    qs('#tab-kandidat').classList.add('active');
};

qs('#k_foto').addEventListener('change', e=>{
    const f = e.target.files[0];
    if(f){
        qs('#previewFoto').src = URL.createObjectURL(f);
        qs('#previewFoto').style.display = "block";
    }
});

qs('#btnAddCandidate').addEventListener('click', async ()=>{
    const fd = new FormData();
    fd.append("nomor", qs('#k_nomor').value);
    fd.append("ketua", qs('#k_ketua').value);
    fd.append("wakil", qs('#k_wakil').value);
    fd.append("visi", qs('#k_visi').value);
    fd.append("misi", qs('#k_misi').value);
    if(qs('#k_foto').files[0]) fd.append("photo", qs('#k_foto').files[0]);

    const res = await fetch(`${API_BASE}/admin/add_candidate`, {method:'POST', body:fd});
    const j = await res.json();
    showToast(j.status === "ok" ? "Kandidat ditambahkan" : (j.message || "Gagal"));
    loadCandidates();
});

qs('#btnUpdateCandidate').addEventListener('click', async ()=>{
    if(!selectedCandidateID) return showToast("Pilih kandidat dulu!");

    const fd = new FormData();
    fd.append("nomor", qs('#k_nomor').value);
    fd.append("ketua", qs('#k_ketua').value);
    fd.append("wakil", qs('#k_wakil').value);
    fd.append("visi", qs('#k_visi').value);
    fd.append("misi", qs('#k_misi').value);
    if(qs('#k_foto').files[0]) fd.append("photo", qs('#k_foto').files[0]);

    const res = await fetch(`${API_BASE}/admin/update_candidate/${selectedCandidateID}`, {method:'POST', body:fd});
    const j = await res.json();
    showToast(j.status === "ok" ? "Kandidat diperbarui" : (j.message || "Gagal update"));
    loadCandidates();
});

window.deleteCandidate = async (id)=>{
    if(!confirm("Hapus kandidat?")) return;

    const res = await fetch(`${API_BASE}/admin/delete_candidate/${id}`, {
        method: "DELETE"
    });
    const j = await res.json();

    showToast("Kandidat dihapus");
    loadCandidates();
};

// Statistik (chart)
let chartVote = null;
async function loadStatistik(){
    const res = await fetch(`${API_BASE}/admin/stats`);
    const data = await res.json();

    const labels = data.map(x=>`Paslon ${x.nomor}`);
    const values = data.map(x=>x.votes);

    const ctx = qs('#chartVote');

    if(chartVote) chartVote.destroy();

    chartVote = new Chart(ctx, {
        type:'bar',
        data:{
            labels: labels,
            datasets:[{
                label:"Jumlah Suara",
                data: values
            }]
        }
    });
}

// REPORT & RESET
qs('#btnGeneratePDF').addEventListener('click', async ()=>{
    const res = await fetch(`${API_BASE}/admin/generate_report`);
    const j = await res.json();

    if(j.file){
        window.open(j.file, "_blank");
    } else {
        showToast("Gagal generate PDF");
    }
});

qs('#btnResetVoting').addEventListener('click', async ()=>{
    if(!confirm("Reset semua voting?")) return;

    const res = await fetch(`${API_BASE}/admin/reset_votes`, {method:"POST"});
    const j = await res.json();
    showToast(j.status === "ok" ? "Voting direset" : ("Error: "+(j.message||"")));
});

// RESET PESERTA
qs('#btnResetVoters').addEventListener('click', async ()=>{
    if(!confirm("Hapus SEMUA peserta?")) return;

    const res = await fetch(`${API_BASE}/admin/reset_voters`, {
        method: "POST"
    });

    const j = await res.json();
    showToast(j.message || "Semua peserta dihapus");
});

// tambahan: clear candidate form
qs('#btnClearCandidate').addEventListener('click', ()=>{
    selectedCandidateID = null;
    qs('#candidateForm').reset();
    qs('#previewFoto').style.display = "none";
});

// refresh candidate list
qs('#btnRefreshC').addEventListener('click', ()=>{
    loadCandidates();
});

// inisialisasi awal
document.addEventListener('DOMContentLoaded', ()=>{
    if(document.querySelector('.nav-btn.active')) {
        const target = document.querySelector('.nav-btn.active').dataset.target;
        if(target === "tab-voters") loadVoters();
        if(target === "tab-kandidat") loadCandidates();
        if(target === "tab-statistik") loadStatistik();
    }
});
