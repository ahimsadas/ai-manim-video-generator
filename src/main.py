#!/usr/bin/env python3
"""AI Video Generator - Create Manim animations from natural language prompts."""

import sys
from pathlib import Path

from src.llm import LLMClient
from src.video import VideoGenerator


MAX_RETRIES = 3


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

    # Initialize clients
    try:
        llm_client = LLMClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    video_generator = VideoGenerator()

    # Generate script and code (two-phase)
    print("Starting two-phase generation...")
    print()
    try:
        manim_code = llm_client.generate_manim_code(user_prompt)
        print("Code generation complete.")
    except Exception as e:
        print(f"Error generating code: {e}")
        sys.exit(1)

    # Retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\nAttempt {attempt}/{MAX_RETRIES}: Rendering video...")

        # Show code preview
        lines = manim_code.split("\n")
        preview = "\n".join(lines[:15])
        if len(lines) > 15:
            preview += f"\n... ({len(lines) - 15} more lines)"
        print(f"\nCode preview:\n{'-' * 40}\n{preview}\n{'-' * 40}")

        # Try to generate video
        result = video_generator.generate(manim_code)

        if result.success:
            print()
            print("=" * 60)
            print("Video generated successfully!")
            print(f"Output: {result.video_path}")
            print("=" * 60)
            return result.video_path

        # Failed - show error
        print(f"\nError on attempt {attempt}:")
        print(result.error[:500] if len(result.error) > 500 else result.error)

        if attempt < MAX_RETRIES:
            print(f"\nAsking LLM to fix the code...")
            try:
                manim_code = llm_client.fix_code(manim_code, result.error)
                print("Received fixed code.")
            except Exception as e:
                print(f"Error getting fix from LLM: {e}")
                break

    # All retries exhausted
    print()
    print("=" * 60)
    print(f"Failed to generate video after {MAX_RETRIES} attempts.")
    print("The generated code has errors that couldn't be automatically fixed.")
    print()
    print("Last generated code:")
    print("=" * 40)
    print(manim_code)
    print("=" * 40)
    sys.exit(1)


if __name__ == "__main__":
    main()
