"""
Flask Web Application for Whisper Transcription Tool
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transcriber import WhisperTranscriber, create_prompt_template
from src.preprocessor import AudioPreprocessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
app.config['SECRET_KEY'] = os.urandom(24)

# アップロードディレクトリの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'wma'}


def allowed_file(filename):
    """許可されたファイル拡張子かチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_api_key():
    """APIキーを取得"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return os.getenv('OPENAI_API_KEY')


def save_api_key(api_key):
    """APIキーを.envファイルに保存"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    # 既存の.envファイルを読み込み
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()

    # OPENAI_API_KEYの行を更新または追加
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith('OPENAI_API_KEY='):
            lines[i] = f'OPENAI_API_KEY={api_key}\n'
            key_found = True
            break

    if not key_found:
        lines.append(f'OPENAI_API_KEY={api_key}\n')

    # .envファイルに書き込み
    with open(env_path, 'w') as f:
        f.writelines(lines)


@app.route('/')
def index():
    """メインページ"""
    api_key = get_api_key()
    has_api_key = bool(api_key)
    return render_template('index.html', has_api_key=has_api_key)


@app.route('/settings')
def settings():
    """設定ページ"""
    api_key = get_api_key()
    # APIキーの最後の4文字のみ表示
    masked_key = None
    if api_key:
        masked_key = '*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'
    return render_template('settings.html', masked_api_key=masked_key)


@app.route('/api/save-api-key', methods=['POST'])
def api_save_key():
    """APIキーを保存"""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()

    if not api_key:
        return jsonify({'success': False, 'error': 'APIキーが空です'}), 400

    try:
        save_api_key(api_key)
        return jsonify({'success': True, 'message': 'APIキーを保存しました'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check-api-key', methods=['GET'])
def api_check_key():
    """APIキーの設定状態をチェック"""
    api_key = get_api_key()
    return jsonify({'has_api_key': bool(api_key)})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """ファイルアップロード"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'サポートされていないファイル形式です。対応形式: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # ファイル情報を取得
        preprocessor = AudioPreprocessor()
        audio_info = preprocessor.get_audio_info(filepath)

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'audio_info': audio_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """文字起こし処理"""
    api_key = get_api_key()

    if not api_key:
        return jsonify({
            'success': False,
            'error': 'APIキーが設定されていません。設定ページでAPIキーを設定してください。'
        }), 400

    try:
        data = request.get_json()
        filepath = data.get('filepath')
        language = data.get('language', None)
        output_format = data.get('format', 'txt')
        use_preprocessing = data.get('use_preprocessing', True)
        use_noise_reduction = data.get('use_noise_reduction', True)
        use_normalization = data.get('use_normalization', True)

        # カスタムプロンプト
        context = data.get('context', None)
        terminology = data.get('terminology', None)
        speaker = data.get('speaker', None)

        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'ファイルが見つかりません'}), 400

        # プロンプトの作成
        prompt = None
        if context or terminology or speaker:
            terms = [t.strip() for t in terminology.split(',')] if terminology else None
            prompt = create_prompt_template(
                context=context if context else None,
                terminology=terms,
                speaker_info=speaker if speaker else None
            )

        # 前処理
        processed_audio = filepath
        temp_files = []

        if use_preprocessing:
            preprocessor = AudioPreprocessor()
            audio_info = preprocessor.get_audio_info(filepath)

            # ファイルサイズチェックと分割
            if audio_info['file_size_mb'] > 24:
                split_files = preprocessor.split_audio(filepath)
                temp_files.extend(split_files)

                # 各チャンクを前処理
                processed_files = []
                for split_file in split_files:
                    processed = preprocessor.process(
                        split_file,
                        remove_noise=use_noise_reduction,
                        normalize_audio=use_normalization
                    )
                    processed_files.append(processed)
                    if processed != split_file:
                        temp_files.append(processed)

                processed_audio = processed_files
            else:
                processed_audio = preprocessor.process(
                    filepath,
                    remove_noise=use_noise_reduction,
                    normalize_audio=use_normalization
                )
                if processed_audio != filepath:
                    temp_files.append(processed_audio)

        # 文字起こし
        transcriber = WhisperTranscriber(api_key=api_key)

        if isinstance(processed_audio, list):
            results = transcriber.transcribe_batch(
                audio_paths=processed_audio,
                language=language if language else None,
                prompt=prompt,
                temperature=0.0
            )
            result = results
        else:
            result = transcriber.transcribe(
                audio_path=processed_audio,
                language=language if language else None,
                prompt=prompt,
                temperature=0.0
            )

        # 出力ファイルの作成
        original_filename = Path(filepath).stem
        output_filename = f"{original_filename}_transcript.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        transcriber.save_transcript(result, output_path, format=output_format)

        # 一時ファイルのクリーンアップ
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

        # テキストプレビューの作成
        preview_text = ""
        if isinstance(result, dict) and 'text' in result:
            preview_text = result['text'][:500] + "..." if len(result['text']) > 500 else result['text']

        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'preview': preview_text,
            'full_result': result if output_format in ['json', 'verbose_json'] else None
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """ファイルダウンロード"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'ファイルが見つかりません'}), 404

        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """アップロードファイルと出力ファイルのクリーンアップ"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')

        if filepath and os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
