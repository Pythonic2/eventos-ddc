# Tarefas — Deploy Cloud Run

- [x] T01 — Configuração production-ready para Neon/GCS/WhiteNoise
- [x] T02 — Dockerfile, Compose e health check
- [x] T03 — Scripts seguros de migration, mídia e Cloud Run
- [x] T04 — Testes e revisão de segurança
- [ ] T05 — Checklist de prontidão GO
- [ ] T06 — Repositório GitHub criado e enviado
- [ ] T07 — Schema/migrations e imagens no GCS
- [ ] T08 — Cloud Run publicado e verificado
- [x] T09 — Guia operacional finalizado

## Evidências

- `uv run --no-sync python manage.py test`: 22 testes passaram.
- `manage.py check` e `makemigrations --check --dry-run`: passaram.
- `docker compose config --quiet` e `docker compose build`: passaram.
- Inspeção da imagem: `.env` ausente e `staticfiles` presente.
- `check --deploy`: configuração passou com chave temporária forte; restam avisos deliberados de HSTS preload/subdomínios, que não devem ser ativados para `run.app`.
- Prontidão atual: **NO-GO**, aguardando troca autorizada da `SECRET_KEY` fraca e autenticação de API para criação do repositório GitHub.
