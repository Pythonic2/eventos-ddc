# PROMO-001 — Promoções repetíveis

## Contexto e problema
O Admin possui uma seção de promoção sem campo de valor e limitada a uma instância por página. A seção também depende da migration ainda não aplicada em produção. O administrador precisa cadastrar várias promoções independentes, com conteúdo rico, mantendo as demais seções estruturais únicas.

## Escopo / Fora de escopo
- Incluído: promoções repetíveis; título, valor, descrição, CTA, ordem e visibilidade; itens internos de texto, foto ou vídeo; renderização pública somente quando ativa; migration aditiva; publicação no GitHub e Cloud Run.
- Excluído: preço calculável, checkout, pagamentos, descontos automáticos, exclusão de conteúdo existente, alteração de DNS/Cloudflare ou deploy do Raspberry.

## Regras de negócio
- RB-01: uma página pode possuir várias seções do tipo `promocao`.
- RB-02: os demais tipos públicos continuam únicos por página.
- RB-03: cada promoção possui título obrigatório e valor textual opcional.
- RB-04: cada promoção aceita zero ou mais itens ativos de texto, foto ou vídeo, ordenados por `ordem` e `id`.
- RB-05: somente promoções e itens ativos aparecem no frontend.
- RB-06: uploads continuam sujeitos aos validadores existentes e ao storage configurado.

## Cenários de aceitação
- AC-01 — Dada uma promoção existente, quando o administrador abre a listagem, então ela aparece mesmo estando invisível no site.
- AC-02 — Dada uma página com promoção, quando o administrador adiciona outra promoção, então ambas são persistidas sem remover ou sobrescrever a anterior.
- AC-03 — Dada uma tentativa de duplicar outro tipo estrutural, quando o registro é validado, então a unicidade continua protegida.
- AC-04 — Dada uma promoção ativa, quando possui título, valor e descrição, então esses campos aparecem no frontend.
- AC-05 — Dada uma promoção ativa com itens de texto, foto e vídeo ativos, quando a página é aberta, então todos aparecem em ordem e com controles apropriados.
- AC-06 — Dada uma promoção inativa, quando a página é aberta, então ela não aparece.
- AC-07 — Dado o deploy aprovado, quando a migration é aplicada uma única vez no schema `eventosddc`, então nenhuma linha existente é apagada e o Cloud Run atualizado responde saudável.

## Requisitos não funcionais
- Segurança: somente usuários autorizados do Django Admin gerenciam promoções; validação de uploads e destinos de CTA permanece no servidor.
- Performance: mídias são carregadas sob demanda e buscadas por prefetch, sem consulta por item.
- Observabilidade: `/healthz/`, logs do Cloud Run e revisão pronta serão verificados após deploy.
- Acessibilidade: imagens exigem texto alternativo/fallback; vídeos mantêm controles e `playsinline`.

## Casos de falha e bordas
- Promoção sem mídia; valor vazio; vídeo sem arquivo; mídia inativa; ordens repetidas; tentativa de duplicar seção estrutural; migration já aplicada; falha de build/deploy.

## Perguntas / premissas
- “Valor” será texto de apresentação (por exemplo, `R$ 199,90` ou `Consulte`), sem semântica financeira ou cálculo.
- “Várias sessões” significa várias promoções; Empresa, Marcas, Eventos e WhatsApp permanecem singulares para preservar o layout.

## Rastreabilidade
| Critério | Teste/comprovação | Status |
|---|---|---|
| AC-01 | `test_admin_section_list_hides_legacy_sections` | passou |
| AC-02/AC-03 | `test_promotions_can_repeat_but_structural_sections_remain_unique` | passou |
| AC-04/AC-05/AC-06 | testes de promoção da `EventPageViewTests` | passou |
| AC-07 | migration + verificações pós-deploy | pendente |
