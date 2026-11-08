# DEP-001 — Deploy do site de eventos

## Objetivo
Publicar o site Django de eventos em um repositório GitHub próprio e no Google Cloud Run, usando PostgreSQL Neon com schema isolado e Google Cloud Storage privado para mídias.

## Escopo
- Docker/Compose local com serviço e container `eventos-ddc`.
- Cloud Run em `southamerica-east1`, serviço `eventos-ddc`, mínimo 0 e máximo 1 instância.
- PostgreSQL configurado exclusivamente por ambiente e limitado ao `DB_SCHEMA` fornecido.
- Mídias privadas em `gs://gesttechmidias/eventos-ddc/midias/` usando ADC e URLs assinadas.
- Migração explícita e separada do processo web.
- Upload inicial das imagens do projeto, repositório GitHub `eventos-ddc` e documentação operacional.

## Fora de escopo
- Alterar DNS ou domínio personalizado.
- Tornar o bucket público.
- Copiar integrações comerciais/Mercado Pago do projeto de referência.
- Executar migrations automaticamente em cada inicialização do Cloud Run.

## Regras
- DEP-R01: `.env`, credenciais, banco local, mídias e temporários nunca entram na imagem nem no Git.
- DEP-R02: produção exige `SECRET_KEY`, dados PostgreSQL, hosts confiáveis e HTTPS via proxy do Cloud Run.
- DEP-R03: `search_path` deve usar identificador de schema validado e parametrizado; o script cria somente o schema informado.
- DEP-R04: o serviço web inicia com Gunicorn e não executa migrations por padrão.
- DEP-R05: o GCS usa prefixo fixo `eventos-ddc/midias`, bucket privado, sem chave JSON no repositório.
- DEP-R06: uploads iniciais não sobrescrevem nem excluem objetos existentes.
- DEP-R07: Cloud Run limita escala a 0–1 instância e usa região `southamerica-east1`.
- DEP-R08: o Docker Compose expõe a aplicação local e usa o nome `eventos-ddc`.

## Critérios de aceitação
- AC-01: imagem Docker constrói e o health check responde com sucesso.
- AC-02: testes Django e `check --deploy` passam com configuração de produção controlada.
- AC-03: migrations são aplicadas no schema Neon configurado sem afetar outros schemas.
- AC-04: imagens atuais são copiadas para `gs://gesttechmidias/eventos-ddc/midias/` sem sobrescrita.
- AC-05: serviço Cloud Run público fica ativo com min 0, max 1 e revisão saudável.
- AC-06: repositório GitHub `eventos-ddc` contém somente arquivos permitidos e o branch principal é enviado.
- AC-07: `DEPLOY.md` e scripts permitem repetir migração, upload e deploy sem redigitar comandos extensos.

## Segurança e recuperação
- Segredos serão lidos localmente e passados por arquivo temporário com permissão restrita, removido por `trap`.
- O bucket permanece privado; a conta do Cloud Run precisa apenas das permissões necessárias no bucket e para assinar URLs.
- Rollback do app: direcionar tráfego para revisão anterior. Rollback de banco: migrations deste projeto são aditivas; qualquer reversão será manual e previamente avaliada.
- Nenhum valor secreto será mostrado em logs, documentação ou commits.

## Autorização
O usuário autorizou explicitamente criação do repositório, alterações IAM necessárias, migrations no schema informado, upload das mídias e deploy em produção nesta solicitação.
