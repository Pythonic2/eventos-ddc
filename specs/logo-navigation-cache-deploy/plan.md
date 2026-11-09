# Plano — Logo, navegação, cache e deploy

1. Registrar a pasta `static/` no pipeline de static files e referenciar a logo por URL estável.
2. Substituir as marcas textuais da home e de `/eventos/` pela nova logo com link para as escolhas.
3. Resetar a sobreposição de transição em carregamento/restauração do bfcache e impedir timers antigos.
4. Ajustar cache privado das mídias e carregamento sob demanda de vídeos.
5. Adicionar testes de contrato para logo, retorno e política de desempenho.
6. Executar validações, revisar segurança/prontidão, publicar por commit/push e validar os dois ambientes.
