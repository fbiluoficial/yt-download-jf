# YouTube Downloader

Um aplicativo web para download de vídeos do YouTube com interface escura e responsiva.

 [Demo / Página do Projeto](https://fbiluoficial.github.io/yt-download-jf/)

## Funcionalidades

- Campo para múltiplos links do YouTube
- Download em formato MP3 ou MP4
- Design responsivo e tema escuro
- Download automático após confirmação
- Barra de progresso em tempo real
- Salvamento em diretório local

## Requisitos

- Python 3.7+
- Flask
- yt-dlp
- pydub

## Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/fbiluoficial/yt-download-jf.git
cd yt-download-jf
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o servidor:
```bash
python app.py
```

4. Abra o navegador e acesse:
```
http://localhost:5000
```

## Como Usar

1. Cole os links dos vídeos do YouTube (um por linha)
2. Selecione o formato desejado (MP3 ou MP4)
3. Clique em "Baixar"
4. Acompanhe o progresso em tempo real
5. Os arquivos serão salvos na pasta Downloads

## Observações

- Os downloads são salvos na pasta Downloads do usuário
- Certifique-se de ter permissão de escrita no diretório
- A versão online (GitHub Pages) é apenas demonstrativa
- Para funcionalidade completa, execute localmente

## Tecnologias Utilizadas

- Backend:
  - Python
  - Flask
  - yt-dlp
  - pydub

- Frontend:
  - HTML5
  - JavaScript
  - Bootstrap 5
  - CSS3

## Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
