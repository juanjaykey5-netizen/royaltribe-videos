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
