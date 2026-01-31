import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.config import OUTPUT_DIR, GENERATED_SCENES_DIR, VIDEO_QUALITY, QUALITY_FLAGS


@dataclass
class GenerationResult:
    """Result of a video generation attempt."""
    success: bool
    video_path: Optional[Path] = None
    error: Optional[str] = None
    scene_file: Optional[Path] = None


class VideoGenerator:
    """Handles Manim code execution and video generation."""

    def __init__(self, quality: str = None):
        self.quality = quality or VIDEO_QUALITY
        self.quality_flag = QUALITY_FLAGS.get(self.quality, "-qm")

    def generate(self, manim_code: str) -> GenerationResult:
        """Generate a video from Manim code.

        Args:
            manim_code: Valid Manim Python code with a GeneratedScene class

        Returns:
            GenerationResult with success status, video path, or error message
        """
        # Create a unique filename for this generation
        scene_id = uuid.uuid4().hex[:8]
        scene_file = GENERATED_SCENES_DIR / f"scene_{scene_id}.py"

        # Write the code to a file
        scene_file.write_text(manim_code)

        try:
            # Run Manim to generate the video
            result = subprocess.run(
                [
                    "manim",
                    self.quality_flag,
                    str(scene_file),
                    "GeneratedScene",
                    "--media_dir", str(OUTPUT_DIR / "media"),
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                # Extract the most relevant error info
                error_msg = self._extract_error(result.stderr, result.stdout)
                return GenerationResult(
                    success=False,
                    error=error_msg,
                    scene_file=scene_file
                )

            # Find the generated video file
            video_path = self._find_generated_video(scene_id)

            if video_path is None:
                return GenerationResult(
                    success=False,
                    error=f"Video generation completed but output file not found.\nManim output: {result.stdout}",
                    scene_file=scene_file
                )

            return GenerationResult(
                success=True,
                video_path=video_path,
                scene_file=scene_file
            )

        except subprocess.TimeoutExpired:
            return GenerationResult(
                success=False,
                error="Manim execution timed out after 5 minutes",
                scene_file=scene_file
            )

    def _extract_error(self, stderr: str, stdout: str) -> str:
        """Extract the most relevant error message from Manim output."""
        # Combine stderr and stdout
        full_output = f"{stderr}\n{stdout}"

        # Look for common error patterns
        lines = full_output.split('\n')
        error_lines = []
        capture = False

        for line in lines:
            # Start capturing at traceback or error indicators
            if 'Traceback' in line or 'Error' in line or 'Exception' in line:
                capture = True
            if capture:
                error_lines.append(line)
            # Also capture AttributeError, TypeError, etc.
            if 'AttributeError:' in line or 'TypeError:' in line or 'NameError:' in line:
                error_lines.append(line)

        if error_lines:
            # Limit to last 30 lines to avoid huge error messages
            return '\n'.join(error_lines[-30:])

        # Fallback to full output (truncated)
        return full_output[-2000:] if len(full_output) > 2000 else full_output

    def _find_generated_video(self, scene_id: str) -> Optional[Path]:
        """Find the generated video file in the media directory."""
        media_dir = OUTPUT_DIR / "media" / "videos" / f"scene_{scene_id}"

        if not media_dir.exists():
            return None

        # Look for .mp4 files in quality subdirectories
        for quality_dir in media_dir.iterdir():
            if quality_dir.is_dir():
                for video_file in quality_dir.glob("*.mp4"):
                    return video_file

        return None
