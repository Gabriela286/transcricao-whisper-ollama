# Transcricao de Audio com Whisper e Extracao de Pontos-Chave com Ollama

Pipeline em Python que recebe um arquivo de audio (.wav ou .mp3), realiza a transcricao usando o Whisper e envia o texto ao Ollama para gerar um resumo com pontos-chave.

## Instalacao

1. Instale o FFmpeg e o Ollama (com o modelo llama3)
2. Instale as dependencias:
```bash
pip3 install -r requirements.txt
```

## Uso

```bash
python3 main.py audio/teste.mp3 --gerar-audio
```
