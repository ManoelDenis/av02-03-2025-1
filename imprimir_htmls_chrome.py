import os
import subprocess
from PyPDF2 import PdfMerger

# Caminho da pasta de avaliações
AVALIACOES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'avaliacoes')
PDFS_DIR = os.path.join(AVALIACOES_DIR, 'pdfs_temp')
MERGED_PDF = os.path.join(AVALIACOES_DIR, 'avaliacoes_unificadas.pdf')

# Caminho do executável do Chrome (ajuste se necessário)
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# Função para buscar todos os HTMLs
def encontrar_htmls(avaliacoes_dir):
    html_files = []
    for root, dirs, files in os.walk(avaliacoes_dir):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)

# Função para imprimir cada HTML em PDF usando Chrome headless
def imprimir_htmls_em_pdfs(html_files, pdfs_dir):
    os.makedirs(pdfs_dir, exist_ok=True)
    pdf_paths = []
    for html_path in html_files:
        pdf_name = os.path.splitext(os.path.basename(html_path))[0] + '.pdf'
        pdf_path = os.path.join(pdfs_dir, pdf_name)
        cmd = [
            CHROME_PATH,
            '--headless',
            '--disable-gpu',
            f'--print-to-pdf={pdf_path}',
            html_path
        ]
        print(f'Imprimindo {html_path} -> {pdf_path}')
        subprocess.run(cmd, check=True)
        pdf_paths.append(pdf_path)
    return pdf_paths

# Função para juntar todos os PDFs em um só
def juntar_pdfs(pdf_paths, output_pdf):
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()
    print(f'PDF final gerado: {output_pdf}')

if __name__ == '__main__':
    print('Buscando arquivos HTML na pasta "avaliacoes"...')
    if not os.path.isdir(AVALIACOES_DIR):
        print('A pasta "avaliacoes" não existe.')
        exit(1)
    htmls = encontrar_htmls(AVALIACOES_DIR)
    if not htmls:
        print('Nenhum arquivo HTML encontrado na pasta "avaliacoes".')
        exit(1)
    print(f'Encontrados {len(htmls)} arquivos HTML.')
    print('Imprimindo HTMLs em PDF usando Google Chrome...')
    pdfs = imprimir_htmls_em_pdfs(htmls, PDFS_DIR)
    print('Juntando todos os PDFs em um único arquivo...')
    juntar_pdfs(pdfs, MERGED_PDF)
    print('Processo concluído!')
    # Opcional: remover PDFs temporários
    import shutil
    shutil.rmtree(PDFS_DIR)
