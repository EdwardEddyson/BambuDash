# 💻 Developer Guidelines

Du bist der ausführende Dev-Agent für **BambuDash**.

**Deine Dev-Regeln:**
- **NO LOCAL EXECUTION:** Führe niemals Terminal-Befehle (Docker, Uvicorn, Next.js) auf dieser Maschine aus. Das Testing findet auf einem Server statt. Du schreibst nur Code.
- **Security First:** Es ist ein lokaler `pre-commit` Hook aktiv. Wenn ein Commit fehlschlägt (z.B. wegen fest codierten Passwörtern), behebe den Code. Nutze NIEMALS `git commit --no-verify`.
- **MANDATORY ACTION:** Bevor du ein Feature abschließt und den Branch für den Merge freigibst, nutzt du zwingend die Action `grill me`, um deinen Code schonungslos auf Sicherheitslücken und Architektur-Fehler zu prüfen.
