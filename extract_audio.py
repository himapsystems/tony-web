import os
from moviepy import VideoFileClip
from pathlib import Path

# CONFIGURAÇÃO DE CAMINHOS
BASE_DIR = Path(__file__).parent
VIDEO_DIR = BASE_DIR / "frontend" / "public" / "videos"
OUTPUT_DIR = BASE_DIR / "backend" / "native_samples"

# CRIA DIRETÓRIO SE NÃO EXISTIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# MAPA DE TRADUÇÃO (Vídeo ID -> Fonema ID que o backend espera)
MAPPING = {
    "21.mp4": "ae.wav",
    "63.mp4": "ih.wav",
    "30.mp4": "uh.wav",
    "05.mp4": "ah.wav",
    "65.mp4": "th.wav",
    "61.mp4": "dh.wav",
    "47.mp4": "zh.wav",
    "07.mp4": "z.wav",
    "22.mp4": "h.wav"
}

def extract_and_convert():
    print(f"🔄 Iniciando extração de áudio...")
    print(f"📂 Origem: {VIDEO_DIR}")
    print(f"📂 Destino: {OUTPUT_DIR}")

    success_count = 0

    for video_file, audio_name in MAPPING.items():
        source = VIDEO_DIR / video_file
        target = OUTPUT_DIR / audio_name

        if source.exists():
            try:
                # Carrega video e extrai audio
                video = VideoFileClip(str(source))
                
                # CORREÇÃO: Removemos 'verbose=False' que não existe mais na v2.0+
                video.audio.write_audiofile(
                    str(target), 
                    codec='pcm_s16le', 
                    ffmpeg_params=["-ac", "1"], 
                    logger=None  # Isso substitui o verbose=False para silenciar logs
                )
                
                video.close()
                print(f"✅ Convertido: {video_file} -> {audio_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ Erro em {video_file}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado: {video_file} (Verifique se baixou este vídeo)")

    print(f"🏁 Concluído! {success_count}/{len(MAPPING)} áudios gerados.")

if __name__ == "__main__":
    extract_and_convert()