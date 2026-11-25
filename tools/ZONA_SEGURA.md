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
