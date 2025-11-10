# Whisper文字起こしツール - クイックスタートガイド

Web UIへのアクセスに問題がある場合は、以下のCLI方式で簡単に使用できます。

## 方法1: 簡易スクリプト（推奨）

最もシンプルな方法です。

### 使い方

```bash
# 基本的な使い方
python simple_transcribe.py <音声ファイル>

# 出力ファイルを指定
python simple_transcribe.py audio.mp3 output.txt

# 言語を指定
python simple_transcribe.py audio.mp3 output.txt en
```

### 例

```bash
# 日本語の音声を文字起こし
python simple_transcribe.py meeting.mp3

# 英語の音声を文字起こし
python simple_transcribe.py interview.mp3 interview.txt en
```

## 方法2: 標準CLI

より高度な機能が必要な場合は、標準CLIを使用します。

### 使い方

```bash
# 基本的な文字起こし
python main.py transcribe audio.mp3

# 様々なオプション付き
python main.py transcribe audio.mp3 \
  -l ja \
  -f verbose_json \
  --context "技術会議" \
  --terminology "API,REST,Docker"
```

### オプション一覧

```bash
-o, --output          出力ファイルのパス
-f, --format          出力形式 (txt/json/srt/vtt)
-l, --language        言語コード (ja/en/など)
--context             文脈情報
--terminology         専門用語（カンマ区切り）
--speaker             話者情報
--no-preprocess       前処理をスキップ
```

## 方法3: Pythonスクリプトから直接使用

独自のスクリプトから使用する場合：

```python
from src.transcriber import WhisperTranscriber
import os

# APIキーを設定
os.environ['OPENAI_API_KEY'] = 'your-api-key'

# 文字起こし実行
transcriber = WhisperTranscriber()
result = transcriber.transcribe('audio.mp3', language='ja')

# 結果を保存
transcriber.save_transcript(result, 'output.txt', format='txt')

print(result['text'])
```

## セットアップ

APIキーは既に `.env` ファイルに設定されています。

確認方法:
```bash
cat .env | grep OPENAI_API_KEY
```

## トラブルシューティング

### 依存パッケージのエラー

```bash
pip install --break-system-packages --ignore-installed -r requirements.txt
```

### 音声ファイルが見つからない

ファイルパスが正しいか確認してください：
```bash
ls -la /path/to/audio.mp3
```

### APIキーのエラー

`.env` ファイルを確認：
```bash
cat .env
```

## サンプル実行

テスト用の短い音声ファイルがあれば、以下のように実行できます：

```bash
# サンプル音声がある場合
python simple_transcribe.py examples/sample.mp3

# または
python main.py transcribe examples/sample.mp3 -l ja
```

## Web UIについて

Web UIにアクセスできない場合でも、上記のCLI方式で全ての機能を利用できます。

サーバーの状態を確認:
```bash
ps aux | grep python | grep flask
```

サーバーを再起動:
```bash
pkill -f flask
python run_web.py &
```

---

質問や問題がある場合は、GitHubのissueを作成してください。
