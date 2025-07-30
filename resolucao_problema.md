# Resolução Detalhada do Problema de Resistência dos Materiais

## Geometria e Parâmetros

> A resolução a seguir baseia-se na geometria da seção confirmada pela imagem e nos parâmetros fornecidos.
>
> - **Mesa de Aço:** Largura `364 x 13` mm.
> - **Alma de Aço:** Largura `13 x 415` mm.
> - **Pranchas de Madeira:** Duas de `200 x 415` mm.

| Parâmetro            | Valor                | Unidade |
|----------------------|----------------------|---------|
| Vão (L)              | 7.10            | m       |
| Carga Vertical (q1)  | 19.00         | kN/m    |
| Carga Horizontal (q2)| 36.00         | kN/m    |
| E_aço (Em)           | 11      | GPa     |
| E_madeira (Ea)       | 108      | GPa     |

---

## (a) Resultante das Forças nos Apoios

As reações nos apoios são calculadas como metade da carga total em cada direção.

**Reação Vertical ($R_y$):**
$$ R_{Ay} = R_{By} = \frac{q_1 \cdot L}{2} = \frac{19.0 \, \text{kN/m} \cdot 7.1 \, \text{m}}{2} = 67.45 \, \text{kN} $$
**Reação Horizontal ($R_z$):**
$$ R_{Az} = R_{Bz} = \frac{q_2 \cdot L}{2} = \frac{36.0 \cdot 7.1 \, \text{m}}{2} = 127.80 \, \text{kN} $$
**Resultante no Apoio:**
$$ R_{apoio} = \sqrt{R_y^2 + R_z^2} = \sqrt{67.45^2 + 127.80^2} = 144.51 \, \text{kN} $$

- **Força Resultante em cada apoio: 144.51 kN**

---

## (b) Momento Máximo Resultante

O momento fletor máximo ocorre no centro do vão ($x = L/2$) para cada eixo.

**Posição:**
$$ x = \frac{L}{2} = \frac{7.1}{2} = 3.55 \, \text{m} $$

**Componentes do Momento Máximo:**
$$ M_{z,max} = \frac{q_1 \cdot L^2}{8} = \frac{19.0 \cdot 7.1^2}{8} = 119.72 \, \text{kN.m} $$
$$ M_{y,max} = \frac{q_2 \cdot L^2}{8} = \frac{36.0 \cdot 7.1^2}{8} = 226.84 \, \text{kN.m} $$

**Momento Resultante Máximo:**
$$ M_{res,max} = \sqrt{M_{z,max}^2 + M_{y,max}^2} = \sqrt{119.72^2 + 226.84^2} = 256.50 \, \text{kN.m} $$

---

## (c, d) Posição do Baricentro da Seção Composta

Homogeneizando a seção em aço ($n = E_{mad}/E_{aço} = 9.8182$), com origem no canto inferior esquerdo:

