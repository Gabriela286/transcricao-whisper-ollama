import os
import sys
import argparse
import whisper
import requests
from gtts import gTTS

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "llama3"


def validar_arquivo_audio(caminho_audio: str) -> bool:
    """Verifica se o arquivo existe e possui extensao .mp3 ou .wav."""
    if not os.path.isfile(caminho_audio):
        print(f"Erro: Arquivo '{caminho_audio}' nao encontrado.")
        return False

    extensoes_validas = (".mp3", ".wav")
    if not caminho_audio.lower().endswith(extensoes_validas):
        print(f"Erro: Formato invalido. Use apenas arquivos {extensoes_validas}.")
        return False

    return True


def transcrever_audio(caminho_audio: str, modelo_whisper: str = "base") -> str:
    """Passo 1: Carrega o modelo Whisper e realiza a transcricao do audio."""
    print(f"[1/2] Carregando modelo Whisper ('{modelo_whisper}') e transcrevendo...")
    try:
        modelo = whisper.load_model(modelo_whisper)
        resultado = modelo.transcribe(caminho_audio, language="pt")
        return resultado.get("text", "").strip()
    except Exception as e:
        print(f"Erro durante a transcricao com Whisper: {e}")
        sys.exit(1)


def extrair_pontos_chave(texto: str, modelo_ollama: str = DEFAULT_OLLAMA_MODEL) -> str:
    """Passo 2: Envia o texto transcrito para o Ollama e extrai os pontos-chave."""
    print(f"[2/2] Enviando transcricao para o Ollama (modelo '{modelo_ollama}')...")

    prompt = (
        "Voce e um assistente especialista em analise e sintese de informacoes. "
        "Analise a transcricao de audio abaixo e gere um resumo claro e objetivo em portugues, "
        "destacando os principais pontos-chave em formato de topicos (bullet points).\n\n"
        f"Transcricao:\n\"\"\"{texto}\"\"\""
    )

    payload = {
        "model": modelo_ollama,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        dados = response.json()
        return dados.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("Erro: Nao foi possivel conectar ao Ollama. Verifique se ele esta aberto.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao gerar resumo com Ollama: {e}")
        sys.exit(1)


def gerar_audio_resposta(texto: str, caminho_saida: str = "resumo_saida.mp3"):
    """Melhoria Opcional: Converte o resumo gerado em um arquivo de audio .mp3."""
    print(f"[Extra] Gerando arquivo de audio em '{caminho_saida}'...")
    try:
        texto_limpo = texto.replace("*", "")
        tts = gTTS(text=texto_limpo, lang="pt", slow=False)
        tts.save(caminho_saida)
        print(f"Audio salvo com sucesso em: {caminho_saida}")
    except Exception as e:
        print(f"Aviso: Nao foi possivel gerar o audio de resposta: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Transcricao de Audio (Whisper) e Extracao de Pontos-Chave (Ollama)."
    )
    parser.add_argument("audio", help="Caminho para o arquivo de audio (.mp3 ou .wav)")
    parser.add_argument("--whisper-model", default="base", help="Modelo Whisper (padrao: base)")
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL, help="Modelo Ollama (padrao: llama3)")
    parser.add_argument("--gerar-audio", action="store_true", help="Gera um .mp3 com o resumo")

    args = parser.parse_args()

    if not validar_arquivo_audio(args.audio):
        sys.exit(1)

    transcricao = transcrever_audio(args.audio, args.whisper_model)
    print("\n--- TRANSCRICAO COMPLETA ---")
    print(transcricao)
    print("----------------------------\n")

    if not transcricao:
        print("Aviso: Nenhum texto foi detectado no audio.")
        sys.exit(0)

    resumo = extrair_pontos_chave(transcricao, args.ollama_model)
    print("\n--- PONTOS-CHAVE (OLLAMA) ---")
    print(resumo)
    print("-----------------------------\n")

    if args.gerar_audio:
        gerar_audio_resposta(resumo)


if __name__ == "__main__":
    main()
