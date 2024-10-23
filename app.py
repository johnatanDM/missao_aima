from flask import Flask, render_template, request, redirect, url_for, send_file
import uuid
import qrcode
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Função para gerar QR code
def gerar_qrcode(id_unico):
    qr_code_img = qrcode.make(f"http://meusistema.com/?id={id_unico}")
    qr_code_path = f"static/qrcodes/{id_unico}.png"
    qr_code_img.save(qr_code_path)
    return qr_code_path

# Função para limpar QR codes antigos
def limpar_qrcodes_antigos():
    qrcodes_dir = 'static/qrcodes'
    documentos_dir = 'uploads'
    tempo_limite = 1800  # 1 hora em segundos
    agora = time.time()

    for arquivo in os.listdir(qrcodes_dir):
        caminho_arquivo = os.path.join(qrcodes_dir, arquivo)
        if os.path.isfile(caminho_arquivo):
            # Verifica o tempo de modificação do arquivo
            tempo_modificacao = os.path.getmtime(caminho_arquivo)
            if agora - tempo_modificacao > tempo_limite:
                os.remove(caminho_arquivo)
                print(f"Arquivo removido: {caminho_arquivo}")
    for arquivo in os.listdir(documentos_dir):
        caminho_arquivo = os.path.join(qrcodes_dir, arquivo)
        if os.path.isfile(caminho_arquivo):
            # Verifica o tempo de modificação do arquivo
            tempo_modificacao = os.path.getmtime(caminho_arquivo)
            if agora - tempo_modificacao > tempo_limite:
                os.remove(caminho_arquivo)
                print(f"Arquivo removido: {caminho_arquivo}")

@app.route('/', methods=['GET', 'POST'])
def index():
    limpar_qrcodes_antigos()
    id_unico = request.args.get('id')  # Captura o ID da URL
    if not id_unico:  # Se não houver ID na URL, gera um novo
        id_unico = str(uuid.uuid4())

    if request.method == 'POST':
        # Upload do arquivo
        arquivo = request.files['file']
        
        if arquivo and id_unico:
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], f"{id_unico}.pdf")
            arquivo.save(caminho_arquivo)
            return redirect(url_for('success', id_unico=id_unico))
    
    qr_code_path = gerar_qrcode(id_unico)  # Gera o QR code com o ID
    return render_template('index.html', id_unico=id_unico, qr_code_path=qr_code_path)

@app.route('/success/<id_unico>')
def success(id_unico):
    return render_template('success.html', id_unico=id_unico)

@app.route('/download/<id_unico>')
def download_file(id_unico):
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], f"{id_unico}.pdf")
    qr_code_path = os.path.join('static/qrcodes', f"{id_unico}.png")

    if os.path.exists(caminho_arquivo):
        # Envia o arquivo para download
        response = send_file(caminho_arquivo, as_attachment=True)
        
        # Remove o arquivo e o QR code após o download
        os.remove(caminho_arquivo)
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)
        
        return response
    
    return "Arquivo não encontrado.", 404

if __name__ == '__main__':
    # Cria diretórios se não existirem
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('static/qrcodes'):
        os.makedirs('static/qrcodes')
    
    # Limpa QR codes antigos ao iniciar o servidor
    limpar_qrcodes_antigos()
    
    app.run(debug=True)
