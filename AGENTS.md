# AGENTS.md — Projeto (personalizar)

## Contexto
- Produto: [preencher]
- Stack: [detectar do repositório]
- Domínios/regras críticas: [preencher]

## Comandos de validação (confirmar no projeto)
- Testes: [comando existente]
- Lint: [comando existente]
- Build/typecheck: [comando existente]

## Políticas do projeto
- Preservar interfaces públicas e padrões já usados.
- Qualquer alteração de API deve documentar compatibilidade e teste de contrato.
- Migrations com perda de dados exigem plano e aprovação explícita.
- Não acessar produção; não fazer deploy, push ou merge sem autorização.
- Risco alto exige `specs/<slug>/spec.md`, `plan.md` e `tasks.md`.

## Pontos a descobrir
- Onde ficam testes, autenticação, autorização, integração externa e configurações de ambientes.
