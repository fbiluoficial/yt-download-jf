from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
from pathlib import Path
import tempfile
import logging

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do yt-dlp
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'progress_hooks': [],
}

download_progress = {}

def progress_hook(d):
    if d['status'] == 'downloading':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        try:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            
            if total > 0:
                progress = (downloaded / total) * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                download_progress[video_id] = {
                    'progress': progress,
                    'speed': speed,
                    'eta': eta,
                    'status': 'downloading'
                }
        except Exception as e:
            logger.error(f"Error in progress_hook: {str(e)}")

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        video_url = data.get('url')
        format_type = data.get('format', 'mp4')
        
        if not video_url:
            return jsonify({'error': 'URL não fornecida'}), 400

        with tempfile.TemporaryDirectory() as temp_dir:
            if format_type == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'postprocessors': [],
                })

            ydl_opts['progress_hooks'] = [progress_hook]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                video_id = info.get('id', 'unknown')
                filename = ydl.prepare_filename(info)
                
                if format_type == 'mp3':
                    filename = filename.rsplit('.', 1)[0] + '.mp3'

                if os.path.exists(filename):
                    download_progress[video_id] = {'status': 'completed'}
                    return send_file(
                        filename,
                        as_attachment=True,
                        download_name=os.path.basename(filename)
                    )
                else:
                    return jsonify({'error': 'Arquivo não encontrado'}), 404

    except Exception as e:
        logger.error(f"Error in download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<video_id>')
def get_progress(video_id):
    return jsonify(download_progress.get(video_id, {'status': 'unknown'}))

if __name__ == '__main__':
    app.run(debug=True)
