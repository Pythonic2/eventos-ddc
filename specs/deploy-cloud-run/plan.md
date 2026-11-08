# Plano — Deploy Cloud Run

1. Adaptar settings para PostgreSQL/Neon, WhiteNoise, GCS e proxy HTTPS preservando SQLite local.
2. Criar backend GCS, comando idempotente de sincronização e testes de configuração/caminhos.
3. Adicionar Dockerfile, Compose, entrypoint, health check e exclusões de build/Git.
4. Criar scripts separados para migrations, upload de mídias e deploy Cloud Run.
5. Validar testes, produção, build e execução local do container.
6. Fazer revisão de segurança e prontidão GO/NO-GO.
7. Em GO, inicializar o Git isolado, criar/enviar `eventos-ddc`, aplicar migration, configurar IAM, enviar mídias e publicar Cloud Run.
8. Verificar URL, configuração de escala, storage e registrar evidências em `DEPLOY.md`.
