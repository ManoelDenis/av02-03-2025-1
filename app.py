import streamlit as st
import numpy as np
import base64

from pathlib import Path
import markdown

# Função para formatar números com vírgula decimal
def format_decimal_with_comma(number, precision=1):
    return f"{number:.{precision}f}".replace('.', ',')

def format_int_with_comma(number):
    return str(int(round(number)))

# Função para gerar os parâmetros aleatórios
def gerar_parametros(seed):
    np.random.seed(seed)
    L = np.random.uniform(4, 8)  # m, 1 casa decimal
    d1 = np.random.randint(100, 201)  # mm
    d2 = np.random.randint(400, 601)  # mm
    d3 = np.random.randint(300, 501)  # mm
    t = np.random.randint(12, 26)     # mm
    q1 = np.random.randint(10, 21)    # kN/m
    q2 = np.random.randint(20, 41)    # kN/m
    Ea = np.random.randint(10, 21)    # GPa
    Em = np.random.randint(100, 201)  # GPa
    return {
        'L': L,
        'd1': d1,
        'd2': d2,
        'd3': d3,
        't': t,
        'q1': q1,
        'q2': q2,
        'Ea': Ea,
        'Em': Em
    }


# Função para ler e converter o enunciado do markdown para HTML
ENUNCIADO_PATH = Path("arquivos/RMI-PP02-II-2025-1.md")
def ler_enunciado_html():
    if ENUNCIADO_PATH.is_file():
        with open(ENUNCIADO_PATH, encoding="utf-8") as f:
            md_content = f.read()
        # Substitui o link da imagem por uma imagem embutida em base64
        import re
        img_path = Path("images/f01_secao.png")
        if img_path.is_file():
            with open(img_path, "rb") as img_file:
                img_b64 = base64.b64encode(img_file.read()).decode()
            # Dobrar o tamanho: max-width:800px
            img_tag = f'<img src="data:image/png;base64,{img_b64}" alt="Seção em T" style="max-width:800px;width:100%;display:block;margin:32px auto;">'
            # Substitui a linha do markdown da imagem por img_tag
            md_content = re.sub(r'!\[.*?\]\([^)]+\)', img_tag, md_content)
        else:
            md_content = md_content.replace("![](../images/f01_secao.png)", "<em>[Figura não encontrada]</em>")
        # Converte markdown para HTML
        html = markdown.markdown(md_content, extensions=['extra'])
        return html
    return "<p>[Arquivo de enunciado não encontrado.]</p>"

# Função para gerar o HTML da avaliação


