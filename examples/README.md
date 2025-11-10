# サンプル音声ファイル

このディレクトリには、テスト用のサンプル音声ファイルを配置してください。

## サンプルの使い方

### 1. 音声ファイルの準備

以下のような音声ファイルをこのディレクトリに配置します：

- `sample.mp3` - 短い会話やスピーチ
- `meeting.wav` - 会議の録音
- `interview.m4a` - インタビュー音声

### 2. テスト実行

```bash
# 基本的な文字起こし
python main.py transcribe examples/sample.mp3

# 情報の確認
python main.py info examples/sample.mp3

# 様々な形式で出力
python main.py transcribe examples/sample.mp3 -f json -o examples/sample.json
python main.py transcribe examples/sample.mp3 -f srt -o examples/sample.srt
```

## 推奨される音声ファイル特性

- **フォーマット**: MP3, WAV, M4A, FLAC等
- **品質**: 明瞭な音声、低ノイズ
- **長さ**: テストには10秒〜5分程度が適切
- **サンプルレート**: 16kHz以上推奨

## 注意事項

音声ファイルは個人情報を含まない、公開可能なものを使用してください。
このディレクトリ内の音声ファイルは`.gitignore`で除外されています。
