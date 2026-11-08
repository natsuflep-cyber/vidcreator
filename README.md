# Verbo

Site estático: você envia o **áudio** da narração e cola o **roteiro**, e o vídeo vertical (576×1024)
com legendas palavra por palavra é gerado e gravado no próprio navegador. Nada para editar nos arquivos.

## Como usar
1. Escolha o áudio. 2. Cole o roteiro (uma frase por linha; linha em branco = nova cena/fundo).
3. Opção "Mostrar legendas" (marcada por padrão). Destaques: `*amarelo*`, `~vermelho~`, `=verde=`. 4. **Prévia** ou **Gerar vídeo** e depois **Baixar**.

## Publicar (Vercel)
`public/` é servido como site estático (veja `vercel.json`). Basta `git push`; não há build.
Se o projeto estiver numa subpasta do repositório, defina *Root Directory* na Vercel.

## Extra
`render/` e `assets/` são o renderizador Python antigo da animação "A Última Vez" (opcional, só no seu computador).
O vídeo pronto está em `public/exemplo/a_ultima_vez.mp4`.
