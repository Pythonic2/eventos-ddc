# Plano técnico — Promoções repetíveis

## Estado atual e interfaces afetadas
- `EventSection` possui unicidade global por `pagina,tipo` e não possui valor.
- A view transforma seções em dicionário, descartando duplicatas.
- O Admin só oferece tipos ainda ausentes e a promoção aceita uma imagem.
- O frontend renderiza no máximo uma promoção.

## Solução proposta
- Dados: adicionar `EventSection.valor` e substituir a constraint global por uma constraint condicional que exclui `promocao`.
- Admin: manter tipos estruturais singulares; oferecer `Promoção` sempre; usar inline rico com texto, foto e vídeo.
- View: separar seções estruturais singulares de uma lista ordenada de promoções.
- Template: iterar promoções e suas mídias ativas prefetched.
- Deploy: migration aditiva no schema `eventosddc`, commit/push na `main`, aguardar o trigger único do Cloud Build e validar a revisão.

## Alternativas e justificativa
- Remover toda unicidade foi rejeitado porque a view/layout dependem de Empresa, Marcas, Eventos e WhatsApp únicos.
- Criar novo model exclusivo de promoção foi rejeitado por duplicar campos, storage e Admin sem necessidade.
- Valor decimal foi rejeitado porque não há checkout ou regra financeira; texto preserva formatos promocionais.

## Riscos e compatibilidade
- A migration remove e recria apenas a constraint; não altera linhas existentes.
- Rollback do app pode conviver com a coluna extra, mas versões antigas não suportam múltiplas promoções; rollback de tráfego exige manter apenas uma ativa ou avaliar dados antes.
- O deploy não executa migrations automaticamente; a migration será aplicada uma única vez antes de atualizar o serviço.

## Plano de teste e recuperação
- Unitários: constraint condicional, valor e tipos de mídia.
- Integração: Admin, view pública, visibilidade e ordenação.
- Segurança: usuário comum continua sem acesso; uploads/URLs usam validadores existentes.
- Rollback: direcionar tráfego para a revisão anterior; não reverter banco automaticamente.

## Dependências e decisões
- Sem dependências novas.
- GCS privado, Neon e failover existentes são preservados.
