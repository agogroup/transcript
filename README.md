# Whisper文字起こしツール

OpenAI Whisper APIを活用した高精度な音声文字起こしツール。文字起こしの精度を向上させるための前処理機能を搭載しています。

## 使用方法

このツールは2つの方法で使用できます：

1. **Web UI** （推奨）- ブラウザから簡単に使える直感的なインターフェース
2. **CLI** - コマンドラインから使える高度なインターフェース

## 特徴

### 🎯 高精度な文字起こし
- OpenAI Whisper APIを使用した最先端の音声認識
- 日本語を含む多言語対応
- カスタムプロンプトによる専門用語対応

### 🔧 前処理による精度向上
- **ノイズ除去**: FFTベースの高度なノイズリダクション
- **音量正規化**: 最適な音量レベルへの自動調整
- **サンプルレート最適化**: Whisper推奨の16kHzへの変換

### 📦 柔軟な出力オプション
- テキスト形式（TXT）
- JSON形式（タイムスタンプ付き）
- 字幕形式（SRT、VTT）

### 🚀 大容量ファイル対応
- 25MB制限への自動対応（ファイル分割処理）
- 長時間音声のバッチ処理
- 複数音声ファイルの一括処理

## インストール

### 前提条件
- Python 3.8以上
- OpenAI APIキー

### 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### FFmpegのインストール（推奨）

