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

# Padrão de Infraestrutura — Gest Tech

## Arquitetura

Todo projeto Django preparado para produção deve suportar dois ambientes:

- **Principal:** Raspberry Pi, Docker e Portainer.
- **Backup:** Google Cloud Run, região `southamerica-east1`.
- **Banco:** Neon PostgreSQL, compartilhado entre as instâncias.
- **Mídias:** Google Cloud Storage, bucket `gesttechmidias`.
- **DNS e HTTPS:** Cloudflare.
- **Failover:** Cloudflare Worker.

## 1. Google Cloud Storage

Utilizar o mesmo bucket nas duas infraestruturas, isolando as mídias por projeto.

Estrutura:

`gs://gesttechmidias/<nome-projeto>/midias/`

Configuração por variáveis de ambiente:

```env
GCS_ENABLED=true
GCS_BUCKET_NAME=gesttechmidias
GCS_PROJECT_ID=gestcloud-500200
GCS_APP_PREFIX=<nome-projeto>
GCS_IAM_SIGN_BLOB=true
GCS_SA_EMAIL=926822874156-compute@developer.gserviceaccount.com
```

No Cloud Run, utilizar Application Default Credentials da conta de serviço associada ao serviço.

No Raspberry, utilizar uma credencial montada no container:

```env
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp.json
```

Docker Compose:

```yaml
volumes:
  - /home/pi/gcp-secrets/eventos-ddc.json:/run/secrets/gcp.json:ro
```

Esse arquivo é reutilizável entre projetos autorizados, mas o acesso ao container deve ser restrito. Nunca incluir a chave JSON no repositório ou na imagem Docker.

O Secret Manager deve manter a cópia de recuperação da credencial. Sua recuperação exige autenticação prévia autorizada; não presumir download automático apenas pela presença de `GCP_SECRET_NAME`.

Não usar armazenamento local como fonte principal das mídias compartilhadas.

## 2. Docker e Raspberry

Os containers publicados pelo Cloudflare Tunnel devem participar da rede externa:

```yaml
networks:
  pi_default:
    external: true
```

Usar nomes de serviço Docker para comunicação interna.

Exemplo:

`http://eventos-ddc:8080`

Não utilizar a porta publicada no host para a comunicação entre containers.

O Django deve aceitar configuração independente de HTTPS:

```env
DJANGO_SECURE_SSL_REDIRECT=false
```

O HTTP é utilizado internamente no Raspberry. O HTTPS público é fornecido pela Cloudflare.

## 3. Failover pelo Cloudflare

Para cada projeto, configurar:

1. Um hostname público que acessa o Worker.
2. Um subdomínio de origem reservado, apontando diretamente ao Raspberry via Tunnel.
3. Uma URL de backup no Cloud Run.
4. Um Worker que encaminha requisições ao Raspberry e utiliza o Cloud Run quando ocorrer timeout ou falha configurada.

Exemplo:

- Público: `donadochopp.com.br`
- Origem Raspberry: `eventos-worker.donadochopp.com.br`
- Tunnel: `http://eventos-ddc:8080`
- Backup: URL correspondente do Cloud Run.

Associar ao Worker a rota:

`donadochopp.com.br/*`

Não associar a rota do Worker ao subdomínio de origem, para evitar loops.

Para requisições GET e HEAD, permitir fallback em caso de timeout ou respostas 502, 503 e 504.

Para POST, PUT, PATCH e DELETE, não repetir automaticamente operações em outra instância, evitando duplicações de pedidos ou pagamentos.

O Worker deve adicionar o cabeçalho:

`X-Failover-Origin: raspberry`

ou

`X-Failover-Origin: cloud-run`

Confirmar que URLs de redirecionamento e hostnames recebidos pelo Django são tratados corretamente.

## 4. Banco de dados

Utilizar o mesmo banco Neon nos dois ambientes, mantendo isolamento lógico por projeto quando aplicável.

Evitar execução simultânea de migrations pelos dois ambientes.

Não depender de SQLite ou volumes locais para dados que precisam permanecer disponíveis durante failover.

## 5. Validação obrigatória

Antes de considerar o deploy concluído:

- Verificar `/healthz/`.
- Verificar autenticação Google no Raspberry.
- Testar geração de URLs assinadas do GCS.
- Confirmar que as imagens aparecem no Raspberry e no Cloud Run.
- Testar acesso direto ao subdomínio de origem.
- Confirmar `X-Failover-Origin: raspberry` no domínio público.
- Simular indisponibilidade do Raspberry e confirmar `X-Failover-Origin: cloud-run`.
- Restaurar o Raspberry e confirmar retorno à origem principal.

Nunca declarar o failover funcional sem executar os testes correspondentes.

## 6. Segurança

- Nunca armazenar credenciais em GitHub.
- Restringir permissões das contas de serviço ao necessário.
- Preferir identidades específicas e de privilégio mínimo quando possível.
- Proteger as credenciais montadas no Raspberry.
- Manter processo documentado de recuperação em um novo servidor.
- Proteger endpoints administrativos e operações sensíveis.
- Não alterar configurações de produção sem verificar impacto nos outros projetos.

## Objetivo

Permitir que qualquer projeto Gest Tech seja executado no Raspberry e no Cloud Run, compartilhando banco e mídias, com failover automático pela Cloudflare e recuperação em caso de perda do hardware.
