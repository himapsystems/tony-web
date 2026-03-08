import sys
import parselmouth
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as pe
import os

# Importa a nossa função de salvar no banco
from database import salvar_resultado

# --- CONFIGURAÇÃO VISUAL PREMIUM ---
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.labelsize': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16
})

def analisar_profissional(caminho_arquivo):
    print(f"🔄 Processando áudio: {caminho_arquivo}...")
    
    try:
        snd = parselmouth.Sound(caminho_arquivo)
        pitch = snd.to_pitch()
        intensity = snd.to_intensity()
        formant = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5)
        
        times = np.arange(0, snd.get_total_duration(), 0.005)
        f1_raw, f2_raw, t_valid = [], [], []

        for t in times:
            f1 = formant.get_value_at_time(1, t)
            f2 = formant.get_value_at_time(2, t)
            inten = intensity.get_value(t)
            
            if np.isnan(f1) or np.isnan(f2) or inten < 55:
                continue

            if (350 < f1 < 950) and (1300 < f2 < 2500):
                f1_raw.append(f1)
                f2_raw.append(f2)
                t_valid.append(t)

        has_vowel = False
        if len(t_valid) > 8:
            has_vowel = True
            t_smooth = np.linspace(min(t_valid), max(t_valid), 100)
            coef_f1 = np.polyfit(t_valid, f1_raw, 3)
            coef_f2 = np.polyfit(t_valid, f2_raw, 3)
            f1_curve = np.polyval(coef_f1, t_smooth)
            f2_curve = np.polyval(coef_f2, t_smooth)
            
            f1_alvo = float(np.mean(f1_curve))
            f2_alvo = float(np.mean(f2_curve))
        else:
            f1_alvo, f2_alvo = 0, 0

        # Calcula F0 médio
        pitch_vals = pitch.selected_array['frequency']
        f0_medio = float(np.mean(pitch_vals[pitch_vals > 0])) if len(pitch_vals[pitch_vals > 0]) > 0 else 0

        # --- SALVAR NO SUPABASE ---
        if has_vowel:
            salvar_resultado("individual", f1_alvo, f2_alvo, f0_medio, os.path.basename(caminho_arquivo))

        # --- PLOTAGEM ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), dpi=300)
        plt.subplots_adjust(hspace=0.35)

        pitch_vals[pitch_vals==0] = np.nan
        ax1.plot(pitch.xs(), pitch_vals, color='#4B0082', linewidth=2.5, label='F0 (Melodia)')
        ax1.fill_between(pitch.xs(), pitch_vals, 0, where=(pitch_vals>0), color='#4B0082', alpha=0.1)
        ax1.set_title('Entonação da Frase (Melodia)', pad=15)
        ax1.set_ylabel('Frequência (Hz)')
        ax1.grid(True, linestyle=':', alpha=0.6)

        if has_vowel:
            ax2.plot(f2_curve, f1_curve, '-', color='#800080', linewidth=5, alpha=0.8, label='Movimento da Língua')
            ax2.scatter([f2_alvo], [f1_alvo], color='#FF0000', s=350, zorder=10, edgecolors='white', linewidth=2.5, label='Centro do Alvo')
            nome_vogal = os.path.basename(caminho_arquivo).replace(".wav", "").replace("_", " ").title()
            txt = ax2.text(f2_alvo - 250, f1_alvo, f"/{nome_vogal}/", fontsize=14, fontweight='bold', color='#333333')
            txt.set_path_effects([pe.withStroke(linewidth=4, foreground='white')])

        ax2.set_xlim(3000, 500)
        ax2.set_ylim(1200, 200)
        ax2.set_title('Mapa da Vogal: Análise de Trajetória', pad=15)
        ax2.set_xlabel('F2 - Anterioridade (Hz)')
        ax2.set_ylabel('F1 - Altura (Hz)')
        ax2.grid(True, color='#DDDDDD', linestyle='--', linewidth=1)

        pasta_saida = "graficos"
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)
        
        nome_imagem = os.path.basename(caminho_arquivo).replace(".wav", "_analise_pro.png")
        caminho_final = os.path.join(pasta_saida, nome_imagem)

        plt.savefig(caminho_final, bbox_inches='tight', dpi=300)
        print(f"✅ Gráfico individual salvo em: {caminho_final}")
        plt.close()

    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analise_pro.py arquivo.wav")
    else:
        analisar_profissional(sys.argv[1])