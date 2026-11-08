# Plano técnico — Página de eventos administrável em Django

## Estado atual e interfaces afetadas
- Aplicação composta por `index.html`, `prepage.html` e `eventos/index.html`, sem backend ou dependências Python.
- `/eventos/` será o contrato público novo; `/admin/` será a interface privada.
- A navegação estática existente para `eventos/index.html` será atualizada para `/eventos/` no template servido pelo Django, mantendo os originais.

## Solução proposta
- Componentes: projeto `config`, app `eventos`, templates Django, static/media locais e Admin.
- Dados/contratos: `EventPage` singleton para o hero; `EventSection` vinculada, tipada e com campos editoriais previsíveis; `EventMedia` como item interno com título, texto, foto/vídeo, ordem e visibilidade.
- Fluxo: view convencional lê a configuração ativa, prefetch das seções/mídias ativas, monta contexto por tipo e renderiza template com fallbacks.
- Uploads: `ImageField`/`FileField`, nomes organizados por prefixo, extensão e tamanho validados; binários fora do banco.
- Admin: item “Seções da página” com fieldsets em português e inline de itens/mídias em todas as seções; tipos estruturais e vínculos permanecem protegidos.

## Alternativas e justificativa
- Um model por seção foi rejeitado por multiplicar tabelas e Admin para uma página curta.
- JSON/page builder foi rejeitado por validação fraca e complexidade desnecessária.
- DRF/SPA foi rejeitado por contrariar o requisito e adicionar superfície operacional.
- Três models relacionais preservam estrutura, edição simples e evolução incremental.
- A alternativa de HTML livre/JSON foi mantida fora do escopo para evitar XSS, campos opacos e um page builder difícil de manter.

## Riscos e compatibilidade
- O diretório `eventos/` já contém HTML/assets: será convertido também em app sem apagar o material existente.
- Pillow é necessário para validar `ImageField`; será dependência explícita.
- SQLite e media local não representam configuração de produção.
- O `.gitignore` atual ignora tudo; será substituído por regras específicas para tornar código/migrations rastreáveis sem versionar banco, uploads ou ambiente virtual.

## Plano de teste e recuperação
- Unitários: validadores, singleton, ordenação e visibilidade.
- Integração: rotas, renderização, conteúdo dinâmico, Admin e permissões.
- Segurança: uploads/URLs inválidos, escaping do template, usuário sem permissão.
- Regressão: `check`, `makemigrations --check --dry-run`, suite Django e inicialização local (`runserver --noreload` com timeout).
- Rollback: restaurar links estáticos e remover os arquivos Django/migration; não há migração destrutiva nem dado real.

## Dependências e decisões
- Python 3.12 detectado; Django ainda ausente.
- Django LTS compatível e Pillow são fixados em `pyproject.toml`/`uv.lock` e sincronizados pelo `uv` em `.venv` local.
- Nenhum serviço externo, segredo real ou ambiente de produção será acessado.
