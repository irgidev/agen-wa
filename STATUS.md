# STATUS — agen-wa (P2)

Dokumen state internal proyek P2. Append-only untuk changelog; semua sub-sesi wajib membaca file ini dan menulis changelog di bagian bawah.

## State milestone

| Milestone | Status | Keterangan |
|---|---|---|
| M0 skeleton | selesai (lokal hijau; CI diverifikasi setelah push) | repo, CI, README + panduan Setup Meta, docker-compose 3 service |
| M1 mock+tools+suite v1 | didelegasikan ke JALUR-A | lihat `prompts/SUB-A-mock-tools.md` |
| M2 loop WhatsApp nyata | diblokir user | user menjalankan README "Setup Part A" (Meta dev account + test number), lalu JALUR-B |
| M3 governance+console+eval | didelegasikan ke JALUR-C | lihat `prompts/SUB-C-governance-console-eval.md` |
| M4 rilis v0.1.0 | sesi induk | setelah A+B+C terintegrasi |

## Pembagian jalur (setelah M0, sesuai bagian 7 PROMPT-INTI)

| Jalur | Owns (hanya ini) | Sub-prompt |
|---|---|---|
| A — mock + tools | `src/mock_service/`, `scenarios/`, `tests/mock_service/` | `prompts/SUB-A-mock-tools.md` |
| B — agent core + webhook | `src/agent/nlu_tools/`, `src/agent/session/`, `src/webhook/`, `tests/agent/`, `tests/webhook/`, `tests/fixtures/` | `prompts/SUB-B-agent-webhook.md` |
| C — governance + console + eval | `src/agent/governance/`, `src/harness/`, `operator_console/`, `tests/governance/`, `tests/harness/`, `reports/` | `prompts/SUB-C-governance-console-eval.md` |

Shared files (dimiliki sesi induk; sub-sesi TIDAK boleh mengubah): `README.md`, `STATUS.md` (kecuali append changelog), `pyproject.toml`, `requirements.txt`, `.github/`, `docker-compose.yml`, `docker/`, `LICENSE`, `.gitignore`, `.env.example`, `tests/test_smoke.py`, `tests/conftest.py`. Permintaan perubahan → tulis baris `DEP-REQUEST:` / `INT-REQUEST:` di changelog bawah file ini.

`prompts/` (sub-prompt) di-gitignore agar repo publik bersih; keputusan tercatat di changelog 2026-11-15.

## Keputusan lokal (D-P2-xx)

- D-P2-01: CI berjalan di Python 3.14 saja (mirror mesin dev; matrix 3.13 ditunda karena requirements di-freeze dari interpreter 3.14).
- D-P2-02: Layout import aplikasi: `agent.*`, `mock_service.*`, `webhook.*` dari `src/`, dan `operator_console.*` dari root repo (pytest `pythonpath = ["src", "."]`). Nama package generik diterima karena ini aplikasi, bukan library PyPI.
- D-P2-03: `operator_console/app.py` stub dibuat sesi induk di M0 agar docker-compose 3 service jalan sejak awal; JALUR-C mengambil alih.
- D-P2-04: `src/harness/` ditambahkan di luar daftar struktur spec; dimiliki JALUR-C, karena bagian 7 memberi C "harness skenario" tapi spec struktur tidak menentukan lokasinya.
- D-P2-05: Laporan harness di-commit ke `reports/` (butuh M1 DoD "laporan pertama committed"); folder di-track git.
- D-P2-06: Kontrak lintas jalur (lihat sub-prompt untuk detail): 5 tool dengan nama/argumen tetap; entri audit JSONL `{ts, user_wa_id, tool, args, result, decision, request_id}`; `decision` ∈ `auto_allowed | requires_approval | approved | rejected | denied`; reply class ∈ `answer | clarify | approval_pending | handoff | refusal`; antarmuka agen offline `handle_text(user_id, text) -> (reply_text, reply_class)`; mode LLM `rule-based` tanpa API key untuk determinisme test/harness.
- D-P2-07: Ambang approval `create_loan` default IDR 10.000.000 (`LOAN_APPROVAL_THRESHOLD_IDR`), boleh diganti user.
- D-P2-08: Bisnis simulasi memakai nama "Gadai Simulasi" dari spec; user boleh minta ganti nama nanti.
- D-P2-09: Biaya API: belum ada pemakaian LLM berbayar (M0 + rule-based). Catat setiap run berbayar di sini.

## Tergantung user

- Setup Meta developer account + test number + token (README "Setup Part A") — diminta ke user di laporan sesi induk, prasyarat M2.
- (Opsional, untuk run evaluasi mode LLM) API key provider LLM — pola `.env.example` sudah disiapkan; tanpa itu semua test & harness tetap jalan di mode `rule-based`.

## Changelog (append-only)

- 2026-11-15 - sesi-P2-induk: M0 selesai. Struktur dibuat, CI (ruff+pytest, Python 3.14), docker-compose 3 service dengan stub `/healthz`, README berbahasa Inggris berisi panduan Setup Meta Part A/B. Keputusan D-P2-01..09 dicatat. Sub-prompt A/B/C ditulis ke `prompts/`. Selanjutnya: push repo, verifikasi CI, lalu user disuruh menjalankan Setup Part A.
- 2026-11-15 - sesi-P2-induk: Repo publik dibuat: https://github.com/irgidev/agen-wa (commit awal `4379a9d`, lint fix `c3318a2`). **CI hijau** (ruff + pytest, Python 3.14) — DoD M0 terpenuhi. Komposisi docker-compose tervalidasi statis (`docker compose config` OK); perbaikan kecil: `env_file .env` webhook dibuat opsional (`required: false`) supaya `docker compose up` tidak gagal sebelum user membuat `.env`. Verifikasi runtime build/up tertunda karena Docker Desktop engine di mesin ini belum reachable saat sesi berjalan (CLI ada, daemon 500); user bisa verifikasi sendiri dengan `docker compose up --build` lalu curl `/healthz` di 8000/8001/8002. Interface governance `engine.py` (kontrak jalur B↔C) ditulis sesi induk dan diserahkan ke jalur C. Sub-prompt: `prompts/SUB-A-mock-tools.md`, `prompts/SUB-B-agent-webhook.md`, `prompts/SUB-C-governance-console-eval.md`. Berikutnya: user menjalankan README "Setup Part A" (Meta), lalu sub-sesi A/B/C dinyalakan.
