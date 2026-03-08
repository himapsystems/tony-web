# Pronunciation MVP – Análise Acústica e Trajetória de Vogais

## 🎯 O que este MVP faz
Este sistema realiza uma análise fonética e acústica profunda, comparando a fala de um estudante com a de um falante nativo. O foco principal desta etapa de validação técnica é a precisão na extração de dados e a facilidade de replicação do ambiente.

O motor do MVP agora é capaz de:
- **Extração Dinâmica (Frame a Frame):** Utiliza o Praat/Parselmouth para extrair os formantes F1 e F2 em janelas deslizantes de 5ms, capturando o movimento real da língua durante a vogal.
- **Gráficos Comparativos (F1 x F2):** Plota a trajetória formântica e o alvo exato da vogal do aluno versus a nativa.
- **Análise de Entonação (F0):** Extrai o pitch (Melodia) real da fala de ambos os usuários para visualização de ritmo e cadência.
- **Integração Cloud (Supabase):** Salva automaticamente os resultados processados (F1, F2 e F0 médios) no banco de dados em nuvem.
- **Ambiente Conteinerizado:** Roda inteiramente via Docker, eliminando a necessidade de instalar Python, Node ou configurar `venv` manualmente na máquina local.

---

## 🛠️ Tecnologias Utilizadas
- **Ambiente:** Docker & Docker Compose
- **Backend / Motor Acústico:** Python + FastAPI + Parselmouth (Praat) + FFmpeg
- **Banco de Dados:** Supabase (PostgreSQL)
- **Frontend:** Next.js + Recharts (Código Legado de Validação)
- **Visualização de Dados:** Matplotlib + Numpy

---

## 🚀 Como rodar localmente (Sem instalar Python/Node)

Para garantir uma execução padronizada em qualquer máquina, o projeto foi migrado para **Docker**. 

### 1. Pré-requisitos
Certifique-se de ter o [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando na sua máquina.

### 2. Configuração do Banco de Dados (.env)
Antes de subir o projeto, configure as credenciais do Supabase.
Dentro da pasta `backend/`, crie um arquivo chamado exatamente `.env` e insira suas chaves:

```env
SUPABASE_URL="[https://sua-url-do-supabase.supabase.co](https://sua-url-do-supabase.supabase.co)"
SUPABASE_KEY="sua-chave-anon-public-aqui"

### 3. Subindo o Projeto

No terminal, na pasta raiz do projeto (onde está o arquivo docker-compose.yml), execute:

docker compose up --build

### 4. Acessando os Serviços

Uma vez que os contêineres estejam rodando, você pode acessar:

    Frontend (Interface Web): http://localhost:3000

    Backend (API Docs): http://localhost:8000/docs


🧪 Como testar o Motor de Análise Acústica (Teste Técnico)
Para validar a extração de áudio, geração do gráfico F1xF2 e persistência no Supabase, abra um novo terminal (mantendo o projeto rodando) e execute o script de comparação por dentro do contêiner:

docker compose exec backend python backend/comparar_vogais.py native_samples/red.wav native_samples/meuaudio.wav

O que este comando faz?

    Processa os dois arquivos de áudio informados.

    Extrai os formantes frame a frame de ambos.

    Salva os valores matemáticos resultantes diretamente na tabela analises_acusticas do Supabase.

    Gera uma imagem comparativa de alta resolução e salva automaticamente na pasta graficos/ na raiz do projeto.