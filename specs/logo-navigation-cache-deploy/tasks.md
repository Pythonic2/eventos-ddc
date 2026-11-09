# Tarefas — Logo, navegação, cache e deploy

- [x] T01 — Integrar `logo2.png` ao static files.
- [x] T02 — Atualizar home e `/eventos/`.
- [x] T03 — Corrigir restauração da home após voltar.
- [x] T04 — Ajustar cache e lazy loading.
- [x] T05 — Implementar e executar testes.
- [x] T06 — Revisar diff, segurança e prontidão.
- [ ] T07 — Fazer deploy e validar Raspberry e Cloud Run.

## Evidências locais

- 42 testes Django passaram com SQLite isolado.
- `check` e `makemigrations --check --dry-run` passaram.
- `collectstatic` incluiu `brand/logo2.png`: 139 arquivos copiados e 393 pós-processados.
- Build Docker `eventos-ddc:codex-verify` passou.
- Sem migrations novas; cache GCS permanece privado e o static usa nomes versionados.
