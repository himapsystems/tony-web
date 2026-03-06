import os
import shutil
import numpy as np
import parselmouth
import subprocess
import imageio_ffmpeg as ffmpeg_exe
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()

# Configuração CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
NATIVE_AUDIO_PATH = Path("native_samples")
NATIVE_AUDIO_PATH.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "online", "system": "Pronunciation MVP Backend"}

def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    finally:
        upload_file.file.close()

def convert_to_pcm_wav(input_path: Path, output_path: Path):
    """CONVERSÃO OBRIGATÓRIA: WebM (Browser) -> WAV PCM (Praat)"""
    ffmpeg_path = ffmpeg_exe.get_ffmpeg_exe()
    command = [
        ffmpeg_path, "-y", "-i", str(input_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
        str(output_path)
    ]
    # Roda silencioso para não sujar o log
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def analyze_vowel_pitch(sound_student, sound_native):
    try:
        pitch_student = sound_student.to_pitch()
        pitch_native = sound_native.to_pitch()
        
        vals_student = pitch_student.selected_array['frequency']
        vals_student = vals_student[vals_student != 0]
        
        vals_native = pitch_native.selected_array['frequency']
        vals_native = vals_native[vals_native != 0]

        if len(vals_student) == 0:
            return 0.0, "Não detectamos sua voz. Fale mais alto.", {}

        # Dados para Gráfico
        times_student = pitch_student.xs()
        original_vals_s = pitch_student.selected_array['frequency']
        graph_data_student = [{"time": t, "pitch": v if v > 0 else None} for t, v in zip(times_student, original_vals_s)]
        
        times_native = pitch_native.xs()
        original_vals_n = pitch_native.selected_array['frequency']
        graph_data_native = [{"time": t, "pitch": v if v > 0 else None} for t, v in zip(times_native, original_vals_n)]

        # Score Simples
        range_s = np.max(vals_student) - np.min(vals_student)
        range_n = np.max(vals_native) - np.min(vals_native)
        score = max(0, 100 - (abs(range_s - range_n) * 0.5))

        return score, "Entonação processada com sucesso!", {
            "student_pitch": graph_data_student,
            "native_pitch": graph_data_native
        }
    except Exception as e:
        print(f"Erro Vowel: {e}")
        return 0, "Erro na análise de vogal.", {}

def analyze_fricative_spectrum(sound_student, target_phoneme):
    try:
        spectrum = sound_student.to_spectrum()
        cog = spectrum.get_centre_of_gravity(power=2.0)
        
        refs = {"s": 6000, "z": 5500, "sh": 4000, "zh": 4000, "f": 2000, "v": 2000, "th": 2500, "dh": 2500, "h": 1000}
        target = refs.get(target_phoneme, 3000)
        
        score = max(0, 100 - (abs(cog - target) / 20))
        band = "green" if score > 75 else "yellow" if score > 50 else "red"
        
        return score, f"Freq: {int(cog)}Hz | Alvo: {target}Hz", {"cog": cog, "band_color": band}
    except Exception as e:
        print(f"Erro Fricative: {e}")
        return 0, "Erro na análise fricativa.", {"band_color": "red"}

@app.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    target_text: str = Form(...),
    target_phoneme: str = Form(...),
    target_type: str = Form(...)
):
    # 1. Salvar arquivo Bruto (WebM/Ogg do navegador)
    raw_path = UPLOAD_DIR / f"raw_{file.filename}"
    clean_path = UPLOAD_DIR / f"clean_{file.filename}.wav"
    save_upload_file(file, raw_path)
    
    try:
        # 2. CONVERTER PARA WAV REAL (Correção do erro "Not an audio file")
        convert_to_pcm_wav(raw_path, clean_path)
        
        # 3. Análise
        snd_student = parselmouth.Sound(str(clean_path))
        
        # Carrega Nativo
        native_file = NATIVE_AUDIO_PATH / f"{target_phoneme}.wav"
        if native_file.exists():
            snd_native = parselmouth.Sound(str(native_file))
        else:
            snd_native = snd_student # Fallback seguro
            
        if target_type == "fricative":
            score, fb, det = analyze_fricative_spectrum(snd_student, target_phoneme)
            return JSONResponse({"type": "fricative", "score": score, "feedback": fb, "details": det})
        else:
            score, fb, det = analyze_vowel_pitch(snd_student, snd_native)
            return JSONResponse({"type": "vowel", "score": score, "feedback": fb, "details": det})

    except Exception as e:
        print(f"ERRO BACKEND: {e}")
        return JSONResponse({
            "type": target_type, 
            "score": 0, 
            "feedback": "Erro técnico no áudio. Verifique o terminal.", 
            "details": {"band_color": "red"}
        })
    finally:
        # Limpeza
        if raw_path.exists(): os.remove(raw_path)
        if clean_path.exists(): os.remove(clean_path)