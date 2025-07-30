# ========== IMPORTS ========== 

from dotenv import load_dotenv
from google.cloud import firestore
import google.auth.exceptions
import streamlit as st
from streamlit_sortables import sort_items
import json
from pathlib import Path
import base64
import markdown
from datetime import datetime

# Deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="Gerador de Avaliação Generalizado", layout="centered")


# Carrega variáveis de ambiente do .env
load_dotenv()

# DEBUG: Mostra o valor da variável de ambiente de credenciais
import os
cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
# st.info(f"GOOGLE_APPLICATION_CREDENTIALS = {cred_path}")

# ========== Firestore utilitários e persistência ========== 

def get_firestore_client():
    try:
        return firestore.Client()
    except google.auth.exceptions.DefaultCredentialsError:
        st.warning("Firestore não configurado corretamente. Usando armazenamento local.")
        return None

def save_firestore(collection, doc_id, data):
    db = get_firestore_client()
    if db:
        db.collection(collection).document(doc_id).set(data)

def load_firestore(collection, doc_id, default=None):
    db = get_firestore_client()
    if db:
        doc = db.collection(collection).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
    return default

def load_header():
    default = {
        "titulo": "RESISTÊNCIA DOS MATERIAIS I - AVALIAÇÃO PERSONALIZADA",
        "subtitulo": "",
        "campos": [
            {"label": "Nome", "placeholder": ""},
            {"label": "Matrícula", "placeholder": ""}
        ]
    }
    header = load_firestore("avaliacao", "header", default=None)
    if header:
        return header
    if HEADER_PATH.is_file():
        with open(HEADER_PATH, encoding="utf-8") as f:
            return json.load(f)
    return default

def save_header(header):
    save_firestore("avaliacao", "header", header)
    with open(HEADER_PATH, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=2, ensure_ascii=False)

def load_markdown():
    md = load_firestore("avaliacao", "markdown", default=None)
    if md is not None:
        return md.get("content", "")
    if MD_PATH.is_file():
        with open(MD_PATH, encoding="utf-8") as f:
            return f.read()
    return ""

def save_markdown(content):
    save_firestore("avaliacao", "markdown", {"content": content})
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def load_params():
    params_data = load_firestore("avaliacao", "params", default=None)
    if params_data:
        # Se for o novo formato, retorna dict com ordem e dados
        if isinstance(params_data, dict) and "ordem" in params_data and "dados" in params_data:
            return params_data
        # Compatibilidade retroativa: só dict de params
        return {"ordem": list(params_data.keys()), "dados": params_data}
    if PARAMS_PATH.is_file():
        with open(PARAMS_PATH, encoding="utf-8") as f:
            params_data = json.load(f)
            if isinstance(params_data, dict) and "ordem" in params_data and "dados" in params_data:
                return params_data
            return {"ordem": list(params_data.keys()), "dados": params_data}
    return {"ordem": [], "dados": {}}

def save_params(params):
    save_firestore("avaliacao", "params", params)
    with open(PARAMS_PATH, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, ensure_ascii=False)




CONFIG_DIR = Path("config")
IMAGES_DIR = CONFIG_DIR / "images"
IMG_DIMENSIONS_PATH = CONFIG_DIR / "img_dimensions.json"
MD_PATH = CONFIG_DIR / "avaliacao.md"
PARAMS_PATH = CONFIG_DIR / "parametros.json"
HEADER_PATH = CONFIG_DIR / "header.json"

