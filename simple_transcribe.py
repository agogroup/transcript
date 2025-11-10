#!/usr/bin/env python3
"""
簡易文字起こしスクリプト - Web UIなしで使用可能
"""

import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.transcriber import WhisperTranscriber
from src.preprocessor import AudioPreprocessor

def transcribe_file(audio_path, output_path=None, language='ja'):
    """
    音声ファイルを文字起こし

    Args:
        audio_path: 音声ファイルのパス
        output_path: 出力ファイルのパス（省略可）
        language: 言語コード（デフォルト: ja）
    """
    # APIキーを環境変数から取得
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("エラー: OPENAI_API_KEYが設定されていません")
        print(".envファイルを確認してください")
        return

    print("=" * 60)
    print("Whisper 文字起こしツール")
    print("=" * 60)
    print(f"\n入力ファイル: {audio_path}")

    # ファイルの存在確認
    if not os.path.exists(audio_path):
        print(f"エラー: ファイルが見つかりません: {audio_path}")
        return

    # 出力ファイル名の決定
    if not output_path:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"{base_name}_transcript.txt"

    print(f"出力ファイル: {output_path}")
    print(f"言語: {language}\n")

    try:
        # 音声情報の表示
        print("【ステップ1】音声ファイル情報")
        print("-" * 60)
        preprocessor = AudioPreprocessor()
        audio_info = preprocessor.get_audio_info(audio_path)
        print(f"  長さ: {audio_info['duration_seconds']:.2f}秒")
        print(f"  サンプルレート: {audio_info['frame_rate']}Hz")
        print(f"  ファイルサイズ: {audio_info['file_size_mb']:.2f}MB\n")

        # 文字起こし
        print("【ステップ2】文字起こし実行中...")
        print("-" * 60)
        transcriber = WhisperTranscriber(api_key=api_key)
        result = transcriber.transcribe(
            audio_path=audio_path,
            language=language,
            temperature=0.0
        )
        print("✓ 文字起こし完了\n")

        # 結果の保存
        print("【ステップ3】結果の保存")
        print("-" * 60)
        transcriber.save_transcript(result, output_path, format='txt')

        # プレビュー表示
        print("\n【プレビュー】")
        print("-" * 60)
        text = result.get('text', '')
        preview = text[:300] + "..." if len(text) > 300 else text
        print(preview)
        print()

        print("=" * 60)
        print("✓ 完了！")
        print(f"結果は {output_path} に保存されました")
        print("=" * 60)

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 使用例
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python simple_transcribe.py <音声ファイル> [出力ファイル] [言語]")
        print("\n例:")
        print("  python simple_transcribe.py audio.mp3")
        print("  python simple_transcribe.py audio.mp3 output.txt")
        print("  python simple_transcribe.py audio.mp3 output.txt en")
        sys.exit(1)

    audio_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    language = sys.argv[3] if len(sys.argv) > 3 else 'ja'

    # .envファイルの読み込み
    from dotenv import load_dotenv
    load_dotenv()

    transcribe_file(audio_file, output_file, language)
