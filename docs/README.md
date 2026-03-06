# Pronunciation MVP – Entonation Analysis

## O que este MVP faz
Este sistema permite comparar a entonação da fala de um estudante com uma fala nativa do inglês americano.

O MVP é capaz de:
- Extrair o pitch (F0) real da fala do aluno e da nativa
- Identificar o ponto principal de ênfase da frase
- Comparar alcance melódico e timing do pico de entonação
- Exibir gráficos comparativos em tempo real
- Gerar feedback pedagógico automático

## Componentes implementados

### 1. Gráfico de entonação
- Curva verde: falante nativo
- Curva vermelha: estudante
- Linhas verticais indicam o ponto de ênfase de cada um

### 2. Gráfico de intensidade
- Comparação visual da intensidade ao longo da frase

### 3. Feedback automático
Exemplos:
- “Seu alcance melódico está menor que o da nativa.”
- “Seu pico de ênfase ocorre X ms depois do ideal.”

## Tecnologias
- Frontend: Next.js + Recharts
- Backend: FastAPI + Parselmouth + FFmpeg
- Análise acústica real (não mock)

## Como rodar localmente

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000


### frontend

cd frontend
npm install
npm run dev

Acesse:

Frontend: http://localhost:3000

Backend: http://127.0.0.1:8000/docs