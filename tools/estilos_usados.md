# Estilos usados (financas + biblia). Uma linha por video, a mais nova no fim.
# REGRA DO JUAN: cor, fonte e musica NAO repetem por pelo menos 7 videos seguidos (financas e biblia contam juntos); voz so entre as 4 em portugues (Keren, Roberta, Diego, Will-PT) e nao repete nos ultimos 3; estilo nao repete nos ultimos 3.
# Antes de produzir: python3 tools/escolher_estilo.py fin|bib (sorteia o que esta livre). Depois de produzir: python3 tools/escolher_estilo.py registrar SISTEMA ESTILO FORMATO ASSUNTO COR FONTE VOZ MUSICA
# Spec: "theme": COR, "font": FONTE; voz = voiceId do vidiq_voiceover_generate; musica = audio/music_<MUSICA>.mp3. Nao reutilize nada acima dentro da janela.
# CARROSSEIS (sistema car): python3 tools/escolher_estilo.py car (estilo: padrao|jornal|poster|quiz; nao repete nos ultimos 3 carrosseis; cor e fonte seguem a janela de 7). Gerador: make_carousel_fin.py (padrao) ou make_carrossel_estilos.py (jornal|poster|quiz).
# formato: AAAA-MM-DD | sistema (fin|bib) | estilo | formato do roteiro | assunto | cor | fonte | voz | musica   (? = nao registrado)
2026-11-25 | bib | padrao | versiculo + reflexao | Salmos 46:1 | ? | ? | ? | ?
2026-11-25 | bib | padrao | curiosidade | Genesis 3:6 (fruto, nao maca) | ? | ? | ? | ?
2026-11-25 | fin | padrao | explicativo | credito do zero nos EUA | ? | ? | ? | ?
2026-11-25 | fin | padrao | explicativo | fundo de emergencia | ? | ? | ? | ?

2026-11-25 | car | padrao | 3 erros | score de credito | grafite | oswald | - | -
2026-11-25 | car | padrao | alerta + checklist | cobranca de dividas (CFPB/FTC) | oceano | merriweather | - | -
2026-11-26 | car | carrossel-foto | pergunta + mito x realidade | por onde comecar a ler a Biblia (C01) | ameixa | montserrat | - | -
2026-11-26 | fin | padrao | mito x fato | Black Friday: juros diferidos e protecao do cartao | esmeralda | poppins(tema) | Keren | dream
