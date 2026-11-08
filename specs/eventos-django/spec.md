# EVT-001 — Página de eventos administrável em Django

## Contexto e problema
A página de eventos é HTML estático. A equipe administrativa precisa atualizar textos, CTAs, fotos e vídeos sem editar código, preservando a experiência cinematográfica existente.

## Escopo / Fora de escopo
- Incluído: projeto Django tradicional, SQLite local, models, migrations, Admin, view/template em `/eventos/`, uploads locais de desenvolvimento, testes e integração da navegação.
- Excluído: DRF, CMS genérico, deploy, banco/bucket de produção, criação de usuários reais e alteração do fluxo comercial/WhatsApp.

## Atores e papéis
- Visitante anônimo: consulta apenas conteúdo ativo da página pública.
- Usuário administrativo autenticado e com permissões: gerencia conteúdo pelo Django Admin.

## Regras de negócio
- RB-01: existe no máximo uma configuração `EventPage`; a página funciona com ou sem registro configurado.
- RB-02: somente página, seções e mídias ativas são exibidas; mídias são ordenadas por `ordem` e identificador.
- RB-03: seções possuem tipos estruturados (`vantagens`, `galeria`, `ocasioes`, `localizacao`, `cta_final`, `videos`, `orcamento`, `faq`), sem construtor genérico.
- RB-04: imagens aceitam somente formatos de imagem permitidos e até 10 MiB; vídeos aceitam formatos permitidos e até 100 MiB.
- RB-05: URLs configuráveis aceitam somente HTTP(S), caminho interno absoluto, âncora ou link `mailto:`/`tel:`.
- RB-06: textos são renderizados com escaping padrão do Django e sem uso de `safe` para conteúdo administrativo.
- RB-07: atendimento de eventos abrange Fortaleza–CE e Região Metropolitana, com essa área visível na prepage e na página de eventos.
- RB-08: as imagens atuais são fallbacks do frontend; o cliente edita títulos/textos e adiciona ou troca fotos e vídeos pelo Admin simplificado.
- RB-09: cada seção permite editar chamada, título, subtítulo, texto principal, texto complementar, CTA e itens internos ordenáveis com título, descrição, foto ou vídeo.
- RB-10: todo texto editorial e toda mídia das seções visíveis da página dinâmica possuem origem administrável; elementos funcionais do formulário e avisos legais permanecem no código.

## Cenários de aceitação
- AC-01 — Dado o projeto local, quando `/eventos/` é acessado, então responde HTTP 200 e preserva o layout cinematográfico.
- AC-02 — Dado conteúdo cadastrado, quando a página é aberta, então títulos, descrições, SEO e CTAs vêm dos models.
- AC-03 — Dadas mídias ativas e inativas, quando a galeria é renderizada, então somente ativas aparecem em ordem.
- AC-04 — Dada ausência de mídia/conteúdo opcional, quando a página é aberta, então não ocorre erro e há fallback visual/textual.
- AC-05 — Dado usuário sem permissão, quando tenta alterar conteúdo no Admin, então a autorização do Django impede a alteração.
- AC-06 — Dado upload ou URL inválida, quando o model/form é validado, então recebe mensagem compreensível e o dado é recusado.
- AC-07 — Dado superusuário local, quando edita e salva conteúdo pelo Admin, então a mudança aparece na página pública sem deploy.
- AC-08 — Dada qualquer seção visual, quando o administrador altera seus títulos/textos ou itens internos, então a seção pública reflete a alteração mantendo o layout correspondente.
- AC-09 — Dadas fotos ou vídeos em uma seção, quando a página é renderizada, então a mídia ativa aparece em ordem, sem deformação e com fallback quando ausente.

## Requisitos não funcionais
- Segurança: `SECRET_KEY` e modo debug configuráveis por ambiente; cookies seguros quando fora de debug; uploads validados; Admin protegido pela autenticação e permissões nativas.
- Performance: imagens abaixo da dobra com lazy loading; vídeos com `preload="none"`; consultas relacionadas carregadas com prefetch.
- Observabilidade: logging padrão do Django; erros de configuração detectados por `manage.py check`.
- Acessibilidade: textos alternativos configuráveis, botões identificáveis, conteúdo essencial independente de animações e suporte a `prefers-reduced-motion` preservado.
- Recuperação: rollback local consiste em remover os novos módulos/migration e restaurar o HTML estático; nenhum recurso de produção é alterado.

## Casos de falha e bordas
- Configuração ainda não criada, seção vazia, imagem ausente, vídeo externo ou arquivo local, ordem repetida, URL malformada e arquivo com extensão/tamanho inválidos.
- Concorrência de edição usa o comportamento padrão de última gravação do Django Admin; aceitável para a única página e pequena equipe.

## Perguntas / premissas
- SQLite e filesystem local são usados somente em desenvolvimento; storage de produção permanece decisão futura.
- O número oficial de WhatsApp informado para os contatos do site é `+55 85 99180-3678`.

## Rastreabilidade
| Critério | Teste/comprovação | Status |
|---|---|---|
| AC-01 | `test_event_page_returns_200_without_configuration` + prova HTTP local | passou |
| AC-02 | `test_database_content_is_rendered_and_escaped` | passou |
| AC-03 | `test_only_active_media_is_shown_in_configured_order` | passou |
| AC-04 | testes sem configuração e página inativa | passou |
| AC-05 | `test_regular_user_cannot_access_admin_change` | passou |
| AC-06 | testes de URL, fontes e compatibilidade de mídia | passou |
| AC-07 | `test_admin_can_change_title_and_public_page_reflects_it` | passou |
| AC-08 | `test_all_visual_sections_are_seeded_and_editable` | passou |
| AC-09 | testes de ordenação/visibilidade de mídia, item textual e formulário genérico do Admin | passou |
