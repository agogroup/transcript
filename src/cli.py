"""
CLIインターフェース

コマンドラインから文字起こしツールを使用するためのインターフェース
"""

import os
import sys
from pathlib import Path
import click
from dotenv import load_dotenv

from .transcriber import WhisperTranscriber, create_prompt_template, OutputFormat
from .preprocessor import AudioPreprocessor


# 環境変数を読み込み
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Whisper文字起こしツール

    OpenAI Whisper APIを使用した音声ファイルの文字起こしツール。
    精度向上のための前処理機能を搭載。
    """
    pass


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="出力ファイルのパス（指定しない場合は入力ファイル名.txt）",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["txt", "json", "srt", "vtt", "verbose_json"]),
    default="txt",
    help="出力形式（デフォルト: txt）",
)
@click.option(
    "-l",
    "--language",
    type=str,
    help="言語コード（例: ja, en）。指定しない場合は自動検出",
)
@click.option(
    "--prompt",
    type=str,
    help="カスタムプロンプト（専門用語や文脈情報）",
)
@click.option(
    "--context",
    type=str,
    help="会話の文脈や背景情報",
)
@click.option(
    "--terminology",
    type=str,
    help="専門用語（カンマ区切り）",
)
@click.option(
    "--speaker",
    type=str,
    help="話者情報",
)
@click.option(
    "--temperature",
    type=float,
    default=0.0,
    help="サンプリング温度（0.0-1.0）。0に近いほど決定的（デフォルト: 0.0）",
)
@click.option(
    "--no-preprocess",
    is_flag=True,
    help="前処理をスキップ",
)
@click.option(
    "--no-noise-reduction",
    is_flag=True,
    help="ノイズ除去をスキップ",
)
@click.option(
    "--no-normalize",
    is_flag=True,
    help="音量正規化をスキップ",
)
@click.option(
    "--api-key",
    type=str,
    envvar="OPENAI_API_KEY",
    help="OpenAI APIキー（環境変数OPENAI_API_KEYからも読み込み可能）",
)
def transcribe(
    audio_file,
    output,
    format,
    language,
    prompt,
    context,
    terminology,
    speaker,
    temperature,
    no_preprocess,
    no_noise_reduction,
    no_normalize,
    api_key,
):
    """
    音声ファイルを文字起こし

    AUDIO_FILE: 文字起こしする音声ファイルのパス
    """
    # APIキーの確認
    if not api_key:
        click.echo("エラー: OpenAI APIキーが設定されていません。", err=True)
        click.echo(
            "環境変数OPENAI_API_KEYを設定するか、--api-keyオプションを使用してください。",
            err=True,
        )
        sys.exit(1)

    try:
        # 出力ファイルパスの決定
        if not output:
            input_path = Path(audio_file)
            output = input_path.with_suffix(f".{format}")

        click.echo(f"\n{'='*60}")
        click.echo("Whisper文字起こしツール")
        click.echo(f"{'='*60}\n")
        click.echo(f"入力ファイル: {audio_file}")
        click.echo(f"出力ファイル: {output}")
        click.echo(f"出力形式: {format}")
        if language:
            click.echo(f"言語: {language}")
        click.echo()

        # 前処理
        processed_audio = audio_file
        temp_files = []

        if not no_preprocess:
            click.echo("【ステップ1】音声の前処理")
            click.echo("-" * 60)

            preprocessor = AudioPreprocessor()

            # 音声情報の表示
            audio_info = preprocessor.get_audio_info(audio_file)
            click.echo(f"音声情報:")
            click.echo(f"  - 長さ: {audio_info['duration_seconds']:.2f}秒")
            click.echo(f"  - サンプルレート: {audio_info['frame_rate']}Hz")
            click.echo(f"  - チャンネル数: {audio_info['channels']}")
            click.echo(f"  - ファイルサイズ: {audio_info['file_size_mb']:.2f}MB")
            click.echo()

            # ファイル分割が必要か確認
            if audio_info["file_size_mb"] > 24:
                click.echo("ファイルサイズが25MBを超えています。分割処理を実行します...")
                split_files = preprocessor.split_audio(audio_file)
                temp_files.extend(split_files)
                click.echo(f"{len(split_files)}個のチャンクに分割しました。")
                click.echo()

                # 各チャンクを前処理
                processed_files = []
                for i, split_file in enumerate(split_files, 1):
                    click.echo(f"チャンク {i}/{len(split_files)} を前処理中...")
                    processed = preprocessor.process(
                        split_file,
                        remove_noise=not no_noise_reduction,
                        normalize_audio=not no_normalize,
                    )
                    processed_files.append(processed)
                    if processed != split_file:
                        temp_files.append(processed)

                processed_audio = processed_files
            else:
                # 単一ファイルの前処理
                processed_audio = preprocessor.process(
                    audio_file,
                    remove_noise=not no_noise_reduction,
                    normalize_audio=not no_normalize,
                )
                if processed_audio != audio_file:
                    temp_files.append(processed_audio)

            click.echo()

        # プロンプトの作成
        if prompt is None and (context or terminology or speaker):
            terms = terminology.split(",") if terminology else None
            prompt = create_prompt_template(
                context=context, terminology=terms, speaker_info=speaker
            )
            if prompt:
                click.echo(f"カスタムプロンプト: {prompt}\n")

        # 文字起こし
        click.echo("【ステップ2】文字起こし")
        click.echo("-" * 60)

        transcriber = WhisperTranscriber(api_key=api_key)

        if isinstance(processed_audio, list):
            # 複数ファイルの処理
            results = transcriber.transcribe_batch(
                audio_paths=processed_audio,
                language=language,
                prompt=prompt,
                temperature=temperature,
            )
            result = results
        else:
            # 単一ファイルの処理
            result = transcriber.transcribe(
                audio_path=processed_audio,
                language=language,
                prompt=prompt,
                temperature=temperature,
            )

        click.echo()

        # 結果の保存
        click.echo("【ステップ3】結果の保存")
        click.echo("-" * 60)

        transcriber.save_transcript(result, output, format=format)

        # 一時ファイルのクリーンアップ
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception:
                pass

        click.echo()
        click.echo(f"{'='*60}")
        click.echo("✓ 文字起こしが完了しました！")
        click.echo(f"{'='*60}\n")

        # テキスト形式の場合は内容をプレビュー
        if format == "txt" and isinstance(result, dict):
            text = result.get("text", "")
            preview = text[:200] + "..." if len(text) > 200 else text
            click.echo("【プレビュー】")
            click.echo(preview)
            click.echo()

    except Exception as e:
        click.echo(f"\nエラーが発生しました: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
def info(audio_file):
    """
    音声ファイルの情報を表示

    AUDIO_FILE: 情報を表示する音声ファイルのパス
    """
    try:
        preprocessor = AudioPreprocessor()
        audio_info = preprocessor.get_audio_info(audio_file)

        click.echo(f"\n音声ファイル情報: {audio_file}")
        click.echo("-" * 60)
        click.echo(f"長さ: {audio_info['duration_seconds']:.2f}秒")
        click.echo(f"サンプルレート: {audio_info['frame_rate']}Hz")
        click.echo(f"チャンネル数: {audio_info['channels']}")
        click.echo(
            f"サンプル幅: {audio_info['sample_width']}バイト"
        )
        click.echo(f"ファイルサイズ: {audio_info['file_size_mb']:.2f}MB")

        # Whisper APIの制限チェック
        if audio_info["file_size_mb"] > 25:
            click.echo(
                "\n⚠️  ファイルサイズが25MBを超えています。"
            )
            click.echo(
                "文字起こし時に自動的に分割処理が実行されます。"
            )

        click.echo()

    except Exception as e:
        click.echo(f"\nエラーが発生しました: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
