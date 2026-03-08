FROM python:3.12-slim

# Instala dependências de sistema para áudio e ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    numpy \
    praat-parselmouth \
    imageio-ffmpeg \
    moviepy \
    matplotlib \
    supabase \
    python-dotenv

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]