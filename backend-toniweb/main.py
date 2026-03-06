from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import parselmouth

app = FastAPI()

# Permite que o Frontend Next.js converse com este Backend Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), target_text: str = Form(...)):
    # Lê o áudio gravado no celular [cite: 3, 5]
    audio_data = await file.read()
    snd = parselmouth.Sound(audio_data)
    
    # Extração de Pitch (Melodia da voz) via Praat [cite: 3, 8]
    pitch = snd.to_pitch()
    values = pitch.selected_array['frequency']
    
    # Gera o score de forma local e gratuita [cite: 12, 27]
    valid_pitch = [p for p in values if p > 0]
    score = 80.0 if len(valid_pitch) > 0 else 0.0
    
    return {
        "score": score,
        "feedback": "Excelente! Gráfico processado." if score > 0 else "Áudio não detectado.",
        "details": {
            "student_pitch": [p if p > 0 else None for p in values],
            "native_pitch": [200, 210, 225, 210, 200] # Mock para comparação
        }
    }