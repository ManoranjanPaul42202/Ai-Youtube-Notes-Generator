# import torch
# print("CUDA available:", torch.cuda.is_available())
# print("Device:", torch.cuda.get_device_name(0))

from notes_generator import NotesGenerator

# Initialize generator
ng = NotesGenerator()

# 1. Load transcript (e.g., from Whisper output)
with open("transcript.txt", "r", encoding="utf-8") as f:
    transcript_text = f.read()

ng.load_transcript(transcript_text)

# 2. Prepare index
ng.split_transcript()
ng.create_index()

# 3. Generate notes
bullet_notes = ng.generate_notes(style="bullet")
summary_notes = ng.generate_notes(style="summary")
detailed_notes = ng.generate_notes(style="detailed", topic="Deep Learning")


