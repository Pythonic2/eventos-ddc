# WEB-001 — Logo, retorno da transição, desempenho e deploy

## Objetivo
Usar `static/logo2.png` como marca na home e em `/eventos/`, permitir retornar às escolhas sem a sobreposição de transição persistir e reduzir transferências desnecessárias de imagens e vídeos antes do deploy no Raspberry e no Cloud Run.

## Cenários e critérios de aceitação
- AC-01: a home e `/eventos/` exibem a mesma `logo2.png`, com texto alternativo e link para `/`.
- AC-02: ao voltar do destino pelo navegador, a home remove imediatamente a transição e volta a aceitar escolhas.
- AC-03: assets locais são servidos pelo pipeline versionado do WhiteNoise, com cache imutável em produção.
- AC-04: mídias privadas do GCS mantêm URL assinada e cache privado moderado, sem tornar o bucket público.
- AC-05: vídeos fora do hero não transferem conteúdo antes da ação do visitante.
- AC-06: testes Django, `check`, migrations pendentes, coleta de estáticos e build/Compose passam antes da publicação.
- AC-07: Raspberry e Cloud Run respondem em `/`, `/eventos/`, `/healthz/`, asset da logo e `/admin/login/` após o deploy.

## Segurança e compatibilidade
- Nenhuma mudança de autenticação, banco, schema, DNS ou permissões do bucket.
- Não cachear respostas do Admin nem tornar mídias públicas.
- O rollback é retornar os dois ambientes ao commit anterior; não há migration de banco.
