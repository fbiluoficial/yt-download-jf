from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return {'status': 'ok'}

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        format_type = data.get('format', 'mp4')

        if not url:
            return jsonify({'error': 'URL não fornecida'}), 400

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
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
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if format_type == 'mp3':
                    filename = filename.rsplit('.', 1)[0] + '.mp3'

                if os.path.exists(filename):
                    return send_file(
                        filename,
                        as_attachment=True,
                        download_name=os.path.basename(filename)
                    )
                else:
                    return jsonify({'error': 'Arquivo não encontrado'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
