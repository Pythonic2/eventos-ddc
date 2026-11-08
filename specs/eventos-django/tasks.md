# Tarefas — Página de eventos administrável em Django

- [x] T01 — Mapear contratos, assets e ambiente atual (AC-01)
- [x] T02 — Definir modelagem, limites e estratégia de segurança (AC-02–AC-06)
- [x] T03 — Criar projeto/app Django e configuração local (AC-01)
- [x] T04 — Implementar models, validadores e migration (AC-02–AC-06)
- [x] T05 — Configurar Admin em português e permissões (AC-05, AC-07)
- [x] T06 — Converter a página cinematográfica e integrar rotas (AC-01–AC-04)
- [x] T07 — Implementar e executar testes (AC-01–AC-07)
- [x] T08 — Revisar segurança, diff, compatibilidade e evidências (AC-01–AC-07)

## Evidências
| Tarefa | Comando/verificação | Resultado |
|---|---|---|
| T01 | inspeção de arquivos, Python e dependências | Python 3.12; Django ausente; HTML estático preservado |
| T03 | `python manage.py check` e servidor local | PASSOU; `/eventos/` 200 e login do `/admin/` 200 após redirect |
| T04 | `python manage.py makemigrations --check --dry-run` | PASSOU; nenhuma mudança pendente |
| T07 | `uv run python manage.py test` | PASSOU; 19 testes |
| T08 | `DJANGO_DEBUG=false ... python manage.py check --deploy` | PASSOU com perfil temporário completo de HTTPS/HSTS |
| T08 | `git diff --check` | PASSOU |
| Ajuste editorial | `uv sync` e `uv run ... test` | `uv.lock` gerado; suite validada pelo uv |

## Expansão editorial completa
- [x] T09 — Ampliar campos e tipos estruturados de seção (AC-08)
- [x] T10 — Disponibilizar itens com foto/vídeo em todas as seções (AC-09)
- [x] T11 — Integrar todas as seções ao template com fallbacks (AC-08, AC-09)
- [x] T12 — Testar Admin, renderização, uploads e regressões (AC-08, AC-09)

| Tarefa | Comando/verificação | Resultado |
|---|---|---|
| T09–T11 | migrations `0005` a `0008` + inspeção do Admin/template | PASSOU; oito seções estruturadas e conteúdo inicial preservado |
| T12 | `UV_CACHE_DIR=.uv-cache uv run --no-sync python manage.py test` | PASSOU; 19 testes |
| T12 | `manage.py check`, `makemigrations --check --dry-run` e `git diff --check` | PASSOU |
