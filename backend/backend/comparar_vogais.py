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
    f1_raw, f2_raw, t_valid, inten_valid = [], [], [], []

    for t in times:
        f1 = formant.get_value_at_time(1, t)
        f2 = formant.get_value_at_time(2, t)
        inten = intensity.get_value(t)
        if np.isnan(f1) or np.isnan(f2) or inten < 55:
            continue
        # Filtro da vogal /ɛ/ (Red)
        if (350 < f1 < 950) and (1300 < f2 < 2500):
            f1_raw.append(f1)
            f2_raw.append(f2)
            t_valid.append(t)
            inten_valid.append(inten)

    f1_curve, f2_curve = [], []
    f1_alvo, f2_alvo = np.nan, np.nan
    
    if len(t_valid) > 5:
        t_valid_np = np.array(t_valid)
        inten_valid_np = np.array(inten_valid)
        
        t_max_inten = t_valid_np[np.argmax(inten_valid_np)]
        
        margem = 0.15 
        indices_janela = np.where((t_valid_np >= t_max_inten - margem) & 
                                  (t_valid_np <= t_max_inten + margem))[0]
        
        if len(indices_janela) < 4:
            indices_janela = np.arange(len(t_valid_np))
            
        t_focado = t_valid_np[indices_janela]
        f1_focado = np.array(f1_raw)[indices_janela]
        f2_focado = np.array(f2_raw)[indices_janela]
        
        grau = 2 if len(t_focado) > 3 else 1
        t_smooth = np.linspace(min(t_focado), max(t_focado), 50)
        coef_f1 = np.polyfit(t_focado, f1_focado, grau)
        coef_f2 = np.polyfit(t_focado, f2_focado, grau)
        
        f1_curve = np.polyval(coef_f1, t_smooth)
        f2_curve = np.polyval(coef_f2, t_smooth)
        
        f1_alvo = float(np.mean(f1_focado))
        f2_alvo = float(np.mean(f2_focado))
    
    return f1_alvo, f2_alvo, f1_curve, f2_curve, snd.to_pitch()

def suavizar_curva_f0(y, tamanho_janela):
    """Aplica uma média móvel para deixar a curva de Pitch redonda e orgânica."""
    if tamanho_janela < 3 or len(y) < tamanho_janela:
        return y
    box = np.ones(tamanho_janela) / tamanho_janela
    y_smooth = np.convolve(y, box, mode='same')
    # Corrige as bordas para não caírem
    margem = tamanho_janela // 2
    y_smooth[:margem] = y[:margem]
    y_smooth[-margem:] = y[-margem:]
    return y_smooth

