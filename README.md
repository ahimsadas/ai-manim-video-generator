# AI Manim Video Generator

Generate 2D mathematical and educational animations using natural language prompts. Powered by Manim and LLM-based code generation.

## Features

- Natural language to Manim animation pipeline
- 3Blue1Brown-inspired visual style
- Configurable video quality settings
- Clean, modular architecture ready for RAG integration (V2)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Run the generator:**
   ```bash
   python -m src.main
   ```

## Configuration

Set these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `LLM_MODEL` | Model for code generation | `xiaomi/mimo-v2-flash` |
| `VIDEO_QUALITY` | Output quality | `production_quality` |

Quality options: `low_quality`, `medium_quality`, `high_quality`, `production_quality`

## Project Structure

```
ai-video-generator/
├── src/
│   ├── main.py          # CLI entry point
│   ├── config.py        # Configuration
│   ├── llm/
│   │   ├── client.py    # OpenRouter API client
│   │   └── prompts.py   # Manim generation prompts
│   ├── video/
│   │   └── generator.py # Manim execution
│   └── rag/             # V2: RAG integration (placeholder)
├── output/              # Generated videos
├── generated_scenes/    # Generated Manim code files
└── requirements.txt
```

## Usage Example

```bash
$ python -m src.main

What would you like to create a video about?
> Explain the Pythagorean theorem with a visual proof

Generating Manim code...
Rendering video with Manim...
Video generated successfully!
Output: output/media/videos/scene_abc123/1080p60/GeneratedScene.mp4
```

## Roadmap

- **V1** (Current): Basic prompt → LLM → Manim pipeline
- **V2**: RAG integration for context-aware generation
