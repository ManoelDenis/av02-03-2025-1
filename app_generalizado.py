
# ========== Funções utilitárias para cabeçalho ==========
def load_header():
    if HEADER_PATH.is_file():
        with open(HEADER_PATH, encoding="utf-8") as f:
            return json.load(f)
    # Padrão inicial
    return {
        "titulo": "RESISTÊNCIA DOS MATERIAIS I - AVALIAÇÃO PERSONALIZADA",
        "subtitulo": "",
        "campos": [
            {"label": "Nome", "placeholder": ""},
            {"label": "Matrícula", "placeholder": ""}
        ]
    }

def save_header(header):
    with open(HEADER_PATH, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=2, ensure_ascii=False)

import streamlit as st
import json
import os
from pathlib import Path
import base64
import markdown
from datetime import datetime


CONFIG_DIR = Path("config")
IMAGES_DIR = CONFIG_DIR / "images"
IMG_DIMENSIONS_PATH = CONFIG_DIR / "img_dimensions.json"
MD_PATH = CONFIG_DIR / "avaliacao.md"
PARAMS_PATH = CONFIG_DIR / "parametros.json"
HEADER_PATH = CONFIG_DIR / "header.json"

# ========== Funções utilitárias ==========
def load_markdown():
    if MD_PATH.is_file():
        with open(MD_PATH, encoding="utf-8") as f:
            return f.read()
    return ""

