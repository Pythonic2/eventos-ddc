# Deploy do eventos-ddc

O projeto usa o PostgreSQL/Neon e o schema definidos no `.env`, mantendo as tabelas isoladas exclusivamente pelo `DB_SCHEMA` (sem fallback para `public`). O frontend continua com os assets versionados na imagem e uploads do Admin usam o bucket privado sob:

```text
gs://gesttechmidias/eventos-ddc/midias/
```

O `.env` não entra no Git nem na imagem Docker. Os scripts leem esse arquivo localmente e nunca imprimem os valores secretos.

## Pré-requisitos

- Docker com Compose para o servidor próprio.
- `uv` para comandos locais.
- Google Cloud CLI autenticada para Cloud Run/GCS.
- Permissão no projeto definido por `GCS_PROJECT_ID`.
- `.env` preenchido com PostgreSQL, GCS, hosts, `SECRET_KEY` e conta de serviço.

## Validação rápida

```bash
uv sync --frozen
uv run --no-sync python manage.py test
uv run --no-sync python manage.py check
docker compose config --quiet
docker compose build
```

## Servidor com Docker Compose

O serviço e o container chamam-se `eventos-ddc` e a porta padrão do host é `8011`:

```bash
./migrate-production.sh
docker compose up -d --build
docker compose ps
```

Verificação:

```bash
curl --fail http://127.0.0.1:8011/healthz/
```

## Migrations no Neon

Este comando cria somente o schema configurado em `DB_SCHEMA` e aplica as migrations nele:

```bash
chmod +x migrate-production.sh
./migrate-production.sh
```

O serviço web não executa migrations automaticamente. Faça backup e valide o schema antes de reverter migrations.

## Imagens e uploads no GCS

Primeiro veja o plano, sem alterar o bucket:

```bash
chmod +x upload-media-gcs.sh
./upload-media-gcs.sh
```

Depois envie somente objetos ausentes, sem sobrescrever ou excluir:

```bash
./upload-media-gcs.sh --execute
```

As imagens atuais ficam em `eventos-ddc/midias/imagens-iniciais/`; uploads locais preexistentes ficam em `eventos-ddc/midias/uploads/`. Novos uploads do Admin são gravados diretamente em `eventos-ddc/midias/`.

## Cloud Run

O padrão é serviço `eventos-ddc`, região `southamerica-east1`, mínimo zero e máximo uma instância:

```bash
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh
```

Para alterar serviço ou região explicitamente:

```bash
SERVICE=eventos-ddc REGION=southamerica-east1 ./deploy-cloud-run.sh
```

Depois do deploy:

```bash
gcloud run services describe eventos-ddc --region southamerica-east1
```

## IAM do bucket privado

A conta configurada em `GCS_SA_EMAIL` precisa de `roles/storage.objectUser` no bucket `gesttechmidias`. Para gerar URLs assinadas sem chave JSON, ela também precisa de `roles/iam.serviceAccountTokenCreator` sobre a própria conta. O bucket não deve ser público.

## Repetir todo o fluxo

Em uma nova versão, normalmente basta:

```bash
uv run --no-sync python manage.py test && \
./migrate-production.sh && \
./upload-media-gcs.sh --execute && \
./deploy-cloud-run.sh
```

O GitHub é atualizado separadamente com `git push`; não coloque `.env`, chave JSON ou dumps no commit.

## Rollback

- Cloud Run: direcione 100% do tráfego para a revisão saudável anterior.
- Docker Compose: volte para a imagem/commit anterior e execute `docker compose up -d --build`.
- Banco: não reverta automaticamente. Avalie `showmigrations` e o impacto da migration no schema configurado.
