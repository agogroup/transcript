# 使用例集

## 基本的な使い方

### シンプルな文字起こし
```bash
python main.py transcribe audio.mp3
```

## ビジネス用途

### 会議の文字起こし
```bash
python main.py transcribe meeting.mp3 \
  -l ja \
  -f verbose_json \
  --context "四半期事業報告会議" \
  --terminology "売上高,営業利益,KPI,ROI" \
  -o meeting_transcript.json
```

### インタビューの文字起こし
```bash
python main.py transcribe interview.mp3 \
  -l ja \
  -f txt \
  --context "製品開発責任者へのインタビュー" \
  --speaker "インタビュアー1名、開発責任者1名" \
  -o interview.txt
```

### プレゼンテーション録音の文字起こし
```bash
python main.py transcribe presentation.mp3 \
  -l ja \
  -f srt \
  --context "新製品発表プレゼンテーション" \
  --terminology "AI,機械学習,自動化,クラウド" \
  -o presentation_subtitles.srt
```

## 教育用途

### 講義の文字起こし
```bash
python main.py transcribe lecture.mp3 \
  -l ja \
  -f verbose_json \
  --context "量子力学の講義" \
  --terminology "波動関数,不確定性原理,重ね合わせ,量子もつれ" \
  --speaker "教授1名" \
  -o lecture.json
```

### オンライン授業の字幕作成
```bash
python main.py transcribe online_class.mp3 \
  -l ja \
  -f vtt \
  --context "高校数学授業" \
  -o class_subtitles.vtt
```

## 医療用途

### 診療記録の文字起こし
```bash
python main.py transcribe medical_record.mp3 \
  -l ja \
  -f json \
  --context "外来診療" \
  --terminology "血圧,脈拍,処方,診断,症状" \
  --speaker "医師1名、患者1名" \
  -o medical_record.json
```

### カンファレンスの議事録作成
```bash
python main.py transcribe conference.mp3 \
  -l ja \
  -f txt \
  --context "症例検討カンファレンス" \
  --terminology "CT,MRI,病理,治療方針,予後" \
  -o conference_minutes.txt
```

## 技術・開発用途

### コードレビュー会議
```bash
python main.py transcribe code_review.mp3 \
  -l ja \
  -f verbose_json \
  --context "Webアプリケーションのコードレビュー" \
  --terminology "API,REST,GraphQL,TypeScript,React,デバッグ" \
  --speaker "開発者3名" \
  -o code_review.json
```

### 技術カンファレンスの文字起こし
```bash
python main.py transcribe tech_conf.mp3 \
  -l en \
  -f srt \
  --context "International AI Conference" \
  --terminology "neural network,deep learning,transformer,LLM" \
  -o tech_conf_en.srt
```

## メディア・コンテンツ制作

### ポッドキャストの文字起こし
```bash
python main.py transcribe podcast_ep01.mp3 \
  -l ja \
  -f txt \
  --context "テクノロジートークポッドキャスト" \
  --speaker "ホスト2名、ゲスト1名" \
  -o podcast_ep01_transcript.txt
```

### YouTube動画の字幕作成
```bash
python main.py transcribe youtube_video.mp3 \
  -l ja \
  -f vtt \
  --context "プログラミングチュートリアル" \
  --terminology "Python,変数,関数,クラス,デバッグ" \
  -o youtube_subtitles.vtt
```

### ドキュメンタリー音声の文字起こし
```bash
python main.py transcribe documentary.mp3 \
  -l ja \
  -f srt \
  --context "歴史ドキュメンタリー" \
  -o documentary_subtitles.srt
```

## 多言語対応

### 英語音声の文字起こし
```bash
python main.py transcribe english_speech.mp3 \
  -l en \
  -f txt \
  --context "Business presentation" \
  --terminology "revenue,profit,market share,strategy" \
  -o english_transcript.txt
```

### 中国語音声の文字起こし
```bash
python main.py transcribe chinese_audio.mp3 \
  -l zh \
  -f json \
  -o chinese_transcript.json
```

## 特殊なケース

### ノイズの多い音声
```bash
# ノイズ除去を強化（デフォルトで有効）
python main.py transcribe noisy_audio.mp3 \
  -l ja \
  -o clean_transcript.txt
```

### 前処理なしで高速処理
```bash
python main.py transcribe audio.mp3 \
  --no-preprocess \
  -o transcript.txt
```

### 大容量ファイル（自動分割）
```bash
# 30MBの音声ファイルを自動分割して処理
python main.py transcribe large_file.wav \
  -l ja \
  -f verbose_json \
  -o large_transcript.json
```

### 複数の音声ファイルのバッチ処理
```bash
# シェルスクリプトで一括処理
for file in *.mp3; do
    python main.py transcribe "$file" \
      -l ja \
      -f txt \
      -o "${file%.mp3}.txt"
done
```

## 精度を最大化する設定

### 最高精度設定
```bash
python main.py transcribe important_meeting.mp3 \
  -l ja \
  -f verbose_json \
  --temperature 0.0 \
  --context "重要な契約交渉" \
  --terminology "契約条件,価格,納期,保証" \
  --speaker "当社2名、先方2名" \
  -o important_meeting.json
```

### バランス型設定
```bash
python main.py transcribe casual_talk.mp3 \
  -l ja \
  --temperature 0.2 \
  -o casual_transcript.txt
```

## 出力形式の使い分け

### テキストのみが必要な場合
```bash
python main.py transcribe audio.mp3 -f txt
```

### タイムスタンプ情報が必要な場合
```bash
python main.py transcribe audio.mp3 -f verbose_json
```

### 動画字幕を作成する場合
```bash
# SRT形式（広く対応）
python main.py transcribe video_audio.mp3 -f srt -o subtitles.srt

# VTT形式（Web向け）
python main.py transcribe video_audio.mp3 -f vtt -o subtitles.vtt
```

## トラブルシューティング例

### 音声ファイル情報の確認
```bash
python main.py info audio.mp3
```

### 短い音声で動作確認
```bash
python main.py transcribe short_test.mp3 \
  -l ja \
  --no-preprocess \
  -o test_output.txt
```

## 統合例

### プロダクション環境での使用
```bash
#!/bin/bash
# 会議音声の自動処理スクリプト

INPUT_DIR="./recordings"
OUTPUT_DIR="./transcripts"
LOG_FILE="./transcription.log"

mkdir -p "$OUTPUT_DIR"

for audio_file in "$INPUT_DIR"/*.mp3; do
    filename=$(basename "$audio_file" .mp3)
    echo "Processing: $filename" | tee -a "$LOG_FILE"

    python main.py transcribe "$audio_file" \
        -l ja \
        -f verbose_json \
        --context "定例会議" \
        -o "$OUTPUT_DIR/${filename}.json" \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        echo "Success: $filename" | tee -a "$LOG_FILE"
    else
        echo "Failed: $filename" | tee -a "$LOG_FILE"
    fi
done

echo "All processing completed" | tee -a "$LOG_FILE"
```

これらの例を参考に、用途に応じて適切なオプションを選択してください。
