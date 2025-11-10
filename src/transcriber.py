"""
文字起こしモジュール

このモジュールは、OpenAI Whisper APIを使用して音声ファイルを文字起こしします。
主な機能:
- Whisper APIを使った文字起こし
- 複数の出力形式対応（TXT, JSON, SRT, VTT）
- カスタムプロンプト対応
- 長時間音声の分割処理
"""

import os
import json
from typing import Optional, Literal
from datetime import timedelta
from openai import OpenAI
from tqdm import tqdm


OutputFormat = Literal["txt", "json", "srt", "vtt", "verbose_json"]


class WhisperTranscriber:
    """Whisper APIを使った文字起こしクラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: OpenAI APIキー（指定しない場合は環境変数から取得）
        """
        self.client = OpenAI(api_key=api_key)

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: OutputFormat = "verbose_json",
    ) -> dict:
        """
        音声ファイルを文字起こし

        Args:
            audio_path: 音声ファイルのパス
            language: 言語コード（例: 'ja', 'en'）。指定しない場合は自動検出
            prompt: カスタムプロンプト（専門用語、文脈情報など）
            temperature: サンプリング温度（0.0-1.0）。0に近いほど決定的
            response_format: レスポンス形式

        Returns:
            文字起こし結果の辞書
        """
        print(f"文字起こし中: {audio_path}")

        with open(audio_path, "rb") as audio_file:
            # Whisper APIを呼び出し
            kwargs = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": response_format,
                "temperature": temperature,
            }

            if language:
                kwargs["language"] = language

            if prompt:
                kwargs["prompt"] = prompt

            response = self.client.audio.transcriptions.create(**kwargs)

        # レスポンス形式に応じて処理
        if response_format == "verbose_json":
            return {
                "text": response.text,
                "language": response.language,
                "duration": response.duration,
                "segments": response.segments if hasattr(response, "segments") else [],
            }
        elif response_format == "json":
            return {"text": response.text}
        else:
            # text, srt, vtt形式の場合は文字列が返される
            return {"text": response}

    def transcribe_batch(
        self,
        audio_paths: list[str],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> list[dict]:
        """
        複数の音声ファイルを文字起こし

        Args:
            audio_paths: 音声ファイルのパスのリスト
            language: 言語コード
            prompt: カスタムプロンプト
            temperature: サンプリング温度

        Returns:
            文字起こし結果のリスト
        """
        results = []

        print(f"\n{len(audio_paths)}個のファイルを処理します...")

        for audio_path in tqdm(audio_paths, desc="文字起こし進捗"):
            result = self.transcribe(
                audio_path=audio_path,
                language=language,
                prompt=prompt,
                temperature=temperature,
            )
            results.append(result)

        return results

    def save_transcript(
        self,
        transcript: dict | list[dict],
        output_path: str,
        format: OutputFormat = "txt",
    ) -> None:
        """
        文字起こし結果をファイルに保存

        Args:
            transcript: 文字起こし結果（単一または複数）
            output_path: 出力ファイルのパス
            format: 出力形式
        """
        # 複数の結果を結合
        if isinstance(transcript, list):
            combined_transcript = self._combine_transcripts(transcript)
        else:
            combined_transcript = transcript

        # 形式に応じて保存
        if format == "txt":
            self._save_as_txt(combined_transcript, output_path)
        elif format in ["json", "verbose_json"]:
            self._save_as_json(combined_transcript, output_path)
        elif format == "srt":
            self._save_as_srt(combined_transcript, output_path)
        elif format == "vtt":
            self._save_as_vtt(combined_transcript, output_path)
        else:
            raise ValueError(f"サポートされていない出力形式: {format}")

        print(f"文字起こし結果を保存しました: {output_path}")

    def _combine_transcripts(self, transcripts: list[dict]) -> dict:
        """
        複数の文字起こし結果を結合

        Args:
            transcripts: 文字起こし結果のリスト

        Returns:
            結合された文字起こし結果
        """
        combined_text = " ".join(t.get("text", "") for t in transcripts)

        combined = {
            "text": combined_text,
            "segments": [],
        }

        # セグメント情報がある場合は結合
        time_offset = 0.0
        for transcript in transcripts:
            if "segments" in transcript and transcript["segments"]:
                for segment in transcript["segments"]:
                    adjusted_segment = segment.copy()
                    adjusted_segment["start"] += time_offset
                    adjusted_segment["end"] += time_offset
                    combined["segments"].append(adjusted_segment)

            # 次のチャンクのためにオフセットを更新
            if "duration" in transcript:
                time_offset += transcript["duration"]

        return combined

    def _save_as_txt(self, transcript: dict, output_path: str) -> None:
        """テキスト形式で保存"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript.get("text", ""))

    def _save_as_json(self, transcript: dict, output_path: str) -> None:
        """JSON形式で保存"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)

    def _save_as_srt(self, transcript: dict, output_path: str) -> None:
        """SRT字幕形式で保存"""
        if "segments" not in transcript or not transcript["segments"]:
            raise ValueError("SRT形式で保存するにはセグメント情報が必要です")

        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(transcript["segments"], 1):
                start_time = self._format_timestamp(segment["start"], srt=True)
                end_time = self._format_timestamp(segment["end"], srt=True)
                text = segment["text"].strip()

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def _save_as_vtt(self, transcript: dict, output_path: str) -> None:
        """WebVTT字幕形式で保存"""
        if "segments" not in transcript or not transcript["segments"]:
            raise ValueError("VTT形式で保存するにはセグメント情報が必要です")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")

            for segment in transcript["segments"]:
                start_time = self._format_timestamp(segment["start"], srt=False)
                end_time = self._format_timestamp(segment["end"], srt=False)
                text = segment["text"].strip()

                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds: float, srt: bool = False) -> str:
        """
        タイムスタンプをフォーマット

        Args:
            seconds: 秒数
            srt: SRT形式（カンマ区切り）かVTT形式（ピリオド区切り）か

        Returns:
            フォーマットされたタイムスタンプ
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        separator = "," if srt else "."

        return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def create_prompt_template(
    context: Optional[str] = None,
    terminology: Optional[list[str]] = None,
    speaker_info: Optional[str] = None,
) -> str:
    """
    カスタムプロンプトを作成（精度向上のため）

    Args:
        context: 会話の文脈や背景情報
        terminology: 専門用語のリスト
        speaker_info: 話者情報

    Returns:
        プロンプト文字列
    """
    prompt_parts = []

    if context:
        prompt_parts.append(f"文脈: {context}")

    if terminology:
        terms = ", ".join(terminology)
        prompt_parts.append(f"専門用語: {terms}")

    if speaker_info:
        prompt_parts.append(f"話者: {speaker_info}")

    return " | ".join(prompt_parts) if prompt_parts else None
