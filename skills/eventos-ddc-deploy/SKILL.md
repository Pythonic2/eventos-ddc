---
name: eventos-ddc-deploy
description: Publicar e validar o projeto eventos-ddc no GitHub, Google Cloud Storage, Docker/Raspberry e Cloud Run, incluindo migrations Neon e automação da main. Use quando o usuário pedir deploy, atualização de produção, sincronização de mídias ou verificação dessa infraestrutura.
---

# Deploy do eventos-ddc

Trabalhe no repositório `/home/igorm/dona-do-chopp-cinematico-automatico` salvo indicação diferente. Leia `AGENTS.md`, `DEPLOY.md`, `specs/deploy-cloud-run/` e o diff antes de agir. Preserve mudanças do usuário, especialmente `docker-compose.yml`, `stack.env`, `.env`, credenciais montadas e regras de failover.

## Invariantes

- Cloud Run: projeto `gestcloud-500200`, serviço `eventos-ddc`, região `southamerica-east1`, `min=0`, `max=1`, `concurrency=1`.
- Banco: Neon no schema exclusivo `eventosddc`; nunca usar `public` como fallback nem executar migrations simultaneamente em duas instâncias.
- Mídias: bucket privado `gesttechmidias`, prefixo `eventos-ddc/midias/`; nunca tornar público, sobrescrever em lote ou versionar chave JSON.
- GitHub: `Pythonic2/eventos-ddc`, branch `main`; `.env`, `stack.env`, banco, mídia e credenciais não entram no commit.
- Raspberry: container e serviço `eventos-ddc`, rede externa `pi_default`, credencial somente leitura montada fora do repositório.
- O número de concorrência não é número de instâncias; mesmo assim ambos ficam em 1 neste projeto.

## Fluxo

1. Confirme que o pedido atual autoriza as mutações externas pretendidas. A invocação da skill demonstra intenção de deploy, mas não autoriza apagar schemas, alterar DNS/Cloudflare, substituir credenciais ou executar outra ação destrutiva não mencionada.
2. Verifique autenticação (`gh auth status`, conta/projeto gcloud), branch, remoto, worktree, arquivos ignorados e configuração ativa do Cloud Run. Não imprima valores de ambiente.
3. Rode testes Django com ambiente local explícito, `check`, migrations pendentes, sintaxe dos scripts, `docker compose config` quando o `stack.env` do ambiente estiver presente e build proporcional à mudança.
4. Se houver migrations novas, aplique uma única vez com `./migrate-production.sh` e confirme `current_schema() = eventosddc`. Não marque migrations manualmente nem inclua `public` no `search_path`.
5. Para mídias, planeje com `./upload-media-gcs.sh`; execute somente quando solicitado e confirme objetos no prefixo sem expor URLs assinadas ou credenciais.
6. Revise o staged diff contra vazamentos, faça commit objetivo e push para `main`. O trigger `eventos-ddc-main` deve construir `cloudbuild.yaml` e atualizar o Cloud Run; não faça um segundo deploy manual concorrente quando o trigger estiver saudável.
7. Se o trigger não existir ou estiver quebrado, diagnostique antes de usar `./deploy-cloud-run.sh` como fallback. Preserve as variáveis já configuradas no serviço.
8. Aguarde estado terminal e valide `/`, `/eventos/`, `/healthz/`, um asset e `/admin/login/`. Confirme revisão pronta, 100% do tráfego, min/max/concurrency e logs sem erro crítico.
9. No Raspberry, valide o Compose somente no host que possui `stack.env`, `/home/pi/gcp-secrets/eventos-ddc.json` e `pi_default`. Nunca fabrique esses arquivos a partir de dados exibidos em logs.

## Paradas obrigatórias

Pare e informe evidências se houver mudança externa sobreposta, segredo fraco/ausente, autenticação inválida, schema diferente, build/teste falhando após três reparos fundamentados, trigger duplicado ou necessidade de ação destrutiva. Não declare deploy concluído sem verificar a URL e a escala reais.

## Entrega

Informe commit, URL/revisão, estado do trigger, escala `0–1`, quantidade de mídias sincronizadas, migrations executadas, testes reais, pendências do Raspberry/Cloudflare e rollback aplicável. Não reproduza segredos.
