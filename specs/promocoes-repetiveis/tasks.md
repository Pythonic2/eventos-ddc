# Tarefas — Promoções repetíveis

- [x] T01 — Mapear contratos, Admin, view, template e deploy (AC-01–AC-07)
- [x] T02 — Implementar schema, Admin e frontend (AC-01–AC-06)
- [x] T03 — Executar testes focalizados e regressão Django (AC-01–AC-06)
- [x] T04 — Revisar segurança, diff, migration e compatibilidade (AC-03/AC-07)
- [x] T05 — Aplicar migration autorizada, fazer push e validar Cloud Run (AC-07)
- [x] T06 — Corrigir CTA promocional e validar divergência Raspberry/Cloud Run (AC-08/AC-09)
- [x] T07 — Reorganizar layout promocional responsivo e eliminar cards vazios (AC-10)

## Evidências
| Tarefa | Comando/verificação | Resultado |
|---|---|---|
| T03 | `manage.py test`, `check`, `makemigrations --check`, migration SQLite | 39 testes e verificações passaram |
| T04 | `git diff --check`, revisão de autenticação/validação/uploads, Docker build | passou; Compose indisponível sem `stack.env` do Raspberry |
| T05 | migration Neon, Cloud Build e revisão Cloud Run `00019` | passou |
| T06 | comparação das origens + 40 testes Django | correção passou; publicação validada no relatório operacional |
| T07 | testes focalizados + regressão de 40 testes | passou; publicação validada no relatório operacional |
