"""
音声前処理モジュール

このモジュールは、文字起こしの精度を向上させるために音声ファイルを前処理します。
主な機能:
- ノイズ除去
- 音量正規化
- サンプルレート変換
- ファイルサイズの最適化
"""

import os
import tempfile
from typing import Optional, Tuple
import numpy as np
import noisereduce as nr
import soundfile as sf
import librosa
from pydub import AudioSegment
from pydub.effects import normalize


class AudioPreprocessor:
    """音声前処理を行うクラス"""

    def __init__(self, sample_rate: int = 16000):
        """
        初期化

        Args:
            sample_rate: 目標サンプルレート（Hz）。Whisperは16kHzが推奨
        """
        self.sample_rate = sample_rate

    def process(
        self,
        audio_path: str,
        remove_noise: bool = True,
        normalize_audio: bool = True,
        output_path: Optional[str] = None
    ) -> str:
        """
        音声ファイルを前処理

        Args:
            audio_path: 入力音声ファイルのパス
            remove_noise: ノイズ除去を実行するか
            normalize_audio: 音量正規化を実行するか
            output_path: 出力ファイルのパス（指定しない場合は一時ファイル）

        Returns:
            処理済み音声ファイルのパス
        """
        print(f"音声ファイルを前処理中: {audio_path}")

        # 音声を読み込み
        audio, sr = librosa.load(audio_path, sr=None)

        # ノイズ除去
        if remove_noise:
            print("  - ノイズ除去を実行中...")
            audio = self._remove_noise(audio, sr)

        # サンプルレート変換
        if sr != self.sample_rate:
            print(f"  - サンプルレートを {sr}Hz から {self.sample_rate}Hz に変換中...")
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            sr = self.sample_rate

        # 一時ファイルに保存
        if output_path is None:
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)

        # WAVファイルとして保存
        sf.write(output_path, audio, sr)

        # 音量正規化（pydubを使用）
        if normalize_audio:
            print("  - 音量を正規化中...")
            audio_segment = AudioSegment.from_wav(output_path)
            normalized = normalize(audio_segment)
            normalized.export(output_path, format="wav")

        print(f"前処理完了: {output_path}")
        return output_path

    def _remove_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        ノイズ除去を実行

        Args:
            audio: 音声データ
            sr: サンプルレート

        Returns:
            ノイズ除去後の音声データ
        """
        # スタティックノイズ除去
        # 最初の1秒をノイズプロファイルとして使用
        noise_sample_duration = min(1.0, len(audio) / sr * 0.1)  # 最大1秒または音声の10%
        noise_sample_length = int(noise_sample_duration * sr)

        if noise_sample_length > 0:
            reduced_noise = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.8  # ノイズ削減の強度（0.0-1.0）
            )
            return reduced_noise

        return audio

    def split_audio(
        self,
        audio_path: str,
        max_size_mb: float = 24,
        output_dir: Optional[str] = None
    ) -> list[str]:
        """
        音声ファイルを分割（Whisper APIの25MB制限対策）

        Args:
            audio_path: 入力音声ファイルのパス
            max_size_mb: 最大ファイルサイズ（MB）
            output_dir: 出力ディレクトリ（指定しない場合は一時ディレクトリ）

        Returns:
            分割された音声ファイルのパスのリスト
        """
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

        if file_size_mb <= max_size_mb:
            # 分割不要
            return [audio_path]

        print(f"ファイルサイズ {file_size_mb:.2f}MB が制限を超えています。分割中...")

        # 音声を読み込み
        audio = AudioSegment.from_file(audio_path)
        duration_ms = len(audio)

        # 分割数を計算
        num_splits = int(np.ceil(file_size_mb / max_size_mb))
        chunk_duration_ms = duration_ms // num_splits

        # 出力ディレクトリの準備
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        os.makedirs(output_dir, exist_ok=True)

        # 分割して保存
        split_files = []
        for i in range(num_splits):
            start_ms = i * chunk_duration_ms
            end_ms = min((i + 1) * chunk_duration_ms, duration_ms)

            chunk = audio[start_ms:end_ms]
            chunk_path = os.path.join(output_dir, f"chunk_{i:03d}.wav")
            chunk.export(chunk_path, format="wav")
            split_files.append(chunk_path)

            print(f"  - チャンク {i+1}/{num_splits} を作成: {chunk_path}")

        return split_files

    def get_audio_info(self, audio_path: str) -> dict:
        """
        音声ファイルの情報を取得

        Args:
            audio_path: 音声ファイルのパス

        Returns:
            音声情報の辞書
        """
        audio = AudioSegment.from_file(audio_path)

        return {
            'duration_seconds': len(audio) / 1000.0,
            'channels': audio.channels,
            'sample_width': audio.sample_width,
            'frame_rate': audio.frame_rate,
            'file_size_mb': os.path.getsize(audio_path) / (1024 * 1024)
        }