def gerar_html(seed, parametros, enunciado_html):
    from datetime import datetime
    datahora = datetime.now().strftime('%d/%m/%Y %H:%M')
    html = [
        "<!DOCTYPE html>",
        "<html lang='pt-BR'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<title>Avaliação ResMat - Seed {}</title>".format(seed),
        "<style>body{background:#f5f6fa;} .container{max-width:800px;margin:40px auto;padding:32px 32px 24px 32px;background:#fff;border-radius:14px;box-shadow:0 2px 12px #0001;border:1px solid #e0e0e0;} h2,h3{text-align:center;} h2{color:#2c3e50;} .enunciado-justificado{ text-align:justify; } table{border-collapse:collapse;width:100%;margin-top:20px;margin-bottom:20px;box-shadow:0 2px 3px rgba(0,0,0,0.07);} th,td{border:1px solid #bdc3c7;text-align:left;padding:10px;} th{background-color:#3498db;color:white;text-align:center;} tr:nth-child(even){background-color:#ecf0f1;} td:nth-child(2),td:nth-child(3){text-align:right;} .header-info{margin-bottom:15px;} .header-info strong{display:inline-block;min-width:250px;} .questions li{margin-bottom:10px;} hr{border:0;height:1px;background-color:#ccc;margin:30px 0;} img{max-width:800px;width:100%;display:block;margin:32px auto;} .ident-aluno{margin:0 0 30px 0;padding:10px 0 18px 0;border-bottom:1px solid #e0e0e0;display:flex;flex-wrap:wrap;align-items:center;} .ident-aluno label{font-weight:bold;display:inline-block;width:90px;} .ident-aluno input{border:none;border-bottom:1px solid #aaa;background:transparent;width:180px;font-size:1em;margin-right:30px;} .ident-aluno .data{margin-left:auto;color:#888;font-size:0.98em;margin-top:8px;} </style>",
        "</head>",
        "<body>",
        "<div class='container'>",
        "<h2>RESISTÊNCIA DOS MATERIAIS I - AVALIAÇÃO 02 - PARTE III (Peso 2)</h2>",
        f"<p style='text-align:center'><strong>Seed (dois últimos dígitos da matrícula):</strong> {seed}</p>",
        "<div class='ident-aluno'>",
        "<label>Nome:</label> <input type='text' maxlength='40'>",
        f"<span class='data'>Data/hora da geração: {datahora}</span>",
        "</div>",
        "<h2>Enunciado</h2>",
        f"<div class='enunciado-justificado'>{enunciado_html}</div>",
        "<hr>",
        "<h2>Parâmetros Gerados</h2>",
        "<table>",
        "<tr><th>Parâmetro</th><th>Valor</th><th>Unidade</th></tr>",
        f"<tr><td>L</td><td>{format_decimal_with_comma(parametros['L'],1)}</td><td>m</td></tr>",
        f"<tr><td>d1</td><td>{format_int_with_comma(parametros['d1'])}</td><td>mm</td></tr>",
        f"<tr><td>d2</td><td>{format_int_with_comma(parametros['d2'])}</td><td>mm</td></tr>",
        f"<tr><td>d3</td><td>{format_int_with_comma(parametros['d3'])}</td><td>mm</td></tr>",
        f"<tr><td>t</td><td>{format_int_with_comma(parametros['t'])}</td><td>mm</td></tr>",
        f"<tr><td>q1</td><td>{format_int_with_comma(parametros['q1'])}</td><td>kN/m</td></tr>",
        f"<tr><td>q2</td><td>{format_int_with_comma(parametros['q2'])}</td><td>kN/m</td></tr>",
        f"<tr><td>E<sub>aço</sub></td><td>{format_int_with_comma(parametros['Ea'])}</td><td>GPa</td></tr>",
        f"<tr><td>E<sub>mad</sub></td><td>{format_int_with_comma(parametros['Em'])}</td><td>GPa</td></tr>",
        "</table>",
        "<hr>",
        "<p style='color:#888'>Arquivo gerado automaticamente para uso didático.</p>",
        "</div>",
        "</body></html>"
    ]
    return "\n".join(html)

# Interface Streamlit
st.set_page_config(page_title="Gerador de Avaliação RMI", layout="centered")
st.title("📝 Gerador Automático de Avaliação - RMI")
st.write("Preencha os dois últimos dígitos da matrícula para gerar sua avaliação personalizada.")


seed_input = st.text_input("Digite os dois últimos dígitos da matrícula (0-99):", max_chars=2)
enunciado_html = ler_enunciado_html()

if st.button("Gerar Avaliação"):
    if seed_input and seed_input.isdigit():
        seed = int(seed_input)
        if 0 <= seed <= 99:
            parametros = gerar_parametros(seed)
            html_content = gerar_html(seed, parametros, enunciado_html)
            file_name = f"Avaliacao_RMI_Seed_{seed}.html"
            b64 = base64.b64encode(html_content.encode()).decode()
            st.success(f"Avaliação gerada para seed {seed}!")
            st.download_button(
                label="⬇️ Baixar Arquivo HTML da Avaliação",
                data=html_content,
                file_name=file_name,
                mime="text/html"
            )
        else:
            st.warning("Digite um número entre 0 e 99.")
    else:
        st.warning("Digite um número válido para o seed.")

st.markdown("---")
st.markdown("Desenvolvido para fins didáticos - RMI - UEL")
