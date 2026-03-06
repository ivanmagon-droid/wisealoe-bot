# Session Log — WiseAloe Bot

## 2026-03-06 — Sessione 1

### Completato
1. **GitHub Actions posting** — funzionante, post_01 pubblicato su @wisealoe
   - Fix: aggiunto polling container status (wait_for_container_ready)
   - Fix: permissions `contents: write` nel workflow yml
   - Fix: post_log.json per tracciare tentativi e prevenire duplicati
   - Fix: already_published() check prima di ogni pubblicazione

2. **Queue 30 post** — creati post 1-30 (5 mar - 3 mag 2026)
   - Post_01: pubblicato (posted: true)
   - Post_02: data cambiata a 06/03 per test, workflow OK
   - Post 03-30: schedulati ogni 2 giorni
   - Brief visivo Canva: content/BRIEF_VISIVO_POST.md

3. **Immagini** — caricate post_01-10 nel repo
   - post_01-03: .png, post_04-10: .jpg
   - Mancano: post_11-30 (utente le crea su Canva)

4. **Sicurezza repo GitHub**
   - Rimossi ID hardcoded da n8n_instagram_workflow.json (sostituiti con placeholder)
   - Scan completo: nessun token/password esposto
   - Repo pubblico necessario per image hosting (raw.githubusercontent.com)

5. **n8n Webhook Meta** — verificato e funzionante
   - Workflow "Meta Webhook Verify" (ID: QHockUq7MbYtOcWq) — attivo, risponde al challenge
   - Risolto bug n8n: errore "Unused Respond to Webhook" causato da 2 webhook nello stesso workflow
   - Fix: separato in 2 workflow, usato responseMode: "responseNode"
   - Campi sottoscritti: comments, messages, live_comments, message_edit, message_reactions

6. **n8n DM Automation** — funzionante
   - Workflow "FLP_Instagram_DM_Automation" (ID: RadsvgMcOKuGnloB) — attivo
   - Rimossi nodi GET/Respond (causa errore)
   - Inserito token System User reale nel nodo "Invia DM Instagram"
   - Inserito chat_id Telegram reale (8285408458)
   - Fix: DM e Telegram ora in parallelo (se DM fallisce, Telegram arriva comunque)
   - Test: notifica Telegram ricevuta con successo

### Errori risolti e da non ripetere
| Errore | Causa | Fix | NON fare |
|--------|-------|-----|----------|
| Error 500 transient Meta | Connessione Page↔IG appena creata | Aspettare 5-10 min propagazione | Non ritentare subito |
| Error 9007 "Media not available" | Container non pronto per publish | Aggiunto wait_for_container_ready() polling | Non pubblicare senza polling |
| 403 push GitHub Actions | Bot non ha write permissions | permissions: contents: write in yml | Non dimenticare permissions |
| Vecchio script in Actions | Workflow triggato prima del push | Verificare commit HEAD prima di triggerare | Non triggerare subito dopo push |
| Post duplicato dopo push fallito | queue.json non aggiornato nel repo | post_log.json + already_published() check | Non ignorare push falliti |
| "Unused Respond to Webhook" n8n | 2 webhook trigger nello stesso workflow | Separare in 2 workflow distinti | Mai 2 webhook trigger in 1 workflow |
| DM fallisce → Telegram non parte | Nodi in serie, errore blocca catena | Messo in parallelo da "Parola chiave" | Mai mettere Telegram dopo DM in serie |
| Canva token invalido in Claude Code | MCP Canva connesso su claude.ai web, non CLI | Utente crea immagini manualmente su Canva | Non provare Canva MCP da CLI |

### Da completare (prossima sessione)
- [ ] Creare immagini post_11-30 su Canva e caricarle nel repo
- [ ] Pubblicare app Meta (serve Privacy Policy URL)
- [ ] Testare DM reale con commento su post Instagram
- [ ] Setup Meta Ads lookalike con lista 100 clienti
- [ ] Supporto caroselli (aggiornare script per multi-immagine)

### File modificati in questa sessione
- `.github/workflows/post_instagram.yml` — permissions + post_log.json nel commit
- `scripts/post_to_instagram.py` — polling, log tentativi, check duplicati
- `content/queue.json` — 30 post, post_01 marcato pubblicato
- `content/post_log.json` — NUOVO, log tentativi pubblicazione
- `content/BRIEF_VISIVO_POST.md` — NUOVO, brief visivo per Canva
- `content/n8n_webhook_verify.json` — NUOVO, workflow verifica Meta
- `content/n8n_instagram_workflow.json` — placeholder al posto di ID reali

### Credenziali usate (NON salvare token qui)
- n8n API key: salvata in sessione, scade 2026-05-02
- System User token: inserito direttamente in n8n (nodo "Invia DM Instagram")
- GitHub Secrets: INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID (invariati)
