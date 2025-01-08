from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import time

app = Flask(__name__)

# Definir o diretório de downloads do usuário
DOWNLOAD_DIR = str(Path.home() / "Downloads")

# Dicionário para armazenar o progresso dos downloads
download_progress = {}

def progress_hook(d):
    if d['status'] == 'downloading':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        
        # Calcular progresso
        if 'total_bytes' in d:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
        elif 'total_bytes_estimate' in d:
            percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
        else:
            percent = 0
            
        # Atualizar progresso
        download_progress[video_id] = {
            'status': 'downloading',
            'percent': percent,
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0),
            'filename': d.get('filename', '')
        }
        
    elif d['status'] == 'finished':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        download_progress[video_id] = {
            'status': 'finished',
            'percent': 100
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress/<video_id>')
def get_progress(video_id):
    return jsonify(download_progress.get(video_id, {'status': 'unknown', 'percent': 0}))

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        urls = data.get('urls', [])
        format_type = data.get('format')
        
        results = []
        for url in urls:
            try:
                output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
                
                ydl_opts = {
                    'format': 'bestaudio/best' if format_type == 'mp3' else 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',
                    'outtmpl': output_template,
                    'progress_hooks': [progress_hook],
                    'quiet': False,
                    'no_warnings': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5',
                        'Sec-Fetch-Mode': 'navigate'
                    }
                }
                
                if format_type == 'mp3':
                    ydl_opts.update({
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Primeiro, extrair informações do vídeo
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Video')
                    video_id = info.get('id', 'unknown')
                    
                    # Inicializar progresso
                    download_progress[video_id] = {
                        'status': 'starting',
                        'percent': 0
                    }
                    
                    # Depois, fazer o download
                    ydl.download([url])
                    
                    # Determinar o caminho do arquivo baixado
                    if format_type == 'mp3':
                        file_path = os.path.join(DOWNLOAD_DIR, f"{video_title}.mp3")
                    else:
                        # Para MP4, pegamos a extensão do formato escolhido
                        ext = 'mp4'
                        file_path = os.path.join(DOWNLOAD_DIR, f"{video_title}.{ext}")
                    
                    # Verificar se o arquivo existe
                    if os.path.exists(file_path):
                        download_url = f"/get_file/{video_title}.{format_type}"
                        results.append({
                            'title': video_title,
                            'status': 'success',
                            'path': file_path,
                            'download_url': download_url,
                            'video_id': video_id
                        })
                    else:
                        raise Exception("Arquivo não foi criado corretamente")
                    
            except Exception as e:
                print(f"Erro no download: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'message': str(e)
                })
        
        return jsonify({'results': results})
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_file/<filename>')
def get_file(filename):
    try:
        return send_file(
            os.path.join(DOWNLOAD_DIR, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True)
