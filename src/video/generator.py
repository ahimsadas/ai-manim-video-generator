import subprocess
import uuid
from pathlib import Path

from src.config import OUTPUT_DIR, GENERATED_SCENES_DIR, VIDEO_QUALITY, QUALITY_FLAGS


class VideoGenerator:
    """Handles Manim code execution and video generation."""

    def __init__(self, quality: str | None = None):
        self.quality = quality or VIDEO_QUALITY
        self.quality_flag = QUALITY_FLAGS.get(self.quality, "-qm")

    def generate(self, manim_code: str) -> Path:
        """Generate a video from Manim code.

        Args:
            manim_code: Valid Manim Python code with a GeneratedScene class

        Returns:
            Path to the generated video file

        Raises:
            RuntimeError: If Manim execution fails
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
                raise RuntimeError(
                    f"Manim execution failed:\n{result.stderr}\n{result.stdout}"
                )

            # Find the generated video file
            video_path = self._find_generated_video(scene_id)

            if video_path is None:
                raise RuntimeError(
                    f"Video generation completed but output file not found.\n"
                    f"Manim output: {result.stdout}"
                )

            return video_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Manim execution timed out after 5 minutes")
        finally:
            # Clean up the scene file (optional - keep for debugging)
            # scene_file.unlink(missing_ok=True)
            pass

    def _find_generated_video(self, scene_id: str) -> Path | None:
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
