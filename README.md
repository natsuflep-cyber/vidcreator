# A Última Vez

Animação vertical (576×1024, 30 fps, 92 s) feita 100% por código em Python (OpenCV + Pillow + ffmpeg),
sincronizada com a narração em `assets/narracao.mp3`. O site em `public/` apenas exibe o vídeo pronto.

## Importante sobre a Vercel
A Vercel **não** consegue renderizar o vídeo (não tem ffmpeg e as funções têm limite de tempo).
Por isso o fluxo é: **renderizar no seu computador** → colocar o `.mp4` em `public/` → subir no GitHub → a Vercel publica a página.
O vídeo já renderizado está em `public/a_ultima_vez.mp4`, então você pode publicar direto.

## Estrutura
```
assets/narracao.mp3      áudio da narração
render/lib.py            desenho: formas, personagens, props, texto
render/render.py         cenas, legenda palavra por palavra, tempos e exportação
public/index.html        página que toca o vídeo (é isso que a Vercel serve)
public/a_ultima_vez.mp4  vídeo final
vercel.json              diz à Vercel para servir a pasta public/
```

## Renderizar no seu computador
Requisitos: Python 3.9+ e ffmpeg instalado (`ffmpeg -version` deve funcionar).
```bash
pip install -r requirements.txt

# pré-visualizar alguns instantes (gera render/test.jpg)
python render/render.py test 4 20 50 70 91

# renderizar o vídeo completo (leva alguns minutos)
python render/render.py full public/a_ultima_vez.mp4
```
Se der erro de fonte, defina `FONT_PATH` com o caminho de um arquivo `.ttf` em negrito.

## Mudar o áudio ou a história
- Troque `assets/narracao.mp3` e ajuste a lista `PHR` em `render/render.py`
  (cada item é: texto, início em segundos, fim em segundos).
- Ajuste `DUR` (duração total) e a lista `SCENES` (início, fim, função da cena).
- Cada cena é uma função `scN` em `render/render.py`; personagens ficam em `render/lib.py`
  (`davi`, `rita`, `mom`, `kid`).

## Publicar no GitHub + Vercel
```bash
git init
git add .
git commit -m "A Última Vez"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/a-ultima-vez.git
git push -u origin main
```
1. Em vercel.com: **Add New → Project** e importe o repositório.
2. **Framework Preset:** Other. **Output Directory:** `public` (o `vercel.json` já indica isso). Sem build command.
3. **Deploy.** A cada `git push`, a Vercel publica de novo.