| Parte                 | Material | Área (A') (mm²) | y_i (mm) | z_i (mm) | A'y_i (mm³) | A'z_i (mm³) |
|-----------------------|----------|-----------------|----------|----------|-------------|-------------|
| Prancha Esq (Mad)     | mad      | 814909.09       | 207.50   | 100.00   | 1.7e+08     | 8.1e+07     |
| Alma (Aço)            | aco      | 5395.00         | 207.50   | 206.50   | 1.1e+06     | 1.1e+06     |
| Prancha Dir (Mad)     | mad      | 814909.09       | 207.50   | 313.00   | 1.7e+08     | 2.6e+08     |
| Mesa (Aço)            | aco      | 4732.00         | 421.50   | 206.50   | 2.0e+06     | 9.8e+05     |


$$ \bar{z} = \frac{\sum A'_i \cdot z_i}{\sum A'_i} = \frac{3.39e+08}{1.64e+06} = 206.50 \, \text{mm} $$
$$ \bar{y} = \frac{\sum A'_i \cdot y_i}{\sum A'_i} = \frac{3.41e+08}{1.64e+06} = 208.12 \, \text{mm} $$

- **Posição $\bar{z}$: 206.50 mm**
- **Posição $\bar{y}$: 208.12 mm**

---

## (e, f) Momentos de Inércia

Calculados com o Teorema dos Eixos Paralelos ($ I = I_c + A \cdot d^2 $).

**Cálculo de $I_{zg}$:**
| Parte                 | I_zc' (mm⁴) | A' (mm²) | d_y (mm) | A'd_y² (mm⁴) | I_zg (mm⁴) |
|-----------------------|-------------|----------|----------|--------------|------------|
| Prancha Esq (Mad)     | 1.17e+10    | 814909.09 | -0.62    | 3.11e+05     | 1.17e+10   |
| Alma (Aço)            | 7.74e+07    | 5395.00  | -0.62    | 2.06e+03     | 7.74e+07   |
| Prancha Dir (Mad)     | 1.17e+10    | 814909.09 | -0.62    | 3.11e+05     | 1.17e+10   |
| Mesa (Aço)            | 6.66e+04    | 4732.00  | 213.38   | 2.15e+08     | 2.16e+08   |

- **Momento de Inércia $I_{zg}$: 2.368e+10 mm⁴**

**Cálculo de $I_{yg}$:**
| Parte                 | I_yc' (mm⁴) | A' (mm²) | d_z (mm) | A'd_z² (mm⁴) | I_yg (mm⁴) |
|-----------------------|-------------|----------|----------|--------------|------------|
| Prancha Esq (Mad)     | 2.72e+09    | 814909.09 | -106.50  | 9.24e+09     | 1.20e+10   |
| Alma (Aço)            | 7.60e+04    | 5395.00  | 0.00     | 0.00e+00     | 7.60e+04   |
| Prancha Dir (Mad)     | 2.72e+09    | 814909.09 | 106.50   | 9.24e+09     | 1.20e+10   |
| Mesa (Aço)            | 5.22e+07    | 4732.00  | 0.00     | 0.00e+00     | 5.22e+07   |

- **Momento de Inércia $I_{yg}$:** 2.397e+10 mm⁴

---

## (g) Inclinação da Linha Neutra

$$ \tan(\phi) = \frac{M_y \cdot I_{zg}}{M_z \cdot I_{yg}} = \frac{2.268e+08 \cdot 2.368e+10}{1.197e+08 \cdot 2.397e+10} = 1.872 $$
- **Ângulo da Linha Neutra ($\phi$): 61.89°**

---

## (h, i) Tensões Máximas

$$ \sigma = -\frac{M_z \cdot y'}{I_{zg}} + \frac{M_y \cdot z'}{I_{yg}} $$

**Tensões no Aço:**
- **Tração Máxima:** Ocorre em `Alma Base Dir` (y'=-208.12, z'=6.50).
  $$ \sigma_{t,max} = -\frac{1.20e+08 \cdot (-208.12)}{2.37e+10} + \frac{2.27e+08 \cdot (6.50)}{2.40e+10} = **1.11 MPa** $$
- **Compressão Máxima:** Ocorre em `Mesa Topo Esq` (y'=219.88, z'=-182.00).
  $$ \sigma_{c,max} = -\frac{1.20e+08 \cdot (219.88)}{2.37e+10} + \frac{2.27e+08 \cdot (-182.00)}{2.40e+10} = **-2.83 MPa** $$

**Tensões na Madeira:**
- **Tração Máxima:** Ocorre em `Prancha Inf Dir` (y'=-208.12, z'=206.50).
  $$ \sigma_{t,max} = n \cdot \left( ... \right) = **29.52 MPa** $$
- **Compressão Máxima:** Ocorre em `Prancha Sup Esq` (y'=206.88, z'=-206.50).
  $$ \sigma_{c,max} = n \cdot \left( ... \right) = **-29.45 MPa** $$

---

## (j) Giro Relativo Entre os Apoios

$$ \theta = \frac{q_1 \cdot L^3}{24 \cdot E_{aço} \cdot I_{zg}} = \frac{(19000) \cdot (7.1)^3}{24 \cdot (1.10e+10) \cdot (2.37e-02)} $$
- **Giro no apoio:** 0.00109 rad (0.0623°)

---

## Visualizações Gráficas

### Seção Transversal e Linha Neutra
![Seção Transversal Corrigida](secao_transversal_corrigida.png)

### Vetores de Momento na Seção
![Vetores de Momento Atuantes](vetores_momento.png)