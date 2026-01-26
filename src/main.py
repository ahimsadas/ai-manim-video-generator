#!/usr/bin/env python3
"""AI Video Generator - Create Manim animations from natural language prompts."""

import sys
from pathlib import Path

from src.llm import LLMClient
from src.video import VideoGenerator


def main():
    """Main entry point for the AI Video Generator."""
    print("=" * 60)
    print("  AI Video Generator - Manim Animation Creator")
    print("=" * 60)
    print()

    # Get user prompt
    print("What would you like to create a video about?")
    print("(Describe the animation you want, e.g., 'Explain the Pythagorean theorem')")
    print()

    try:
        user_prompt = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting...")
        sys.exit(0)

    if not user_prompt:
        print("Error: Please provide a description for your video.")
        sys.exit(1)

    print()
    print("-" * 60)
    print("Generating Manim code...")

    # Initialize clients
    try:
        llm_client = LLMClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    video_generator = VideoGenerator()

    # Generate Manim code
    try:
        manim_code = llm_client.generate_manim_code(user_prompt)
        print("Manim code generated successfully.")
        print()
        print("Generated code preview:")
        print("-" * 40)
        # Show first 20 lines
        lines = manim_code.split("\n")
        preview = "\n".join(lines[:20])
        if len(lines) > 20:
            preview += f"\n... ({len(lines) - 20} more lines)"
        print(preview)
        print("-" * 40)
        print()
    except Exception as e:
        print(f"Error generating code: {e}")
        sys.exit(1)

    # Generate video
    print("Rendering video with Manim...")
    print("(This may take a few moments)")
    print()

    try:
        video_path = video_generator.generate(manim_code)
        print("-" * 60)
        print("Video generated successfully!")
        print(f"Output: {video_path}")
        print("-" * 60)
    except RuntimeError as e:
        print(f"Error generating video: {e}")
        print()
        print("The generated code may have errors. Here's the full code:")
        print("=" * 40)
        print(manim_code)
        print("=" * 40)
        sys.exit(1)

    return video_path


if __name__ == "__main__":
    main()
