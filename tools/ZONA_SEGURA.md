# Zona segura dos vídeos (1080x1920)

Os apps cobrem o vídeo com interface. Medido nos prints de Instagram, TikTok e YouTube Shorts (25/11/2026):

- Topo: ~290 px livres (status bar, busca do TikTok, cabeçalho do Instagram). NUNCA colocar logo, título ou barra de progresso aí.
- Base: nada abaixo de y=1400 (nome do perfil, legenda, barra de progresso do app).
- Direita: nada importante em x>880 entre y=750 e y=1400 (curtir, comentar, salvar, compartilhar).
- Esquerda: margem de ~110 px (o TikTok corta as laterais em telas altas).

No make.py as cenas são desenhadas numa camada transparente de 1080x1920 e `frame()` reduz a faixa
y=235..1600 por SAFE_K=0.795 para dentro da zona segura. Ao criar cenas novas, mantenha o conteúdo
entre y=250 e y=1580 e no mínimo 34 px de fonte (fica ~27 px depois da redução).
Sem barra de progresso desenhada no vídeo. Logo no início (cena 1) e grande no fim (CTA).

## Ritmo (sem silêncio morto)
A voz NÃO é acelerada. `trim_narr.py` corta só silêncio: sobra de 0,10 s antes e 0,22 s depois de cada fala
(0,5 s no último fecho) e pausas internas acima de 0,14 s viram 0,14 s. Ele grava `timing.json` com a duração
de cada cena; o `make.py` lê esse arquivo (variável TIMING_JSON) e acelera as animações da cena junto (SPEED).
Fluxo: `python3 trim_narr.py narracao.mp3 cuts.json audio/narracao_curta.wav timing.json`, renderizar as cenas,
juntar e `python3 mix.py audio/narracao_curta.wav audio/musica.mp3 silent.mp4 saida.mp4 timing.json`.
No vídeo "Crédito do zero": 42,4 s -> 38,1 s.


## Atualizacao 25/11: centralizacao
SAFE_K=0.77, DST_CX=540 (centro real do video), DST_Y0=320. Antes DST_CX=500 deixava o conteudo ~40 px para a esquerda. Margens simetricas: ~210 px de cada lado, area livre dos botoes da direita (x>880).
