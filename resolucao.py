import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def gerar_markdown_final_corrigido():
    """
    Executa todos os cálculos com a geometria correta da imagem,
    gera os gráficos e cria um arquivo .md com a resolução detalhada.
    """
    #---------------------------------------------------------------------------
    # 1. PARÂMETROS DE ENTRADA
    #---------------------------------------------------------------------------
    L_m, d1, d2, d3, t = 7.1, 200.0, 415.0, 364.0, 13.0
    q1_kNm, q2_kNm = 19.0, 36.0
    E_aco_GPa, E_mad_GPa = 11.0, 108.0

    L, q1, q2 = L_m * 1000, q1_kNm, q2_kNm
    E_aco, E_mad = E_aco_GPa * 1000, E_mad_GPa * 1000

    #---------------------------------------------------------------------------
    # 2. CÁLCULOS
    #---------------------------------------------------------------------------
    # (a) Reações e (b) Momentos
    Ry_N = (q1 * L) / 2
    Rz_N = (q2 * L) / 2
    R_apoio_N = np.sqrt(Ry_N**2 + Rz_N**2)
    pos_Mmax_m = L_m / 2
    Mz_max_Nmm = (q1 * L**2) / 8
    My_max_Nmm = (q2 * L**2) / 8
    M_res_max_Nmm = np.sqrt(Mz_max_Nmm**2 + My_max_Nmm**2)

    # (c, d) Baricentro (GEOMETRIA CORRIGIDA)
    n = E_mad / E_aco
    
    # Baseado na imagem, com origem no canto inferior esquerdo
    largura_base = d1 + t + d1
    
    partes = {
        'Prancha Esq (Mad)':{'mat': 'mad', 'b': d1, 'h': d2, 'A': d1*d2, 'y_i': d2/2, 'z_i': d1/2},
        'Alma (Aço)':       {'mat': 'aco', 'b': t,  'h': d2, 'A': t*d2,  'y_i': d2/2, 'z_i': d1 + t/2},
        'Prancha Dir (Mad)':{'mat': 'mad', 'b': d1, 'h': d2, 'A': d1*d2, 'y_i': d2/2, 'z_i': d1 + t + d1/2},
        'Mesa (Aço)':       {'mat': 'aco', 'b': d3, 'h': t,  'A': d3*t,  'y_i': d2+t/2,'z_i': largura_base/2},
    }

    sum_A_t, sum_A_t_y, sum_A_t_z = 0, 0, 0
    for p in partes.values():
        p['A_t'] = p['A'] * n if p['mat'] == 'mad' else p['A']
        p['A_t_y'] = p['A'] * p['y_i'] * n if p['mat'] == 'mad' else p['A'] * p['y_i']
        p['A_t_z'] = p['A'] * p['z_i'] * n if p['mat'] == 'mad' else p['A'] * p['z_i']
        sum_A_t += p['A_t']
        sum_A_t_y += p['A_t_y']
        sum_A_t_z += p['A_t_z']
        
    y_bar = sum_A_t_y / sum_A_t
    z_bar = sum_A_t_z / sum_A_t

    # (e, f) Momentos de Inércia
    sum_Izg, sum_Iyg = 0, 0
    for p in partes.values():
        p['d_y'] = p['y_i'] - y_bar
        p['d_z'] = p['z_i'] - z_bar
        Izc, Iyc = (p['b'] * p['h']**3)/12, (p['h'] * p['b']**3)/12
        Izc_t = Izc * n if p['mat'] == 'mad' else Izc
        Iyc_t = Iyc * n if p['mat'] == 'mad' else Iyc
        p['Izg_p'] = Izc_t + p['A_t'] * p['d_y']**2
        p['Iyg_p'] = Iyc_t + p['A_t'] * p['d_z']**2
        sum_Izg += p['Izg_p']
        sum_Iyg += p['Iyg_p']
    I_zg, I_yg = sum_Izg, sum_Iyg

    # (g) Ângulo da Linha Neutra
    tan_phi = (My_max_Nmm / I_yg) * (I_zg / Mz_max_Nmm)
    phi_rad = np.arctan(tan_phi)
    phi_deg = np.degrees(phi_rad)
    
    # (h, i) Tensões
    def get_tensao(y, z, mat):
        y_p, z_p = y - y_bar, z - z_bar
        sigma = -(Mz_max_Nmm * y_p / I_zg) + (My_max_Nmm * z_p / I_yg)
        return (sigma * n, y_p, z_p) if mat == 'madeira' else (sigma, y_p, z_p)

    z_flange_esq = z_bar - d3/2
    z_flange_dir = z_bar + d3/2
    pontos_aco = {
        "Mesa Topo Esq": (d2+t, z_flange_esq), "Mesa Topo Dir": (d2+t, z_flange_dir),
        "Alma Base Esq": (0, d1), "Alma Base Dir": (0, d1 + t)
    }
    pontos_mad = {
        "Prancha Sup Esq": (d2, 0), "Prancha Sup Dir": (d2, largura_base),
        "Prancha Inf Esq": (0, 0), "Prancha Inf Dir": (0, largura_base)
    }
    res_tensoes_aco = {nome: get_tensao(y, z, 'aco') for nome, (y, z) in pontos_aco.items()}
    res_tensoes_mad = {nome: get_tensao(y, z, 'madeira') for nome, (y, z) in pontos_mad.items()}
    ponto_t_aco = max(res_tensoes_aco, key=lambda p: res_tensoes_aco[p][0])
    ponto_c_aco = min(res_tensoes_aco, key=lambda p: res_tensoes_aco[p][0])
    ponto_t_mad = max(res_tensoes_mad, key=lambda p: res_tensoes_mad[p][0])
    ponto_c_mad = min(res_tensoes_mad, key=lambda p: res_tensoes_mad[p][0])
    tensao_max_tracao_aco, yt_aco, zt_aco = res_tensoes_aco[ponto_t_aco]
    tensao_max_compressao_aco, yc_aco, zc_aco = res_tensoes_aco[ponto_c_aco]
    tensao_max_tracao_madeira, yt_mad, zt_mad = res_tensoes_mad[ponto_t_mad]
    tensao_max_compressao_madeira, yc_mad, zc_mad = res_tensoes_mad[ponto_c_mad]
    
    # (j) Giro nos Apoios
    E_aco_Pa = E_aco_GPa * 1e9
    I_zg_m4 = I_zg * (1e-3)**4
    q1_Nm = q1_kNm * 1000
    theta_apoio_rad = (q1_Nm * L_m**3) / (24 * E_aco_Pa * I_zg_m4)
    theta_apoio_deg = np.degrees(theta_apoio_rad)

    #---------------------------------------------------------------------------
    # 3. GERAÇÃO DOS GRÁFICOS
    #---------------------------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(8, 10))
    # Geometria para plotagem
    z_flange_start = largura_base/2 - d3/2
    # Partes
    prancha_esq = patches.Rectangle((0, 0), d1, d2, linewidth=1, edgecolor='k', facecolor='tan', label='Madeira')
    alma_aco = patches.Rectangle((d1, 0), t, d2, linewidth=1, edgecolor='k', facecolor='lightgray', label='Aço')
    prancha_dir = patches.Rectangle((d1 + t, 0), d1, d2, linewidth=1, edgecolor='k', facecolor='tan')
    mesa_aco = patches.Rectangle((z_flange_start, d2), d3, t, linewidth=1, edgecolor='k', facecolor='lightgray')
    
    ax1.add_patch(prancha_esq)
    ax1.add_patch(alma_aco)
    ax1.add_patch(prancha_dir)
    ax1.add_patch(mesa_aco)
    
    ax1.plot(z_bar, y_bar, 'r+', markersize=12, label='Centroide (CG)')
    ax1.axhline(y=y_bar, color='gray', linestyle='--', lw=0.8, label='Eixo $z_g$')
    ax1.axvline(x=z_bar, color='gray', linestyle='--', lw=0.8, label='Eixo $y_g$')
    
    z_ext = (d1 + t + d1)/2.2  # Extensão da linha neutra
    z_ln = np.array([z_bar - (z_ext), z_bar + z_ext])
    y_ln = y_bar + np.tan(phi_rad) * (z_ln - z_bar)
    ax1.plot(z_ln, y_ln, 'b--', lw=1.5, label=f'LN ($\\phi$) a {phi_deg:.2f}°')

    ax1.set_aspect('equal', adjustable='box') 
    ax1.set_title('Seção Transversal (Geometria Corrigida)') 
    ax1.set_xlabel('z (mm)') 
    ax1.set_ylabel('y (mm)') 
    ax1.set_xlim(-((d3/2)-(d1+t/2)+z_ext), (2*d1+t) + ((d3/2)-(d1+t/2)+z_ext))
    ax1.set_ylim(-z_ext, d2 + t + z_ext)
    ax1.legend(loc='best') 
    ax1.grid(True, linestyle=':', alpha=0.6)
    plt.savefig('secao_transversal_corrigida.png', dpi=150, bbox_inches='tight'); plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(7, 7)); ax2.axhline(0, color='gray', linestyle='--', lw=0.8) 
    ax2.axvline(0, color='gray', linestyle='--', lw=0.8)
    ax2.arrow(0, 0, My_max_Nmm, 0, head_width=20e6, fc='g', ec='g', label='$M_y$') 
    ax2.arrow(0, 0, 0, Mz_max_Nmm, head_width=20e6, fc='purple', ec='purple', label='$M_z$') 
    ax2.arrow(0, 0, My_max_Nmm, Mz_max_Nmm, head_width=20e6, fc='r', ec='r', label='$M_{res}$')
    theta_M_deg = np.degrees(np.arctan2(Mz_max_Nmm, My_max_Nmm))
    ax2.text(My_max_Nmm*0.6, Mz_max_Nmm*0.3, f'$\\theta_M = {theta_M_deg:.1f}°$', fontsize=12, color='r')
    ax2.set_aspect('equal', adjustable='box') 
    ax2.set_title('Vetores de Momento no Centroide') 
    ax2.set_xlabel('Eixo $z_g$'); ax2.set_ylabel('Eixo $y_g$') 
    ax2.legend(); ax2.grid(True, linestyle=':', alpha=0.6)
    plt.savefig('vetores_momento.png', dpi=150, bbox_inches='tight')
    plt.close(fig2)

    #---------------------------------------------------------------------------
    # 5. GERAÇÃO DO ARQUIVO MARKDOWN
    #---------------------------------------------------------------------------
    
    tabela_baricentro = "| Parte                 | Material | Área (A') (mm²) | y_i (mm) | z_i (mm) | A'y_i (mm³) | A'z_i (mm³) |\n|-----------------------|----------|-----------------|----------|----------|-------------|-------------|\n"
    for nome, p in partes.items():
        tabela_baricentro += f"| {nome:<21} | {p['mat']:<8} | {p['A_t']:<15.2f} | {p['y_i']:<8.2f} | {p['z_i']:<8.2f} | {p['A_t_y']:<11.1e} | {p['A_t_z']:<11.1e} |\n"

    tabela_inercia_z = "| Parte                 | I_zc' (mm⁴) | A' (mm²) | d_y (mm) | A'd_y² (mm⁴) | I_zg (mm⁴) |\n|-----------------------|-------------|----------|----------|--------------|------------|\n"
    for nome, p in partes.items():
        Izc_t = (p['b']*p['h']**3)/12 * (n if p['mat']=='mad' else 1)
        tabela_inercia_z += f"| {nome:<21} | {Izc_t:<11.2e} | {p['A_t']:<8.2f} | {p['d_y']:<8.2f} | {p['A_t']*p['d_y']**2:<12.2e} | {p['Izg_p']:<10.2e} |\n"
    
    tabela_inercia_y = "| Parte                 | I_yc' (mm⁴) | A' (mm²) | d_z (mm) | A'd_z² (mm⁴) | I_yg (mm⁴) |\n|-----------------------|-------------|----------|----------|--------------|------------|\n"
    for nome, p in partes.items():
        Iyc_t = (p['h']*p['b']**3)/12 * (n if p['mat']=='mad' else 1)
        tabela_inercia_y += f"| {nome:<21} | {Iyc_t:<11.2e} | {p['A_t']:<8.2f} | {p['d_z']:<8.2f} | {p['A_t']*p['d_z']**2:<12.2e} | {p['Iyg_p']:<10.2e} |\n"

    markdown = f"""
# Resolução Detalhada do Problema de Resistência dos Materiais

## Geometria e Parâmetros

> A resolução a seguir baseia-se na geometria da seção confirmada pela imagem e nos parâmetros fornecidos.
>
> - **Mesa de Aço:** Largura `{d3:.0f} x {t:.0f}` mm.
> - **Alma de Aço:** Largura `{t:.0f} x {d2:.0f}` mm.
> - **Pranchas de Madeira:** Duas de `{d1:.0f} x {d2:.0f}` mm.

| Parâmetro            | Valor                | Unidade |
|----------------------|----------------------|---------|
| Vão (L)              | {L_m:.2f}            | m       |
| Carga Vertical (q1)  | {q1_kNm:.2f}         | kN/m    |
| Carga Horizontal (q2)| {q2_kNm:.2f}         | kN/m    |
| E_aço (Em)           | {E_aco_GPa:.0f}      | GPa     |
| E_madeira (Ea)       | {E_mad_GPa:.0f}      | GPa     |

---

## (a) Resultante das Forças nos Apoios

As reações nos apoios são calculadas como metade da carga total em cada direção.

**Reação Vertical ($R_y$):**
$$ R_{{Ay}} = R_{{By}} = \\frac{{q_1 \\cdot L}}{{2}} = \\frac{{{q1_kNm:.1f} \\, \\text{{kN/m}} \\cdot {L_m:.1f} \\, \\text{{m}}}}{{2}} = {Ry_N/1000:.2f} \\, \\text{{kN}} $$
**Reação Horizontal ($R_z$):**
$$ R_{{Az}} = R_{{Bz}} = \\frac{{q_2 \\cdot L}}{{2}} = \\frac{{{q2_kNm:.1f} \\cdot {L_m:.1f} \\, \\text{{m}}}}{{2}} = {Rz_N/1000:.2f} \\, \\text{{kN}} $$
**Resultante no Apoio:**
$$ R_{{apoio}} = \\sqrt{{R_y^2 + R_z^2}} = \\sqrt{{{Ry_N/1000:.2f}^2 + {Rz_N/1000:.2f}^2}} = {R_apoio_N/1000:.2f} \\, \\text{{kN}} $$

- **Força Resultante em cada apoio: {R_apoio_N/1000:.2f} kN**

---

## (b) Momento Máximo Resultante

O momento fletor máximo ocorre no centro do vão ($x = L/2$) para cada eixo.

**Posição:**
$$ x = \\frac{{L}}{{2}} = \\frac{{{L_m:.1f}}}{{2}} = {pos_Mmax_m:.2f} \\, \\text{{m}} $$

**Componentes do Momento Máximo:**
$$ M_{{z,max}} = \\frac{{q_1 \\cdot L^2}}{{8}} = \\frac{{{q1_kNm:.1f} \\cdot {L_m:.1f}^2}}{{8}} = {Mz_max_Nmm/1e6:.2f} \\, \\text{{kN.m}} $$
$$ M_{{y,max}} = \\frac{{q_2 \\cdot L^2}}{{8}} = \\frac{{{q2_kNm:.1f} \\cdot {L_m:.1f}^2}}{{8}} = {My_max_Nmm/1e6:.2f} \\, \\text{{kN.m}} $$

**Momento Resultante Máximo:**
$$ M_{{res,max}} = \\sqrt{{M_{{z,max}}^2 + M_{{y,max}}^2}} = \\sqrt{{{Mz_max_Nmm/1e6:.2f}^2 + {My_max_Nmm/1e6:.2f}^2}} = {M_res_max_Nmm/1e6:.2f} \\, \\text{{kN.m}} $$

---

## (c, d) Posição do Baricentro da Seção Composta

Homogeneizando a seção em aço ($n = E_{{mad}}/E_{{aço}} = {n:.4f}$), com origem no canto inferior esquerdo:

{tabela_baricentro}

$$ \\bar{{z}} = \\frac{{\\sum A'_i \\cdot z_i}}{{\\sum A'_i}} = \\frac{{{sum_A_t_z:.2e}}}{{{sum_A_t:.2e}}} = {z_bar:.2f} \\, \\text{{mm}} $$
$$ \\bar{{y}} = \\frac{{\\sum A'_i \\cdot y_i}}{{\\sum A'_i}} = \\frac{{{sum_A_t_y:.2e}}}{{{sum_A_t:.2e}}} = {y_bar:.2f} \\, \\text{{mm}} $$

- **Posição $\\bar{{z}}$: {z_bar:.2f} mm**
- **Posição $\\bar{{y}}$: {y_bar:.2f} mm**

---

## (e, f) Momentos de Inércia

Calculados com o Teorema dos Eixos Paralelos ($ I = I_c + A \\cdot d^2 $).

**Cálculo de $I_{{zg}}$:**
{tabela_inercia_z}
- **Momento de Inércia $I_{{zg}}$: {I_zg:.3e} mm⁴**

**Cálculo de $I_{{yg}}$:**
{tabela_inercia_y}
- **Momento de Inércia $I_{{yg}}$:** {I_yg:.3e} mm⁴

---

## (g) Inclinação da Linha Neutra

$$ \\tan(\\phi) = \\frac{{M_y \\cdot I_{{zg}}}}{{M_z \\cdot I_{{yg}}}} = \\frac{{{My_max_Nmm:.3e} \\cdot {I_zg:.3e}}}{{{Mz_max_Nmm:.3e} \\cdot {I_yg:.3e}}} = {tan_phi:.3f} $$
- **Ângulo da Linha Neutra ($\phi$): {phi_deg:.2f}°**

---

## (h, i) Tensões Máximas

$$ \\sigma = -\\frac{{M_z \\cdot y'}}{{I_{{zg}}}} + \\frac{{M_y \\cdot z'}}{{I_{{yg}}}} $$

**Tensões no Aço:**
- **Tração Máxima:** Ocorre em `{ponto_t_aco}` (y'={yt_aco:.2f}, z'={zt_aco:.2f}).
  $$ \\sigma_{{t,max}} = -\\frac{{{Mz_max_Nmm:.2e} \\cdot ({yt_aco:.2f})}}{{{I_zg:.2e}}} + \\frac{{{My_max_Nmm:.2e} \\cdot ({zt_aco:.2f})}}{{{I_yg:.2e}}} = **{tensao_max_tracao_aco:.2f} MPa** $$
- **Compressão Máxima:** Ocorre em `{ponto_c_aco}` (y'={yc_aco:.2f}, z'={zc_aco:.2f}).
  $$ \\sigma_{{c,max}} = -\\frac{{{Mz_max_Nmm:.2e} \\cdot ({yc_aco:.2f})}}{{{I_zg:.2e}}} + \\frac{{{My_max_Nmm:.2e} \\cdot ({zc_aco:.2f})}}{{{I_yg:.2e}}} = **{tensao_max_compressao_aco:.2f} MPa** $$

**Tensões na Madeira:**
- **Tração Máxima:** Ocorre em `{ponto_t_mad}` (y'={yt_mad:.2f}, z'={zt_mad:.2f}).
  $$ \\sigma_{{t,max}} = n \\cdot \\left( ... \\right) = **{tensao_max_tracao_madeira:.2f} MPa** $$
- **Compressão Máxima:** Ocorre em `{ponto_c_mad}` (y'={yc_mad:.2f}, z'={zc_mad:.2f}).
  $$ \\sigma_{{c,max}} = n \\cdot \\left( ... \\right) = **{tensao_max_compressao_madeira:.2f} MPa** $$

---

## (j) Giro Relativo Entre os Apoios

$$ \\theta = \\frac{{q_1 \\cdot L^3}}{{24 \\cdot E_{{aço}} \\cdot I_{{zg}}}} = \\frac{{({q1_Nm:.0f}) \\cdot ({L_m:.1f})^3}}{{24 \\cdot ({E_aco_Pa:.2e}) \\cdot ({I_zg_m4:.2e})}} $$
- **Giro no apoio:** {theta_apoio_rad:.5f} rad ({theta_apoio_deg:.4f}°)

---

## Visualizações Gráficas

### Seção Transversal e Linha Neutra
![Seção Transversal Corrigida](secao_transversal_corrigida.png)

### Vetores de Momento na Seção
![Vetores de Momento Atuantes](vetores_momento.png)
"""

    file_name = "resolucao_problema.md"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(markdown.strip())
        
    return f"Arquivo '{file_name}' e as imagens de suporte foram gerados com sucesso!"

# Executar a função para gerar o arquivo e os gráficos
gerar_markdown_final_corrigido()