# ========== Funções utilitárias ==========


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
        if dims.get("width"):
            style += f"width:{dims['width']}px;max-width:100%;"
        if dims.get("height"):
            style += f"height:{dims['height']}px;"
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
    st.header("Área do Professor")
    senha = st.text_input("Senha de acesso", type="password")
    senha_padrao = "prof123"
    if senha != senha_padrao:
        st.info(f"Digite a senha para acessar as funcionalidades do modo professor.")
        return
    st.success("Acesso liberado!")
    st.markdown("---")
    pagina_prof = st.radio("Selecione a funcionalidade:", ["Geração de Avaliações em Lote", "Configuração da Avaliação"], key="prof_pagina")

    if pagina_prof == "Geração de Avaliações em Lote":
        st.header("Gerar conjunto de avaliações para vários seeds")
        seed_ini = st.number_input("Seed inicial", min_value=0, max_value=99, value=0, key="prof_seed_ini")
        seed_fim = st.number_input("Seed final", min_value=0, max_value=99, value=10, key="prof_seed_fim")
        gerar_lote = st.button("Gerar Conjunto de Avaliações", key="prof_btn_gerar_lote")

        def gerar_html_avaliacao(seed):
            param_vals = gerar_parametros(load_params().get('dados', {}), seed)
            katex_header = """
            <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'>
            <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'></script>
            <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js' onload="renderMathInElement(document.body, {delimiters: [{left: '$', right: '$', display: false}]});"></script>
            """
            param_order = load_params().get('ordem', [])
            params = load_params().get('dados', {})
            header = load_header()
            md_content = load_markdown()
            tabela = katex_header + "<table><tr><th>Parâmetro</th><th>Valor</th><th>Unidade</th></tr>"
            for nome in param_order:
                cfg = params[nome]
                val = param_vals[nome]
                val_str = f"{val:.{cfg['decimais']}f}".replace('.', ',') if cfg['decimais'] > 0 else str(int(val))
                tabela += f"<tr><td>$ {nome} $</td><td>{val_str}</td><td>{cfg['unidade']}</td></tr>"
            tabela += "</table>"
            campos = header.get("campos", [])
            campos_html = "<div style='display:flex;flex-wrap:wrap;width:100%;gap:0 0;'>"
            n_campos = len(campos)
            for i in range(0, n_campos, 2):
                campos_html += "<div style='display:flex;width:100%;margin-bottom:16px;'>"
                if i < n_campos:
                    campo = campos[i]
                    label = campo.get("label", "")
                    placeholder = campo.get("placeholder", "")
                    campos_html += "<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                    campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                    campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                    campos_html += "</div>"
                if i+1 < n_campos:
                    campo = campos[i+1]
                    label = campo.get("label", "")
                    placeholder = campo.get("placeholder", "")
                    campos_html += "<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                    campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                    campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                    campos_html += "</div>"
                campos_html += "</div>"
            campos_html += "</div>"
            html = f"""
            <!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>
            <title>Avaliação Personalizada</title>
            <style>body{{background:#f5f6fa;}} .container{{max-width:800px;margin:40px auto;padding:32px 32px 24px 32px;background:#fff;border-radius:14px;box-shadow:0 2px 12px #0001;border:1px solid #e0e0e0;}} h2,h3{{text-align:center;}} h2{{color:#2c3e50;}} .enunciado-justificado{{ text-align:justify; }} table{{border-collapse:collapse;width:100%;margin-top:20px;margin-bottom:20px;box-shadow:0 2px 3px rgba(0,0,0,0.07);}} th,td{{border:1px solid #bdc3c7;text-align:left;padding:10px;}} th{{background-color:#3498db;color:white;text-align:center;}} tr:nth-child(even){{background-color:#ecf0f1;}} td:nth-child(2),td:nth-child(3){{text-align:right;}} .ident-aluno{{margin:0 0 30px 0;padding:10px 0 18px 0;border-bottom:1px solid #e0e0e0;display:flex;flex-wrap:wrap;align-items:center;}} .ident-aluno label{{font-weight:bold;display:inline-block;width:90px;}} .ident-aluno input{{border:none;border-bottom:1px solid #aaa;background:transparent;width:180px;font-size:1em;margin-right:30px;}} .ident-aluno .data{{margin-left:auto;color:#888;font-size:0.98em;margin-top:8px;}} </style></head><body><div class='container'>
            <h2 style='margin-bottom:0.2em'>{header.get('titulo','')}</h2>
            {f"<div style='text-align:center;font-size:1.25em;color:#2c3e50;margin-bottom:0.7em'>{header.get('subtitulo','')}</div>" if header.get('subtitulo','') else ''}
            <div class='ident-aluno'>
            {campos_html}
            </div>
            <h3>Enunciado</h3>
            <div class='enunciado-justificado'>{markdown_to_html(md_content)}</div>
            <hr><h3>Parâmetros Gerados</h3>{tabela}
            <hr><div style='display:flex;justify-content:space-between;color:#888;font-size:0.98em;'>
              <span>Arquivo gerado automaticamente para uso didático. <strong>Seed:</strong> {seed}</span>
              <span>Data/hora da geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
            </div></div></body></html>
            """
            return html

        if gerar_lote:
            import io
            import zipfile
            if seed_fim < seed_ini:
                st.warning("Seed final deve ser maior ou igual ao inicial.")
            else:
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w") as zipf:
                    for seed in range(seed_ini, seed_fim+1):
                        html = gerar_html_avaliacao(seed)
                        file_name = f"Avaliacao_Personalizada_Seed_{seed}.html"
                        zipf.writestr(file_name, html)
                buffer.seek(0)
                st.success(f"Conjunto de avaliações gerado para seeds {seed_ini} a {seed_fim}!")
                st.download_button(
                    label="⬇️ Baixar ZIP com avaliações",
                    data=buffer,
                    file_name=f"Avaliacoes_Seeds_{seed_ini}_a_{seed_fim}.zip",
                    mime="application/zip"
                )

    elif pagina_prof == "Configuração da Avaliação":
        # ...toda a lógica de configuração da avaliação...
        st.header("Configuração da Avaliação (Professor)")
        header = load_header()
        titulo = st.text_input("Título principal da avaliação", value=header.get("titulo", ""), key="header_titulo")
        subtitulo = st.text_input("Subtítulo (opcional)", value=header.get("subtitulo", ""), key="header_subtitulo")
        if 'campos_temp' not in st.session_state:
            st.session_state['campos_temp'] = header.get("campos", [])
        campos_temp = st.session_state['campos_temp']
        st.markdown("**Campos do cabeçalho:** (ex: Nome, Matrícula, Turma, etc.)")
        if 'remover_idx' not in st.session_state:
            st.session_state['remover_idx'] = None
        campos_editados = []
        n = len(campos_temp)
        for i in range(n):
            cols = st.columns([3,3,1])
            with cols[0]:
                label = st.text_input("Rótulo", value=campos_temp[i].get("label",""), key=f"header_label_{i}")
            with cols[1]:
                placeholder = st.text_input("Placeholder", value=campos_temp[i].get("placeholder",""), key=f"header_placeholder_{i}")
            with cols[2]:
                st.markdown("<div style='height: 1.9em'></div>", unsafe_allow_html=True)
                if st.session_state['remover_idx'] == i:
                    if st.button("✅", key=f"btn_confirma_remover_{i}", help="Confirmar remoção"):
                        campos_temp.pop(i)
                        st.session_state['remover_idx'] = None
                        st.rerun()
                    if st.button("❌", key=f"btn_cancela_remover_{i}", help="Cancelar remoção"):
                        st.session_state['remover_idx'] = None
                        st.rerun()
                else:
                    if st.button("🗑️", key=f"btn_remover_{i}", help="Remover campo"):
                        st.session_state['remover_idx'] = i
                        st.rerun()
            campos_editados.append({"label": label.strip(), "placeholder": placeholder.strip()})
        st.session_state['campos_temp'] = campos_temp = campos_editados
        if st.button("Adicionar campo ao cabeçalho"):
            campos_temp.append({"label": "", "placeholder": ""})
            st.session_state['remover_idx'] = None
            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
        header_config = {"titulo": titulo, "subtitulo": subtitulo, "campos": campos_temp}
        st.subheader("Enunciado (Markdown)")
        md_content = st.text_area("Conteúdo do enunciado em Markdown", load_markdown(), height=300)
        st.subheader("Imagens para o enunciado")
        uploaded_imgs = st.file_uploader("Upload de imagens", accept_multiple_files=True, type=["png","jpg","jpeg","gif"])
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
                width = st.session_state[width_key]
                height = st.session_state[height_key]
                if width > 0 or height > 0:
                    img_dims[img.name] = {"width": width if width > 0 else None, "height": height if height > 0 else None}
                elif img.name in img_dims:
                    del img_dims[img.name]
        st.subheader("Parâmetros Aleatórios")
        if 'parametros_temp' not in st.session_state or 'param_order' not in st.session_state:
            params_struct = load_params()
            param_order = params_struct.get('ordem', [])
            params_dict = params_struct.get('dados', {})
            param_order = [k for k in param_order if k in params_dict]
            for k in params_dict:
                if k not in param_order:
                    param_order.append(k)
            st.session_state['param_order'] = param_order
            st.session_state['parametros_temp'] = [
                {'nome': k, **params_dict[k]} for k in param_order
            ]
        parametros_temp = st.session_state['parametros_temp']
        param_order = st.session_state['param_order']
        st.markdown("---")
        show_sort_list = st.toggle(
            label="🔀 Ordenar parâmetros (arraste para reordenar)",
            value=st.session_state.get('show_sort_list', False),
            key="toggle_sort_list_btn",
            help="Mostrar/ocultar lista de ordenação"
        )
        if show_sort_list:
            param_names = [p['nome'] for p in parametros_temp if p['nome']]
            if param_names:
                sorted_names = sort_items(param_names, direction="vertical", key="sortable_param_list")
                if sorted_names != param_names:
                    idx_map = [param_names.index(n) for n in sorted_names]
                    parametros_temp = [parametros_temp[i] for i in idx_map]
                    param_order = [param_order[i] for i in idx_map]
                    st.session_state['parametros_temp'] = parametros_temp
                    st.session_state['param_order'] = param_order
            else:
                st.info("Adicione parâmetros para poder ordená-los.")
        for i, param in enumerate(parametros_temp):
            with st.expander(f"{param['nome']} | {param['min']} - {param['max']} {param['unidade']} ({param['decimais']} decimais)", expanded=True):
                cols = st.columns([2,2,2,2,2,1])
                with cols[0]:
                    nome = st.text_input("Nome", value=param.get('nome',''), key=f"param_nome_{i}")
                casas_decimais = param.get('decimais', 0)
                formato = f"%.{casas_decimais}f"
                passo = 10**-casas_decimais if casas_decimais > 0 else 1.0
                with cols[1]:
                    minv = st.number_input("Mínimo", value=float(param.get('min',0)), key=f"param_min_{i}", step=passo, format=formato)
                with cols[2]:
                    maxv = st.number_input("Máximo", value=float(param.get('max',0)), key=f"param_max_{i}", step=passo, format=formato)
                with cols[3]:
                    decimais = st.number_input("Decimais", value=param.get('decimais',0), key=f"param_dec_{i}", min_value=0, max_value=6, step=1)
                with cols[4]:
                    unidade = st.text_input("Unidade", value=param.get('unidade',''), key=f"param_uni_{i}")
                with cols[5]:
                    st.markdown("<div style='height: 1.9em'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"btn_remover_param_{i}", help="Remover parâmetro"):
                        parametros_temp.pop(i)
                        param_order.pop(i)
                        st.session_state['parametros_temp'] = parametros_temp
                        st.session_state['param_order'] = param_order
                        st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
                parametros_temp[i] = {
                    'nome': nome.strip(),
                    'min': minv,
                    'max': maxv,
                    'decimais': decimais,
                    'unidade': unidade.strip()
                }
                param_order[i] = nome.strip()
        if st.button("Adicionar parâmetro"):
            parametros_temp.append({'nome': '', 'min': 0, 'max': 0, 'decimais': 0, 'unidade': ''})
            param_order.append('')
            st.session_state['parametros_temp'] = parametros_temp
            st.session_state['param_order'] = param_order
            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
        if st.button("Salvar Tudo"):
            save_header(header_config)
            save_markdown(md_content)
            if uploaded_imgs:
                for img in uploaded_imgs:
                    save_image(img)
            try:
                params_dict = {p['nome']: {
                    'min': p['min'],
                    'max': p['max'],
                    'decimais': p['decimais'],
                    'unidade': p['unidade']
                } for p in parametros_temp if p['nome']}
                param_order_clean = [n for n in param_order if n in params_dict]
                save_params({'ordem': param_order_clean, 'dados': params_dict})
                save_img_dimensions(img_dims)
                st.success("Cabeçalho, enunciado, imagens, parâmetros e dimensões salvos!")
            except Exception as e:
                st.error(f"Erro ao salvar parâmetros: {e}")
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
    params_struct = load_params()
    header = load_header()
    param_order = params_struct.get('ordem', [])
    params = params_struct.get('dados', {})
    if not md_content or not params:
        st.warning("Nenhuma avaliação publicada pelo professor.")
        return
    seed_input = st.text_input("Digite os dois últimos dígitos da matrícula (0-99):", max_chars=2)
    gerar_individual = st.button("Gerar Avaliação", key="btn_gerar_individual")

    def gerar_html_avaliacao(seed):
        param_vals = gerar_parametros(params, seed)
        katex_header = """
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'>
        <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'></script>
        <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js' onload="renderMathInElement(document.body, {delimiters: [{left: '$', right: '$', display: false}]});"></script>
        """
        tabela = katex_header + "<table><tr><th>Parâmetro</th><th>Valor</th><th>Unidade</th></tr>"
        for nome in param_order:
            cfg = params[nome]
            val = param_vals[nome]
            val_str = f"{val:.{cfg['decimais']}f}".replace('.', ',') if cfg['decimais'] > 0 else str(int(val))
            tabela += f"<tr><td>$ {nome} $</td><td>{val_str}</td><td>{cfg['unidade']}</td></tr>"
        tabela += "</table>"
        campos = header.get("campos", [])
        campos_html = "<div style='display:flex;flex-wrap:wrap;width:100%;gap:0 0;'>"
        n_campos = len(campos)
        for i in range(0, n_campos, 2):
            campos_html += "<div style='display:flex;width:100%;margin-bottom:16px;'>"
            if i < n_campos:
                campo = campos[i]
                label = campo.get("label", "")
                placeholder = campo.get("placeholder", "")
                campos_html += "<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                campos_html += "</div>"
            if i+1 < n_campos:
                campo = campos[i+1]
                label = campo.get("label", "")
                placeholder = campo.get("placeholder", "")
                campos_html += "<div style='flex:1;display:flex;align-items:center;justify-content:center;'>"
                campos_html += f"<label style='font-weight:bold;display:inline-block;width:auto;margin-right:8px'>{label}:</label> "
                campos_html += f"<input type='text' placeholder='{placeholder}' maxlength='40' style='border:none;border-bottom:1px solid #aaa;background:transparent;width:70%;font-size:1em;margin-right:0px;text-align:center;'>"
                campos_html += "</div>"
            campos_html += "</div>"
        campos_html += "</div>"
        html = f"""
        <!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>
        <title>Avaliação Personalizada</title>
        <style>body{{background:#f5f6fa;}} .container{{max-width:800px;margin:40px auto;padding:32px 32px 24px 32px;background:#fff;border-radius:14px;box-shadow:0 2px 12px #0001;border:1px solid #e0e0e0;}} h2,h3{{text-align:center;}} h2{{color:#2c3e50;}} .enunciado-justificado{{ text-align:justify; }} table{{border-collapse:collapse;width:100%;margin-top:20px;margin-bottom:20px;box-shadow:0 2px 3px rgba(0,0,0,0.07);}} th,td{{border:1px solid #bdc3c7;text-align:left;padding:10px;}} th{{background-color:#3498db;color:white;text-align:center;}} tr:nth-child(even){{background-color:#ecf0f1;}} td:nth-child(2),td:nth-child(3){{text-align:right;}} .ident-aluno{{margin:0 0 30px 0;padding:10px 0 18px 0;border-bottom:1px solid #e0e0e0;display:flex;flex-wrap:wrap;align-items:center;}} .ident-aluno label{{font-weight:bold;display:inline-block;width:90px;}} .ident-aluno input{{border:none;border-bottom:1px solid #aaa;background:transparent;width:180px;font-size:1em;margin-right:30px;}} .ident-aluno .data{{margin-left:auto;color:#888;font-size:0.98em;margin-top:8px;}} </style></head><body><div class='container'>
        <h2 style='margin-bottom:0.2em'>{header.get('titulo','')}</h2>
        {f"<div style='text-align:center;font-size:1.25em;color:#2c3e50;margin-bottom:0.7em'>{header.get('subtitulo','')}</div>" if header.get('subtitulo','') else ''}
        <div class='ident-aluno'>
        {campos_html}
        </div>
        <h3>Enunciado</h3>
        <div class='enunciado-justificado'>{markdown_to_html(md_content)}</div>
        <hr><h3>Parâmetros Gerados</h3>{tabela}
        <hr><div style='display:flex;justify-content:space-between;color:#888;font-size:0.98em;'>
          <span>Arquivo gerado automaticamente para uso didático. <strong>Seed:</strong> {seed}</span>
          <span>Data/hora da geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div></div></body></html>
        """
        return html

    if gerar_individual:
        if seed_input and seed_input.isdigit():
            seed = int(seed_input)
            if 0 <= seed <= 99:
                html = gerar_html_avaliacao(seed)
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
menu = st.sidebar.radio("Selecione o modo:", ["Aluno", "Professor (Configuração)"])
if menu == "Professor (Configuração)":
    area_professor()
else:
    area_aluno()

st.markdown("---")
st.markdown("Desenvolvido para fins didáticos - Prof. Manoel Dênis Costa Ferreira")
