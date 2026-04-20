"""
Audio processor for format conversion
Handles conversion between platform formats and STT/TTS requirements
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path


class AudioProcessor:
    """
    Audio format conversion and processing

    Handles:
    - Telegram OGG → WAV (for Whisper)
    - Discord MP3/OGG → WAV (for Whisper)
    - Any → OGG/MP3 (for response)
    """

    def __init__(self, temp_dir: str = None):
        """
        Initialize audio processor

        Args:
            temp_dir: Directory for temporary files (default: system temp)
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.logger = logging.getLogger(__name__)

        # Check FFmpeg availability
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            self.ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.ffmpeg_available = False
            self.logger.warning("FFmpeg not found. Install it for audio conversion.")

    def convert_for_stt(self, input_path: str,
                        output_path: str = None) -> str:
        """
        Convert audio to STT-compatible format (WAV, 16kHz, mono)

        Args:
            input_path: Input audio file path
            output_path: Output path (optional, auto-generate if None)

        Returns:
            Output file path
        """
        if not self.ffmpeg_available:
            self.logger.error("FFmpeg not available for conversion")
            raise RuntimeError("FFmpeg required for audio conversion")

        if output_path is None:
            # Generate temp file
            output_path = os.path.join(
                self.temp_dir,
                f"converted_{os.path.basename(input_path)}.wav"
            )

        # Convert to WAV, 16kHz, mono, 16-bit PCM
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "16000",      # Sample rate
            "-ac", "1",            # Mono
            "-c:a", "pcm_s16le",  # 16-bit PCM
            "-y",                 # Overwrite without asking
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Converted: {input_path} -> {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Conversion failed: {e.stderr.decode()}")
            raise RuntimeError(f"Audio conversion failed: {e}")

    def convert_for_platform(self, input_path: str, platform: str,
                          output_path: str = None) -> str:
        """
        Convert audio for platform output

        Args:
            input_path: Input audio (WAV from TTS)
            platform: Target platform (telegram, discord)
            output_path: Output path (optional)

        Returns:
            Output file path
        """
        if not self.ffmpeg_available:
            # Return as-is if FFmpeg not available
            return input_path

        if output_path is None:
            # Determine format based on platform
            format = "ogg" if platform == "telegram" else "mp3"
            ext = f".{format}"
            output_path = os.path.join(
                self.temp_dir,
                f"response_{os.path.basename(input_path)}{ext}"
            )

        # Convert based on platform
        if platform == "telegram":
            # Telegram prefers OGG Opus
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-c:a", "libopus",
                "-b:a", "64k",
                "-y",
                output_path
            ]
        else:  # discord
            # Discord accepts MP3 or OGG
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-codec:a", "libmp3lame",
                "-b:a", "128k",
                "-y",
                output_path
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Converted for {platform}: {input_path} -> {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Platform conversion failed: {e.stderr.decode()}")
            raise RuntimeError(f"Audio conversion failed: {e}")

    def cleanup(self, pattern: str = None):
        """
        Clean up temporary files

        Args:
            pattern: File pattern to clean (None = all voice_*.wav, converted_*, response_*)
        """
        try:
            if pattern:
                # Clean specific pattern
                for file in Path(self.temp_dir).glob(pattern):
                    file.unlink()
                    self.logger.debug(f"Cleaned: {file}")
            else:
                # Clean all our temp files
                patterns = ["voice_*.wav", "converted_*", "response_*"]
                for p in patterns:
                    for file in Path(self.temp_dir).glob(p):
                        file.unlink()
                        self.logger.debug(f"Cleaned: {file}")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is installed and available

    Returns:
        True if FFmpeg is available
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_ffmpeg_instructions() -> str:
    """
    Get FFmpeg installation instructions for current platform

    Returns:
        Installation instructions
    """
    import platform

    system = platform.system()

    if system == "Windows":
        return """Install FFmpeg on Windows:

1. Download from: https://ffmpeg.org/download.html
2. Extract to C:\\ffmpeg
3. Add C:\\ffmpeg\\bin to PATH

Or use Chocolatey:
    choco install ffmpeg
"""
    elif system == "Darwin":  # macOS
        return """Install FFmpeg on macOS:

Using Homebrew:
    brew install ffmpeg

Using MacPorts:
    sudo port install ffmpeg
"""
    else:  # Linux
        return """Install FFmpeg on Linux:

Debian/Ubuntu:
    sudo apt update
    sudo apt install ffmpeg

Fedora:
    sudo dnf install ffmpeg

Arch:
    sudo pacman -S ffmpeg
"""