音声ファイルの形式変換のためにFFmpegが必要です。

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
[FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードしてインストール

## セットアップ

### 1. 環境変数の設定

`.env`ファイルを作成して、OpenAI APIキーを設定します：

```bash
cp .env.example .env
```

`.env`ファイルを編集：
```
OPENAI_API_KEY=your_api_key_here
```

### 2. 実行権限の付与（Unix系OSの場合）

```bash
chmod +x main.py run_web.py
```

## 使い方

### Web UI（推奨）

ブラウザから簡単に使える直感的なインターフェースです。

#### 起動方法

```bash
python run_web.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

詳細は [Web UI ガイド](WEB_UI_GUIDE.md) を参照してください。

#### Web UIの特徴

- ドラッグ&ドロップでファイルアップロード
- リアルタイムプレビュー
- 直感的なオプション設定
- ブラウザで結果をダウンロード

### CLI

### 基本的な使い方

```bash
python main.py transcribe input.mp3
```

### 出力ファイルを指定

```bash
python main.py transcribe input.mp3 -o output.txt
```

### 出力形式を指定

```bash
# JSON形式（タイムスタンプ付き）
python main.py transcribe input.mp3 -f verbose_json -o output.json

# SRT字幕形式
python main.py transcribe input.mp3 -f srt -o output.srt

# WebVTT字幕形式
python main.py transcribe input.mp3 -f vtt -o output.vtt
```

### 言語を指定

```bash
python main.py transcribe input.mp3 -l ja  # 日本語
python main.py transcribe input.mp3 -l en  # 英語
```

### カスタムプロンプトで精度向上

専門用語や文脈情報を指定することで、文字起こしの精度を向上できます：

```bash
# 専門用語を指定
python main.py transcribe medical_meeting.mp3 \
  --terminology "カテーテル,心房細動,抗凝固薬"

# 文脈情報を指定
python main.py transcribe tech_meeting.mp3 \
  --context "Pythonのコードレビュー会議"

# 話者情報を指定
python main.py transcribe interview.mp3 \
  --speaker "インタビュアー1名、エンジニア2名"

# すべてを組み合わせ
python main.py transcribe meeting.mp3 \
  --context "AI開発プロジェクト会議" \
  --terminology "機械学習,ニューラルネットワーク,Transformer" \
  --speaker "エンジニア3名、マネージャー1名"
```

### 前処理オプション

```bash
# 前処理をスキップ
python main.py transcribe input.mp3 --no-preprocess

# ノイズ除去のみスキップ
python main.py transcribe input.mp3 --no-noise-reduction

# 音量正規化のみスキップ
python main.py transcribe input.mp3 --no-normalize
```

### 音声ファイル情報の確認

```bash
python main.py info input.mp3
```

### 高度な使用例

```bash
# 品質重視の設定
python main.py transcribe interview.mp3 \
  -l ja \
  -f verbose_json \
  --temperature 0.0 \
  --context "製品開発インタビュー" \
  --terminology "UX,UI,プロトタイプ,イテレーション"

# 長時間音声（自動分割処理）
python main.py transcribe long_lecture.mp3 \
  -l ja \
  -f srt \
  -o lecture_subtitles.srt
```

## コマンドラインオプション

### `transcribe` コマンド

| オプション | 説明 | デフォルト |
|----------|------|----------|
| `-o, --output` | 出力ファイルのパス | 入力ファイル名.txt |
| `-f, --format` | 出力形式（txt/json/srt/vtt/verbose_json） | txt |
| `-l, --language` | 言語コード（ja/en等） | 自動検出 |
| `--prompt` | カスタムプロンプト | なし |
| `--context` | 会話の文脈情報 | なし |
| `--terminology` | 専門用語（カンマ区切り） | なし |
| `--speaker` | 話者情報 | なし |
| `--temperature` | サンプリング温度（0.0-1.0） | 0.0 |
| `--no-preprocess` | 前処理をスキップ | False |
| `--no-noise-reduction` | ノイズ除去をスキップ | False |
| `--no-normalize` | 音量正規化をスキップ | False |
| `--api-key` | OpenAI APIキー | 環境変数から取得 |

## プロジェクト構成

```
transcript/
├── src/
│   ├── __init__.py          # パッケージ初期化
│   ├── cli.py               # CLIインターフェース
│   ├── transcriber.py       # 文字起こしメインロジック
│   └── preprocessor.py      # 音声前処理
├── tests/
│   ├── __init__.py
│   ├── test_transcriber.py  # 文字起こしテスト
│   └── test_preprocessor.py # 前処理テスト
├── examples/                # サンプル音声ファイル
├── main.py                  # エントリーポイント
├── requirements.txt         # 依存パッケージ
├── pytest.ini              # テスト設定
├── .env.example            # 環境変数サンプル
├── .gitignore
└── README.md
```

## 精度向上のベストプラクティス

### 1. 音声品質の確保
- クリアな録音環境
- 適切なマイク配置
- 背景ノイズの最小化

### 2. 前処理の活用
- ノイズ除去機能を有効化（デフォルト）
- 音量正規化を有効化（デフォルト）

### 3. カスタムプロンプトの活用
- 専門用語リストの指定
- 会話の文脈情報の提供
- 話者情報の明示

### 4. 適切な設定
- 言語を明示的に指定（`-l ja`）
- 決定的な出力には`--temperature 0.0`を使用
- 長時間音声は自動分割（25MB超の場合）

## テスト

```bash
# すべてのテストを実行
pytest

# 詳細な出力
pytest -v

# 特定のテストファイルを実行
pytest tests/test_transcriber.py
```

## トラブルシューティング

### FFmpegがインストールされていない

```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**解決方法**: FFmpegをインストールしてください（上記「FFmpegのインストール」を参照）

### APIキーが設定されていない

```
エラー: OpenAI APIキーが設定されていません。
```

**解決方法**: `.env`ファイルに`OPENAI_API_KEY`を設定するか、`--api-key`オプションを使用

### ファイルサイズ制限

Whisper APIには25MBのファイルサイズ制限があります。このツールは自動的に大きなファイルを分割処理しますが、非常に長い音声の場合は時間がかかることがあります。

## 技術詳細

### 使用している主要なライブラリ

- **openai**: OpenAI Whisper API クライアント
- **pydub**: 音声ファイル操作
- **noisereduce**: FFTベースのノイズ除去
- **librosa**: 音声信号処理
- **soundfile**: 音声ファイルI/O
- **click**: CLIフレームワーク

### 前処理アルゴリズム

1. **ノイズ除去**:
   - FFT（高速フーリエ変換）ベースの周波数分析
   - スタティックノイズプロファイルの抽出
   - スペクトラルゲーティングによるノイズ低減

2. **音量正規化**:
   - ピークレベルの検出
   - RMS（二乗平均平方根）ベースの正規化
   - 動的レンジの最適化

3. **サンプルレート変換**:
   - リサンプリングアルゴリズム
   - 16kHzへの最適化（Whisper推奨値）

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

問題や質問がある場合は、GitHubのissueを作成してください。

## 参考資料

- [OpenAI Whisper API Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [Whisper GitHub Repository](https://github.com/openai/whisper)
- [OpenAI Cookbook - Whisper Processing Guide](https://cookbook.openai.com/examples/whisper_processing_guide)

---

開発: [Your Name]
バージョン: 1.0.0
最終更新: 2025年1月
