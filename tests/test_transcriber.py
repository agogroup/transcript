"""
文字起こしモジュールのテスト
"""

import json
import tempfile
import os
import pytest
from src.transcriber import WhisperTranscriber, create_prompt_template


class TestWhisperTranscriber:
    """WhisperTranscriberクラスのテスト"""

    def test_create_prompt_template_empty(self):
        """空のプロンプトテンプレート作成テスト"""
        prompt = create_prompt_template()
        assert prompt is None

    def test_create_prompt_template_with_context(self):
        """文脈ありのプロンプトテンプレート作成テスト"""
        prompt = create_prompt_template(context="医療会議")
        assert "文脈: 医療会議" in prompt

    def test_create_prompt_template_with_terminology(self):
        """専門用語ありのプロンプトテンプレート作成テスト"""
        prompt = create_prompt_template(terminology=["API", "REST", "JSON"])
        assert "専門用語:" in prompt
        assert "API" in prompt
        assert "REST" in prompt
        assert "JSON" in prompt

    def test_create_prompt_template_with_all(self):
        """全要素ありのプロンプトテンプレート作成テスト"""
        prompt = create_prompt_template(
            context="技術会議",
            terminology=["Python", "Docker"],
            speaker_info="エンジニア3名",
        )
        assert "文脈: 技術会議" in prompt
        assert "専門用語: Python, Docker" in prompt
        assert "話者: エンジニア3名" in prompt

    def test_save_transcript_txt(self):
        """TXT形式での保存テスト"""
        transcriber = WhisperTranscriber(api_key="dummy")

        transcript = {"text": "これはテストです。"}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            output_path = f.name

        try:
            transcriber.save_transcript(transcript, output_path, format="txt")

            assert os.path.exists(output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert content == "これはテストです。"
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_save_transcript_json(self):
        """JSON形式での保存テスト"""
        transcriber = WhisperTranscriber(api_key="dummy")

        transcript = {
            "text": "これはテストです。",
            "language": "ja",
            "duration": 5.0,
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_path = f.name

        try:
            transcriber.save_transcript(transcript, output_path, format="json")

            assert os.path.exists(output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                assert content["text"] == "これはテストです。"
                assert content["language"] == "ja"
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_combine_transcripts(self):
        """複数の文字起こし結果の結合テスト"""
        transcriber = WhisperTranscriber(api_key="dummy")

        transcripts = [
            {"text": "最初の部分。", "duration": 5.0},
            {"text": "次の部分。", "duration": 3.0},
        ]

        combined = transcriber._combine_transcripts(transcripts)

        assert "text" in combined
        assert "最初の部分。 次の部分。" == combined["text"]