def comparar_audios(caminho_nativa, caminho_aluno):
    print(f"🔄 Comparando: Nativa ({caminho_nativa}) vs. Aluno ({caminho_aluno})...")
    
    # === MUDE ESTE VALOR PARA TESTAR AS AMOSTRAS PARA O CLIENTE (Ex: 10, 15, 20) ===
    NIVEL_SUAVIZACAO_F0 = 15 
    
    try:
        f1_n, f2_n, c1_n, c2_n, p_n = extrair_dados_vogal(caminho_nativa)
        f1_a, f2_a, c1_a, c2_a, p_a = extrair_dados_vogal(caminho_aluno)

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

        # === GRÁFICO 1: MELODIA (AGORA COM SUAVIZAÇÃO ORGÂNICA) ===
        times_n = p_n.xs()
        times_a = p_a.xs()
        
        mask_n = vals_n > 0
        if np.any(mask_n):
            # Interpola e depois Suaviza
            vals_n_cont = np.interp(times_n, times_n[mask_n], vals_n[mask_n])
            vals_n_smooth = suavizar_curva_f0(vals_n_cont, NIVEL_SUAVIZACAO_F0)
            
            ax1.plot(times_n, vals_n_smooth, color='#4B0082', linewidth=3, label='Nativa')
            max_f0_n = np.max(vals_n_smooth)
            time_max_n = times_n[np.argmax(vals_n_smooth)]
            ax1.annotate('Ênfase Nativa', xy=(time_max_n, max_f0_n), xytext=(time_max_n, max_f0_n + 30),
                         arrowprops=dict(facecolor='#4B0082', shrink=0.05, width=2, headwidth=8),
                         ha='center', color='#4B0082', fontweight='bold')

        mask_a = vals_a > 0
        if np.any(mask_a):
            # Interpola e depois Suaviza
            vals_a_cont = np.interp(times_a, times_a[mask_a], vals_a[mask_a])
            vals_a_smooth = suavizar_curva_f0(vals_a_cont, NIVEL_SUAVIZACAO_F0)
            
            ax1.plot(times_a, vals_a_smooth, color='#008000', linewidth=3, label='Aluno')
            max_f0_a = np.max(vals_a_smooth)
            time_max_a = times_a[np.argmax(vals_a_smooth)]
            ax1.annotate('Sua Ênfase', xy=(time_max_a, max_f0_a), xytext=(time_max_a, max_f0_a + 30),
                         arrowprops=dict(facecolor='#008000', shrink=0.05, width=2, headwidth=8),
                         ha='center', color='#008000', fontweight='bold')

        ax1.set_title(f'Intonation Graph (Curva de Pitch) - Smooth: {NIVEL_SUAVIZACAO_F0}', pad=15)
        ax1.set_ylabel('Pitch (Hz)')
        ax1.set_xlabel('Time (s)')
        ax1.legend(loc='upper right')
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        max_y = 300
        if np.any(mask_n) or np.any(mask_a):
             max_y = max(np.max(vals_n_smooth) if np.any(mask_n) else 0, 
                         np.max(vals_a_smooth) if np.any(mask_a) else 0)
        ax1.set_ylim(bottom=50, top=max_y + 60)

        # === GRÁFICO 2: MAPA F1xF2 (MANTIDO INTACTO) ===
        if not np.isnan(f1_n) and not np.isnan(f1_a):
            ax2.scatter([f2_n], [f1_n], color='#FF0000', s=10000, alpha=0.07, label='Margem Aceitável')
            ax2.scatter([f2_n], [f1_n], color='#FF0000', s=3000, alpha=0.12)

            ax2.plot(c2_n, c1_n, '-', color='#800080', linewidth=4.5, alpha=0.8, label='Trajetória Nativa')
            ax2.plot(c2_a, c1_a, '-', color='#008000', linewidth=4.5, alpha=0.8, label='Trajetória Aluno')

            ax2.scatter([f2_n], [f1_n], color='#FF0000', s=600, zorder=15, edgecolors='white', linewidth=3, alpha=0.95, label='Alvo Nativa')
            ax2.scatter([f2_a], [f1_a], color='#00FF00', s=600, zorder=15, edgecolors='white', linewidth=3, alpha=0.95, label='Alvo Aluno')

            ax2.plot([f2_n, f2_a], [f1_n, f1_a], color='gray', linestyle='--', linewidth=2, zorder=10, alpha=0.5)
            
            distancia = np.sqrt((f2_n - f2_a)**2 + (f1_n - f1_a)**2)
            porcentagem = int(max(10, min(100, 100 - (distancia * 0.12))))

            if porcentagem >= 85:
                status = f"🎯 {porcentagem}% - EXCELENTE!"
                cor_feedback = '#008000'
            elif porcentagem >= 60:
                status = f"⚠️ {porcentagem}% - QUASE LÁ"
                cor_feedback = '#FFA500'
            else:
                status = f"❌ {porcentagem}% - FORA DO ALVO"
                cor_feedback = '#FF0000'

            dicas = []
            if f1_a < f1_n - 70: dicas.append("abra mais a boca")
            elif f1_a > f1_n + 70: dicas.append("feche um pouco a boca")
            
            if f2_a < f2_n - 150: dicas.append("projete a língua mais para frente")
            elif f2_a > f2_n + 150: dicas.append("recue um pouco a língua")
                
            texto_dica = f"Dica: {', '.join(dicas).capitalize()}." if dicas else "Perfeito! Mantenha assim."
            feedback_txt = f"{status}\n{texto_dica}"

            ax2.text(0.5, 0.08, feedback_txt, 
                     transform=ax2.transAxes,
                     fontsize=13, fontweight='bold', color=cor_feedback, ha='center', va='center', zorder=25,
                     bbox=dict(facecolor='white', alpha=0.95, edgecolor=cor_feedback, boxstyle='round,pad=0.7', linewidth=2))

        ax2.set_xlim(3000, 500)
        ax2.set_ylim(1200, 200)
        ax2.set_title('Mapa da Vogal: Feedback Pedagógico e Score', pad=15)
        ax2.set_ylabel('Pitch F1 (Abertura Boca)')
        ax2.set_xlabel('Pitch F2 (Posição Língua)')
        ax2.grid(True, color='#DDDDDD', linestyle='--', linewidth=1)
        ax2.legend(loc='upper right')

        pasta_saida = "graficos"
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)

        # O nome do arquivo agora inclui o nível de smooth para você não se perder
        nome_saida = f"comparativo_UI_smooth_{NIVEL_SUAVIZACAO_F0}_{os.path.basename(caminho_nativa).replace('.wav', '')}_vs_{os.path.basename(caminho_aluno).replace('.wav', '')}.png"
        caminho_final = os.path.join(pasta_saida, nome_saida)

        plt.savefig(caminho_final, bbox_inches='tight', dpi=300)
        print(f"✅ Gráfico final com Smooth {NIVEL_SUAVIZACAO_F0} salvo em: {caminho_final}")
        plt.close()

    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python comparar_vogais.py nativa.wav aluno.wav")
    else:
        comparar_audios(sys.argv[1], sys.argv[2])