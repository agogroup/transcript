"""
音声前処理モジュールのテスト
"""

import os
import tempfile
import pytest
import numpy as np
import soundfile as sf
from src.preprocessor import AudioPreprocessor


class TestAudioPreprocessor:
    """AudioPreprocessorクラスのテスト"""

    @pytest.fixture
    def preprocessor(self):
        """テスト用のpreprocessorインスタンス"""
        return AudioPreprocessor()

    @pytest.fixture
    def sample_audio_file(self):
        """テスト用の音声ファイルを作成"""
        # 1秒間の440Hzのサイン波を生成
        sample_rate = 16000
        duration = 1.0
        frequency = 440.0

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)

        # 一時ファイルに保存
        temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_fd)

        sf.write(temp_path, audio_data, sample_rate)

        yield temp_path

        # クリーンアップ
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_get_audio_info(self, preprocessor, sample_audio_file):
        """音声情報の取得テスト"""
        info = preprocessor.get_audio_info(sample_audio_file)

        assert "duration_seconds" in info
        assert "channels" in info
        assert "frame_rate" in info
        assert "file_size_mb" in info

        # 1秒の音声なので、おおよそ1秒であることを確認
        assert 0.9 <= info["duration_seconds"] <= 1.1

    def test_process_without_preprocessing(self, preprocessor, sample_audio_file):
        """前処理なしの処理テスト"""
        output_path = preprocessor.process(
            sample_audio_file,
            remove_noise=False,
            normalize_audio=False,
        )

        assert os.path.exists(output_path)

        # クリーンアップ
        if output_path != sample_audio_file:
            os.remove(output_path)

    def test_process_with_noise_reduction(self, preprocessor, sample_audio_file):
        """ノイズ除去ありの処理テスト"""
        output_path = preprocessor.process(
            sample_audio_file,
            remove_noise=True,
            normalize_audio=False,
        )

        assert os.path.exists(output_path)

        # クリーンアップ
        if output_path != sample_audio_file:
            os.remove(output_path)

    def test_split_audio_small_file(self, preprocessor, sample_audio_file):
        """小さいファイルの分割テスト（分割不要）"""
        split_files = preprocessor.split_audio(sample_audio_file, max_size_mb=10)

        # 小さいファイルなので分割されない
        assert len(split_files) == 1
        assert split_files[0] == sample_audio_file
