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

def extrair_dados_vogal(caminho_arquivo):
    snd = parselmouth.Sound(caminho_arquivo)
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

    f1_curve, f2_curve = [], []
    f1_alvo, f2_alvo = np.nan, np.nan
    if len(t_valid) > 8:
        t_smooth = np.linspace(min(t_valid), max(t_valid), 100)
        coef_f1 = np.polyfit(t_valid, f1_raw, 3)
        coef_f2 = np.polyfit(t_valid, f2_raw, 3)
        f1_curve = np.polyval(coef_f1, t_smooth)
        f2_curve = np.polyval(coef_f2, t_smooth)
        f1_alvo = float(np.mean(f1_curve))
        f2_alvo = float(np.mean(f2_curve))
    
    return f1_alvo, f2_alvo, f1_curve, f2_curve, snd.to_pitch(), f1_raw, f2_raw

def comparar_audios(caminho_nativa, caminho_aluno):
    print(f"🔄 Comparando: Nativa ({caminho_nativa}) vs. Aluno ({caminho_aluno})...")
    try:
        f1_n, f2_n, c1_n, c2_n, p_n, f1_r_n, f2_r_n = extrair_dados_vogal(caminho_nativa)
        f1_a, f2_a, c1_a, c2_a, p_a, f1_r_a, f2_r_a = extrair_dados_vogal(caminho_aluno)

        # Calcula F0 médio de ambos para salvar no banco
        vals_n = p_n.selected_array['frequency']
        f0_medio_n = float(np.mean(vals_n[vals_n > 0])) if len(vals_n[vals_n > 0]) > 0 else 0
        
        vals_a = p_a.selected_array['frequency']
        f0_medio_a = float(np.mean(vals_a[vals_a > 0])) if len(vals_a[vals_a > 0]) > 0 else 0

        # --- SALVAR NO SUPABASE ---
        if not np.isnan(f1_n):
            salvar_resultado("nativa", f1_n, f2_n, f0_medio_n, os.path.basename(caminho_nativa))
        if not np.isnan(f1_a):
            salvar_resultado("aluno", f1_a, f2_a, f0_medio_a, os.path.basename(caminho_aluno))

        # --- PLOTAGEM ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), dpi=300)
        plt.subplots_adjust(hspace=0.35)

        # Gráfico 1: Melodia
        for p, col, lab in [(p_n, '#4B0082', 'Nativa'), (p_a, '#006400', 'Aluno')]:
            vals = p.selected_array['frequency']
            vals[vals==0] = np.nan
            ax1.plot(p.xs(), vals, color=col, linewidth=2.5, label=f'F0 {lab}')
            ax1.fill_between(p.xs(), vals, 0, where=(vals>0), color=col, alpha=0.1)

        ax1.set_title('Entonação da Frase (Melodia) - Comparativo', pad=15)
        ax1.legend(loc='upper right')
        ax1.grid(True, linestyle=':', alpha=0.6)

        # Gráfico 2: Mapa
        if not np.isnan(f1_n):
            ax2.scatter(f2_r_n, f1_r_n, color='#800080', s=10, alpha=0.3, label='Frames Nativa')
            ax2.plot(c2_n, c1_n, '-', color='#800080', linewidth=3, alpha=0.8, label='Trajetória Nativa')
            ax2.scatter([f2_n], [f1_n], color='#FF0000', s=350, zorder=10, edgecolors='white', linewidth=2.5)
            txt_n = ax2.text(f2_n - 150, f1_n, "/Nativa/", fontsize=14, fontweight='bold', color='#FF0000', verticalalignment='center')
            txt_n.set_path_effects([pe.withStroke(linewidth=4, foreground='white')])
        
        if not np.isnan(f1_a):
            ax2.scatter(f2_r_a, f1_r_a, color='#008000', s=10, alpha=0.3, label='Frames Aluno')
            ax2.plot(c2_a, c1_a, '-', color='#008000', linewidth=3, alpha=0.8, label='Trajetória Aluno')
            ax2.scatter([f2_a], [f1_a], color='#00FF00', s=350, zorder=10, edgecolors='white', linewidth=2.5)
            txt_a = ax2.text(f2_a + 100, f1_a, "/Aluno/", fontsize=14, fontweight='bold', color='#008000', verticalalignment='center')
            txt_a.set_path_effects([pe.withStroke(linewidth=4, foreground='white')])

        ax2.set_xlim(3000, 500)
        ax2.set_ylim(1200, 200)
        ax2.set_title('Mapa da Vogal: Comparativo /ɛ/', pad=15)
        ax2.grid(True, color='#DDDDDD', linestyle='--', linewidth=1)
        ax2.legend(loc='upper right')

        pasta_saida = "graficos"
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)

        nome_saida = f"comparativo_{os.path.basename(caminho_nativa).replace('.wav', '')}_vs_{os.path.basename(caminho_aluno).replace('.wav', '')}.png"
        caminho_final = os.path.join(pasta_saida, nome_saida)

        plt.savefig(caminho_final, bbox_inches='tight', dpi=300)
        print(f"✅ Gráfico comparativo salvo em: {caminho_final}")
        plt.close()

    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python comparar_vogais.py nativa.wav aluno.wav")
    else:
        comparar_audios(sys.argv[1], sys.argv[2])