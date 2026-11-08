DONA DO CHOPP — LANDING PAGE DE EVENTOS
======================================

Abra index.html no navegador para ver a página.

Tecnologias:
- HTML5, Bootstrap 5.3, Bootstrap Icons
- CSS personalizado e JavaScript puro
- Google Fonts (Outfit e DM Sans)

1. WHATSAPP
No final do index.html, configure:
  const WHATSAPP_DESTINO = '5585XXXXXXXXX';
Use o número REAL do cliente com 55 + DDD + número, somente dígitos.

2. FOTOS
As fotos de eventos usam links ilustrativos do Unsplash e dependem
 de internet. Substitua as URLs de imagens pelas fotos reais autorizadas
do cliente antes de publicar. A foto da chopeira e da atendente é a
imagem original fornecida pelo cliente em assets/bomba-dona-do-chopp.png.

3. VÍDEOS
Cadastre os vídeos na seção Eventos do Django Admin. Os uploads usam
o storage configurado pelo projeto e o frontend recebe a URL dinâmica
do FileField. MP4 com vídeo H.264 e áudio AAC oferece a melhor
compatibilidade entre computadores e celulares.

4. IMPLANTAÇÃO
Publique index.html e a pasta assets no mesmo diretório.
Bootstrap, fontes e imagens ilustrativas são carregados pela internet.
A página do formulário não possui backend: cria uma mensagem de WhatsApp.

5. REVISÃO DO CLIENTE
Confirme textos, fotos, serviços e condições reais antes de publicar.
Não há depoimentos, métricas ou promessas comerciais inventadas.