def save_markdown(content):
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def load_params():
    if PARAMS_PATH.is_file():
        with open(PARAMS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_params(params):
    with open(PARAMS_PATH, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, ensure_ascii=False)

def save_image(uploaded_file):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    img_path = IMAGES_DIR / uploaded_file.name
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return img_path

def load_img_dimensions():
    if IMG_DIMENSIONS_PATH.is_file():
        with open(IMG_DIMENSIONS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_img_dimensions(dimensions):
    with open(IMG_DIMENSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(dimensions, f, indent=2, ensure_ascii=False)

def embed_images_in_markdown(md_content):
    import re
    img_dims = load_img_dimensions()
    def img_replacer(match):
        alt, path = match.groups()
        img_file = (CONFIG_DIR / path).resolve()
        if not img_file.is_file():
            img_file = (IMAGES_DIR / Path(path).name).resolve()
        style = "max-width:800px;width:100%;display:block;margin:32px auto;"
        # Aplica dimensões customizadas se existirem
        dims = img_dims.get(Path(path).name, {})
        if dims.get("width"): style += f"width:{dims['width']}px;max-width:100%;"
        if dims.get("height"): style += f"height:{dims['height']}px;"
        if img_file.is_file():
            with open(img_file, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            ext = img_file.suffix[1:] or "png"
            return f'<img src="data:image/{ext};base64,{img_b64}" alt="{alt}" style="{style}">' 
        return f'<em>[Imagem não encontrada: {path}]</em>'
    return re.sub(r'!\[(.*?)\]\((.*?)\)', img_replacer, md_content)

def markdown_to_html(md_content):
    md_content = embed_images_in_markdown(md_content)
    return markdown.markdown(md_content, extensions=['extra'])

# ========== Área do Professor ==========
def area_professor():
    st.header("Configuração da Avaliação (Professor)")
    senha = st.text_input("Senha de acesso", type="password")
    senha_padrao = "prof123"
    if senha != senha_padrao:
        st.info(f"Digite a senha para acessar a configuração. (Padrão: {senha_padrao})")
        return
    st.success("Acesso liberado!")
    # Sessão de configuração do cabeçalho (após senha)
    st.subheader("Configuração do Cabeçalho da Avaliação")
    header = load_header()
    titulo = st.text_input("Título principal da avaliação", value=header.get("titulo", ""), key="header_titulo")
    subtitulo = st.text_input("Subtítulo (opcional)", value=header.get("subtitulo", ""), key="header_subtitulo")
    # Usar session_state para manter campos temporários
    if 'campos_temp' not in st.session_state:
        st.session_state['campos_temp'] = header.get("campos", [])
    campos_temp = st.session_state['campos_temp']
    st.markdown("**Campos do cabeçalho:** (ex: Nome, Matrícula, Turma, etc.)")
    # Controle de remoção
    if 'remover_idx' not in st.session_state:
        st.session_state['remover_idx'] = None
    campos_editados = []
    n = len(campos_temp)
    for i in range(n):
        cols = st.columns([3,3,1])
        with cols[0]:
            label = st.text_input(f"Rótulo do campo {i+1}", value=campos_temp[i].get("label",""), key=f"header_label_{i}")
        with cols[1]:
            placeholder = st.text_input(f"Placeholder {i+1}", value=campos_temp[i].get("placeholder",""), key=f"header_placeholder_{i}")
        with cols[2]:
            if st.session_state['remover_idx'] == i:
                if st.button("Confirmar remoção", key=f"btn_confirma_remover_{i}"):
                    campos_temp.pop(i)
                    st.session_state['remover_idx'] = None
                    st.rerun()
                if st.button("Cancelar", key=f"btn_cancela_remover_{i}"):
                    st.session_state['remover_idx'] = None
                    st.rerun()
            else:
                if st.button("Remover", key=f"btn_remover_{i}"):
                    st.session_state['remover_idx'] = i
                    st.rerun()
        campos_editados.append({"label": label.strip(), "placeholder": placeholder.strip()})
    st.session_state['campos_temp'] = campos_temp = campos_editados
    if st.button("Adicionar campo ao cabeçalho"):
        campos_temp.append({"label": "", "placeholder": ""})
        st.session_state['remover_idx'] = None
        st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
    header_config = {"titulo": titulo, "subtitulo": subtitulo, "campos": campos_temp}
    # Markdown
    st.subheader("Enunciado (Markdown)")
    md_content = st.text_area("Conteúdo do enunciado em Markdown", load_markdown(), height=300)
    # Imagens
    st.subheader("Imagens para o enunciado")
    uploaded_imgs = st.file_uploader("Upload de imagens", accept_multiple_files=True, type=["png","jpg","jpeg","gif"])
    # Visualizar imagens já salvas e configurar dimensões
    img_files = list(IMAGES_DIR.glob("*")) if IMAGES_DIR.exists() else []
    img_dims = load_img_dimensions()
    if img_files:
        st.markdown("**Imagens já salvas:**")
        from PIL import Image
        for img in img_files:
            pil_img = Image.open(img)
            orig_w, orig_h = pil_img.size
            width_key = f"w_{img.name}"
            height_key = f"h_{img.name}"
            prop_key = f"prop_{img.name}"
            # Inicialização dos valores
            if width_key not in st.session_state:
                st.session_state[width_key] = img_dims.get(img.name, {}).get("width", orig_w)
            if height_key not in st.session_state:
                st.session_state[height_key] = img_dims.get(img.name, {}).get("height", orig_h)
            if prop_key not in st.session_state:
                st.session_state[prop_key] = True

            def update_height(img_name=img.name, orig_w=orig_w, orig_h=orig_h):
                width = st.session_state[f"w_{img_name}"]
                if width > 0:
                    st.session_state[f"h_{img_name}"] = int(width * orig_h / orig_w)

            def update_width(img_name=img.name, orig_w=orig_w, orig_h=orig_h):
                height = st.session_state[f"h_{img_name}"]
                if height > 0:
                    st.session_state[f"w_{img_name}"] = int(height * orig_w / orig_h)

            # Mostra imagem com tamanho configurado em tempo real usando HTML
            width = st.session_state[width_key]
            height = st.session_state[height_key]
            with open(img, "rb") as f:
                img_bytes = f.read()
            import base64
            img_b64 = base64.b64encode(img_bytes).decode()
            ext = img.suffix[1:] or "png"
            style = "display:block;margin:12px 0;"
            if width > 0:
                style += f"width:{width}px;"
            if height > 0:
                style += f"height:{height}px;"
            html_img = f'<img src="data:image/{ext};base64,{img_b64}" alt="{img.name}" style="{style}"><div style="text-align:center;font-size:0.95em;color:#888">{img.name}</div>'
            st.markdown(html_img, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                manter_prop = st.checkbox("Manter proporção", key=prop_key)
            with col2:
                if manter_prop:
                    if width_key in st.session_state:
                        width = st.number_input(f"Largura (px) - {img.name}", min_value=0, max_value=2000, key=width_key, on_change=update_height)
                    else:
                        width = st.number_input(f"Largura (px) - {img.name}", min_value=0, max_value=2000, value=img_dims.get(img.name, {}).get("width", orig_w), key=width_key, on_change=update_height)
                else:
                    if width_key in st.session_state:
                        width = st.number_input(f"Largura (px) - {img.name}", min_value=0, max_value=2000, key=width_key)
                    else:
                        width = st.number_input(f"Largura (px) - {img.name}", min_value=0, max_value=2000, value=img_dims.get(img.name, {}).get("width", orig_w), key=width_key)
            with col3:
                if manter_prop:
                    if height_key in st.session_state:
                        height = st.number_input(f"Altura (px) - {img.name}", min_value=0, max_value=2000, key=height_key, on_change=update_width)
                    else:
                        height = st.number_input(f"Altura (px) - {img.name}", min_value=0, max_value=2000, value=img_dims.get(img.name, {}).get("height", orig_h), key=height_key, on_change=update_width)
                else:
                    if height_key in st.session_state:
                        height = st.number_input(f"Altura (px) - {img.name}", min_value=0, max_value=2000, key=height_key)
                    else:
                        height = st.number_input(f"Altura (px) - {img.name}", min_value=0, max_value=2000, value=img_dims.get(img.name, {}).get("height", orig_h), key=height_key)
            # Atualiza dimensões no dicionário
            width = st.session_state[width_key]
            height = st.session_state[height_key]
            if width > 0 or height > 0:
                img_dims[img.name] = {"width": width if width > 0 else None, "height": height if height > 0 else None}
            elif img.name in img_dims:
                del img_dims[img.name]
    # Parâmetros
    st.subheader("Parâmetros Aleatórios (JSON)")
    params_str = st.text_area("Edite o JSON dos parâmetros", json.dumps(load_params(), indent=2, ensure_ascii=False), height=250)
    # Botão único de salvar tudo
    if st.button("Salvar Tudo"):
        # Salva cabeçalho
        save_header(header_config)
        # Salva enunciado
        save_markdown(md_content)
        # Salva imagens
        if uploaded_imgs:
            for img in uploaded_imgs:
                save_image(img)
        # Salva parâmetros
        try:
            params = json.loads(params_str)
            save_params(params)
            # Salva dimensões das imagens
            save_img_dimensions(img_dims)
            st.success("Cabeçalho, enunciado, imagens, parâmetros e dimensões salvos!")
        except Exception as e:
            st.error(f"Erro ao salvar parâmetros (JSON): {e}")
    st.info("Ao salvar, a avaliação ativa será atualizada para os alunos.")

# ========== Área do Aluno ==========
def gerar_parametros(params, seed):
    import numpy as np
    np.random.seed(seed)
    resultado = {}
    for nome, cfg in params.items():
        if cfg["decimais"] == 0:
            val = np.random.randint(cfg["min"], cfg["max"]+1)
        else:
            val = np.round(np.random.uniform(cfg["min"], cfg["max"]), cfg["decimais"])
        resultado[nome] = val
    return resultado

def area_aluno():
    st.header("Geração de Avaliação Personalizada")
    md_content = load_markdown()
    params = load_params()
    header = load_header()
    if not md_content or not params:
        st.warning("Nenhuma avaliação publicada pelo professor.")
        return
    seed_input = st.text_input("Digite os dois últimos dígitos da matrícula (0-99):", max_chars=2)
    if st.button("Gerar Avaliação"):
        if seed_input and seed_input.isdigit():
            seed = int(seed_input)
            if 0 <= seed <= 99:
                param_vals = gerar_parametros(params, seed)
                # Monta tabela de parâmetros
                tabela = "<table><tr><th>Parâmetro</th><th>Valor</th><th>Unidade</th></tr>"
                for nome, cfg in params.items():
                    val = param_vals[nome]
                    val_str = f"{val:.{cfg['decimais']}f}".replace('.', ',') if cfg['decimais'] > 0 else str(int(val))
                    tabela += f"<tr><td>{nome}</td><td>{val_str}</td><td>{cfg['unidade']}</td></tr>"
                tabela += "</table>"
                # Monta campos do cabeçalho
                campos = header.get("campos", [])
                campos_html = "<div style='display:flex;flex-wrap:wrap;width:100%;gap:0 0;'>"
                n_campos = len(campos)
                for i in range(0, n_campos, 2):
                    campos_html += "<div style='display:flex;width:100%;margin-bottom:16px;'>"
                    # Primeira coluna
                    if i < n_campos:
                        campo = campos[i]
                        label = campo.get("label", "")
                        placeholder = campo.get("placeholder", "")
                        campos_html += f"<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                        campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                        campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                        campos_html += "</div>"
                    # Segunda coluna
                    if i+1 < n_campos:
                        campo = campos[i+1]
                        label = campo.get("label", "")
                        placeholder = campo.get("placeholder", "")
                        campos_html += f"<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                        campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                        campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                        campos_html += "</div>"
                    campos_html += "</div>"
                campos_html += "</div>"
                # Gera HTML final
                html = f"""
                <!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>
                <title>Avaliação Personalizada</title>
                <style>body{{background:#f5f6fa;}} .container{{max-width:800px;margin:40px auto;padding:32px 32px 24px 32px;background:#fff;border-radius:14px;box-shadow:0 2px 12px #0001;border:1px solid #e0e0e0;}} h2,h3{{text-align:center;}} h2{{color:#2c3e50;}} .enunciado-justificado{{ text-align:justify; }} table{{border-collapse:collapse;width:100%;margin-top:20px;margin-bottom:20px;box-shadow:0 2px 3px rgba(0,0,0,0.07);}} th,td{{border:1px solid #bdc3c7;text-align:left;padding:10px;}} th{{background-color:#3498db;color:white;text-align:center;}} tr:nth-child(even){{background-color:#ecf0f1;}} td:nth-child(2),td:nth-child(3){{text-align:right;}} .ident-aluno{{margin:0 0 30px 0;padding:10px 0 18px 0;border-bottom:1px solid #e0e0e0;display:flex;flex-wrap:wrap;align-items:center;}} .ident-aluno label{{font-weight:bold;display:inline-block;width:90px;}} .ident-aluno input{{border:none;border-bottom:1px solid #aaa;background:transparent;width:180px;font-size:1em;margin-right:30px;}} .ident-aluno .data{{margin-left:auto;color:#888;font-size:0.98em;margin-top:8px;}} </style></head><body><div class='container'>
                <h2 style='margin-bottom:0.2em'>{header.get('titulo','')}</h2>
                {f"<div style='text-align:center;font-size:1.25em;color:#2c3e50;margin-bottom:0.7em'>{header.get('subtitulo','')}</div>" if header.get('subtitulo','') else ''}
                <div class='ident-aluno'>
                {campos_html}
                <span class='data'>Data/hora da geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
                </div>
                <h3>Enunciado</h3>
                <div class='enunciado-justificado'>{markdown_to_html(md_content)}</div>
                <hr><h3>Parâmetros Gerados</h3>{tabela}
                <hr><p style='color:#888'>Arquivo gerado automaticamente para uso didático.</p></div></body></html>
                """
                file_name = f"Avaliacao_Personalizada_Seed_{seed}.html"
                st.success(f"Avaliação gerada para seed {seed}!")
                st.download_button(
                    label="⬇️ Baixar Arquivo HTML da Avaliação",
                    data=html,
                    file_name=file_name,
                    mime="text/html"
                )
            else:
                st.warning("Digite um número entre 0 e 99.")
        else:
            st.warning("Digite um número válido para o seed.")

# ========== Página principal ==========
st.set_page_config(page_title="Gerador de Avaliação Generalizado", layout="centered")
menu = st.sidebar.radio("Selecione o modo:", ["Aluno", "Professor (Configuração)"])
if menu == "Professor (Configuração)":
    area_professor()
else:
    area_aluno()

st.markdown("---")
st.markdown("Desenvolvido para fins didáticos - Prof. Manoel Dênis Costa Ferreira")
