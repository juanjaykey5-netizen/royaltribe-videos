# royaltribe-videos
## Gerador generico (use este para videos novos)
`python3 tools/make_template.py spec.json outdir` renderiza 6 cenas Royal Signature (tipos: hook, stat, calc, cards, rule, cta) e junta em `outdir/silent.mp4`.
Exemplo de spec: `tools/spec_fundo_emergencia.json` (`durs` = duracao de cada linha da narracao vidIQ). Passo a passo:
1. `vidiq_voiceover_generate` (6 linhas, ~550 caracteres = ~40 s; 800 caracteres deu 57 s).
2. Coloque as `durationSeconds` das linhas em `durs` e rode make_template.py.
3. Suba `silent.mp4` em videos/, `git push`, `vidiq_video_upload url=raw...`.
4. `vidiq_compose` (1 cena video fill, voiceover.audioUrl do vidIQ, music = audio/musica.mp3 raw, duckTo 0.25, fadeMs 1200, loop true) -> `vidiq_job_poll` -> `vidiq_video_upload url=<compose videoUrl>`.
5. Thumbnail: `python3 tools/thumb.py "L1" "DESTAQUE" "sub" thumbs/NOME.png`, push, `vidiq_upload_image image=<raw url>` -> thumbnailImageId (YouTube).
6. draft_create -> publish -> status.

## Variedade (tema, fonte, cores e musica)
- Todo dia: `python3 tools/variety.py` imprime `TEMA MUSICA` (ex.: `esmeralda warm`), girando entre 6 temas (royal, esmeralda, ameixa, grafite, oceano, por-do-sol; cada um com fonte e cores proprias) e 5 trilhas (lofi, bright, calm, groove, warm).
- Ponha `"theme": "<tema>"` no spec do make_template.py e use `audio/music_<musica>.mp3` (raw GitHub) como music.audioUrl no vidiq_compose.
- Thumbnail no mesmo tema: `python3 tools/thumb.py "L1" "DESTAQUE" "sub" thumbs/NOME.png <tema>`.
- Novas trilhas: `python3 tools/music.py ESTILO audio/music_ESTILO.mp3 75`.

## Conteudo biblico (segundo canal de videos)
Mesmo gerador. Cena extra `verse` (title, lines = versiculo em linhas de ~24 caracteres, ref, foot = traducao). Modelo: `tools/spec_exemplo_biblico.json`. Use traducoes em dominio publico (Almeida Revista e Corrigida em PT, Reina-Valera 1909 em ES, KJV em EN).

## Carrossel Instagram (dias impares)
`python3 tools/make_carousel.py spec.json outdir` gera slide_01.jpg..N (1080x1350, JPEG) com logo Royal Signature fixa no canto superior esquerdo, conteudo centralizado entre y=230 e y=1090 (zona segura), tema/fonte/cores do dia (themes.py). Tipos: cover, alert, tip, list, compare, cta. Modelo: tools/spec_carrossel_exemplo.json; exemplo renderizado em carrosseis/exemplo/.
