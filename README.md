# Notes Generator with CUDA (Ollama + Whisper)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)]
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)]
[![CUDA](https://img.shields.io/badge/CUDA-Optional-green?logo=nvidia)]
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)]
[![License](https://img.shields.io/badge/License-MIT-yellow)]

A beginner-friendly Flask application that downloads audio (e.g., from YouTube), transcribes it using OpenAI Whisper (PyTorch) with optional CUDA acceleration, and generates structured notes and summaries using a local LLM via Ollama.

---

## Project Description

This project converts audio or video content into useful, human-readable notes without relying on paid APIs.

Workflow:
1. Download or upload audio
2. Transcribe using Whisper
3. Generate notes using Ollama
4. Review and export notes

The pipeline works fully offline (except video downloads).

---

## Features

- Download audio using yt-dlp
- Local Whisper transcription
- Optional CUDA acceleration
- Notes generation using Ollama
- Supports llama3, mistral, phi, gemma
- Flask web UI
- Upload files or paste URLs

---

## Tech Stack

- Python 3.10+
- Flask
- PyTorch
- OpenAI Whisper
- CUDA (optional)
- Ollama
- yt-dlp
- ffmpeg
- HTML/CSS

---

## Prerequisites

- Python 3.10+
- pip
- ffmpeg installed
- Ollama installed and running
- Optional NVIDIA GPU with CUDA

---

## Installing Ollama

Download from https://ollama.com/download

Pull a model:
```bash
ollama pull llama3
```

---

## Installation

```bash
git clone https://github.com/your-username/notes_generator_with_cuda.git
cd notes_generator_with_cuda
python -m venv .venv
source .venv/bin/activate  # or Windows equivalent
pip install -r requirements.txt
```

(Optional CUDA install via PyTorch site)

---

## Usage

Start Ollama:
```bash
ollama serve
```

Run app:
```bash
python run.py
```

Open http://127.0.0.1:5000

---

## Project Structure

notes_generator_with_cuda/
- run.py
- requirements.txt
- app/
  - audio_transcription.py
  - notes_generator.py
  - routes.py
  - templates/
  - static/

---

## Future Enhancements

- Model selection UI
- PDF/Markdown export
- Multi-language support
- Docker support

---

## License

MIT License

---

## Author

Your Name
