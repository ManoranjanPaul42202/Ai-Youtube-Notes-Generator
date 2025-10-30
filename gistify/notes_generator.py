# # import json
# # from langchain_community.vectorstores import FAISS
# # from langchain_core.messages import HumanMessage, SystemMessage
# # from langchain_ollama import ChatOllama, OllamaEmbeddings
# # from langchain_text_splitters import RecursiveCharacterTextSplitter

# # class NotesGenerator:
# #     def __init__(self, base_url="http://localhost:11434") -> None:
# #         # System & user templates for different note styles
# #         self.system_prompt = """You are an expert note taker. You receive a transcription of a YouTube video. 
# #         Your job is to generate well-structured notes that capture all important ideas clearly."""

# #         self.user_prompts = {
# #             "bullet": """Convert the following transcript into clear, concise bullet point notes.
# #             Each bullet should represent one key idea.
# #             Transcript:
# #             {context}""",

# #             "summary": """Summarize the following transcript into a short but comprehensive summary. 
# #             Use paragraphs and preserve important facts and examples.
# #             Transcript:
# #             {context}""",

# #             "detailed": """Convert the following transcript into structured and detailed notes.
# #             Organize the notes with headings and subheadings like:
# #             I. Introduction
# #             II. Key Concepts
# #             III. Examples
# #             IV. Key Takeaways
# #             Transcript:
# #             {context}"""
# #         }

# #         # Embeddings and LLM setup
# #         self.embeddings = OllamaEmbeddings(
# #             model="nomic-embed-text",
# #             base_url=base_url,
# #         )

# #         self.llm = ChatOllama(
# #             model="llama3.2:3b",
# #             temperature=0.6,
# #             top_k=80,
# #             top_p=0.9,
# #             seed=0,
# #             base_url=base_url,
# #         )

# #     def load_transcript(self, transcript_text: str):
# #         """Store the transcript in memory for processing."""
# #         print("Loading transcript...")
# #         self.transcript = transcript_text
# #         print("Transcript loaded successfully.")
# #         return self.transcript

# #     def split_transcript(self, chunk_size=700, chunk_overlap=50):
# #         """Split transcript into manageable chunks for better embeddings & processing."""
# #         print("Splitting transcript into chunks...")
# #         splitter = RecursiveCharacterTextSplitter(
# #             chunk_size=chunk_size, chunk_overlap=chunk_overlap
# #         )
# #         self.chunks = splitter.create_documents([self.transcript])
# #         print(f"Transcript split into {len(self.chunks)} chunks.")
# #         return self.chunks

# #     def create_index(self):
# #         """Embed transcript chunks and create FAISS vector index."""
# #         print("Creating FAISS Index...")
# #         self.index = FAISS.from_documents(documents=self.chunks, embedding=self.embeddings)
# #         print("Index created successfully.")
# #         return self.index

# #     def get_relevant_chunks(self, topic="", k=5):
# #         """Retrieve top chunks related to a topic (or all if no topic given)."""
# #         if not topic.strip():
# #             # If no specific topic, just use all chunks
# #             return self.chunks
# #         print(f"Retrieving top {k} relevant chunks for topic: {topic}")
# #         return self.index.similarity_search(topic, k=k)

# #     # def generate_notes(self, style="detailed", topic=""):
# #     #     """Generate notes from transcript based on selected style (bullet, summary, detailed)."""
# #     #     if style not in self.user_prompts:
# #     #         raise ValueError(f"Invalid style '{style}'. Must be one of {list(self.user_prompts.keys())}")

# #     #     # Step 1: Retrieve relevant chunks
# #     #     relevant_docs = self.get_relevant_chunks(topic=topic, k=6)
# #     #     context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

# #     #     # Step 2: Build chat messages
# #     #     messages = [
# #     #         SystemMessage(content=self.system_prompt),
# #     #         HumanMessage(content=self.user_prompts[style].format(context=context_text))
# #     #     ]

# #     #     # Step 3: Generate notes using LLM
# #     #     print(f"Generating {style} notes...")
# #     #     result = self.llm.invoke(messages)
# #     #     notes_text = result.content.strip()

# #     #     # Optional: Save notes to file
# #     #     filename = f"notes_{style}.txt"
# #     #     with open(filename, "w", encoding="utf-8") as f:
# #     #         f.write(notes_text)

# #     #     print(f"{style.capitalize()} notes generated and saved as {filename}.")
# #     #     return notes_text

# #     def generate_notes(self, transcript_text: str, style="detailed", topic=""):
# #         """
# #         Generate notes from a given transcript text passed directly from the dashboard.
# #         Style can be one of: 'bullet', 'summary', or 'detailed'.
# #         Optionally, a topic can be provided to focus on specific sections.
# #         """
# #         if style not in self.user_prompts:
# #             raise ValueError(f"Invalid style '{style}'. Must be one of {list(self.user_prompts.keys())}")

# #         # Step 1: Split transcript into chunks (temporary, not stored globally)
# #         splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
# #         chunks = splitter.create_documents([transcript_text])

# #         # Step 2: Create temporary FAISS index from these chunks
# #         index = FAISS.from_documents(documents=chunks, embedding=self.embeddings)

# #         # Step 3: Retrieve relevant chunks (or all if no topic)
# #         if topic.strip():
# #             relevant_docs = index.similarity_search(topic, k=6)
# #         else:
# #             relevant_docs = chunks

# #         context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

# #         # Step 4: Build messages for the LLM
# #         messages = [
# #             SystemMessage(content=self.system_prompt),
# #             HumanMessage(content=self.user_prompts[style].format(context=context_text))
# #         ]

# #         # Step 5: Generate notes using LLM
# #         print(f"Generating {style} notes from provided transcript...")
# #         result = self.llm.invoke(messages)
# #         notes_text = result.content.strip()

# #         # Step 6: Save notes to file (optional)
# #         filename = f"notes_{style}.txt"
# #         with open(filename, "w", encoding="utf-8") as f:
# #             f.write(notes_text)

# #         print(f"{style.capitalize()} notes generated and saved as {filename}.")
# #         return notes_text
# import re
# from langchain_community.vectorstores import FAISS
# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_ollama import ChatOllama, OllamaEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

# class NotesGenerator:
#     def __init__(self, base_url="http://localhost:11434") -> None:
#         # System prompt to guide the LLM
#         self.system_prompt = """You are an expert note taker. You receive a transcription of a YouTube video. 
#         Your job is to generate well-structured notes that capture all important ideas clearly, 
#         including any code snippets or examples. Maintain the formatting of code blocks."""

#         # User prompts for different note styles
#         self.user_prompts = {
#             "bullet": """Convert the following transcript into concise, clear bullet point notes.
#             Each bullet should capture one key idea or code snippet.
#             Transcript:
#             {context}""",

#             "summary": """Summarize the following transcript into a short, comprehensive summary.
#             Include important examples and code snippets as needed.
#             Transcript:
#             {context}""",

#             "detailed": """
#             You are an expert note taker and educator. You receive a transcript of a YouTube video that may contain concepts, examples, explanations, and code snippets. 
#             Your task is to generate extremely detailed and comprehensive notes that:

#             1. Include **all concepts, explanations, and examples** — do not skip anything.
#             2. Include **all code blocks exactly as they appear**, preserving formatting and indentation.
#             3. Explain every code snippet line by line if applicable.
#             4. Use **headings and subheadings** for sections and subsections.
#             5. Include **bullets, numbered lists, or tables** wherever it improves clarity.
#             6. Add **context for examples** so the reader understands why each concept is important.
#             7. Provide **key takeaways at the end of each section**.
#             8. Keep the notes readable and structured like a textbook or study guide.

#             Do **not summarize or shorten** the content. Every concept, example, and code snippet must be included.

#             Transcript:
#             {context}
#             """
#         }

#         # Embeddings and LLM
#         self.embeddings = OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=base_url
#         )

#         self.llm = ChatOllama(
#             model="llama3.2:3b",
#             temperature=0.5,
#             top_k=80,
#             top_p=0.9,
#             seed=0,
#             base_url=base_url
#         )

#     def split_transcript(self, transcript_text: str, chunk_size=700, chunk_overlap=50):
#         """
#         Split transcript into chunks for embeddings.
#         This splitter ensures code blocks are preserved together.
#         """
#         # Preprocess: separate code blocks and text
#         code_blocks = re.findall(r"```[\s\S]*?```", transcript_text)
#         text_only = re.sub(r"```[\s\S]*?```", "\nCODEBLOCKPLACEHOLDER\n", transcript_text)

#         # Split the text only parts
#         splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#         text_chunks = splitter.create_documents([text_only])

#         # Inject code blocks back into chunks
#         final_chunks = []
#         code_idx = 0
#         for chunk in text_chunks:
#             content = chunk.page_content
#             while "CODEBLOCKPLACEHOLDER" in content and code_idx < len(code_blocks):
#                 content = content.replace("CODEBLOCKPLACEHOLDER", code_blocks[code_idx], 1)
#                 code_idx += 1
#             final_chunks.append(chunk.__class__(page_content=content))

#         print(f"Transcript split into {len(final_chunks)} chunks with code preserved.")
#         return final_chunks

#     def create_index(self, chunks):
#         """Create a FAISS index from transcript chunks."""
#         print("Creating FAISS index...")
#         index = FAISS.from_documents(documents=chunks, embedding=self.embeddings)
#         print("FAISS index created.")
#         return index

#     def get_relevant_chunks(self, index, topic="", k=5, chunks=None):
#         """Retrieve top chunks related to a topic (or all if no topic given)."""
#         if topic.strip() and index:
#             print(f"Searching top {k} relevant chunks for topic: {topic}")
#             return index.similarity_search(topic, k=k)
#         else:
#             # If no topic provided, return all chunks
#             return chunks

#     def generate_notes(self, transcript_text: str, style="detailed", topic=""):
#         """
#         Generate notes from a transcript text, preserving code and all concepts.
#         """
#         if style not in self.user_prompts:
#             raise ValueError(f"Invalid style '{style}'. Must be one of {list(self.user_prompts.keys())}")

#         # Step 1: Split transcript into chunks with code preserved
#         chunks = self.split_transcript(transcript_text)

#         # Step 2: Create FAISS index
#         index = self.create_index(chunks)

#         # Step 3: Get relevant chunks
#         relevant_docs = self.get_relevant_chunks(index, topic=topic, k=6, chunks=chunks)
#         context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

#         # Step 4: Build messages for LLM
#         messages = [
#             SystemMessage(content=self.system_prompt),
#             HumanMessage(content=self.user_prompts[style].format(context=context_text))
#         ]

#         # Step 5: Generate notes
#         print(f"Generating {style} notes...")
#         result = self.llm.invoke(messages)
#         notes_text = result.content.strip()

#         # Step 6: Save notes to file
#         filename = f"notes_{style}.txt"
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(notes_text)
#         print(f"{style.capitalize()} notes saved as {filename}.")

#         return notes_text

import re
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class NotesGenerator:
    def __init__(self, base_url="http://localhost:11434") -> None:
        # System prompt to guide the LLM
        self.system_prompt = """You are an expert note taker. You receive a transcript of a YouTube video. 
        Your job is to generate well-structured, extremely detailed notes that capture all ideas clearly,
        including code snippets, explanations, and examples. Preserve all formatting for code blocks."""

        # User prompts for different note styles
        self.user_prompts = {
            "detailed": """
            You are an expert educator creating detailed study notes from a transcript. 
            For this chunk of the transcript:

            1. Include **all concepts, explanations, examples, and code snippets**.
            2. Preserve formatting for code blocks exactly.
            3. Explain code snippets line by line if applicable.
            4. Use headings, subheadings, bullets, or numbered lists for clarity.
            5. Include key takeaways for this chunk.
            6. Do **not summarize or skip content**; expand wherever possible.

            Transcript chunk:
            {context}
            """
        }

        # Embeddings and LLM setup
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=base_url
        )
        self.llm = ChatOllama(
            model="llama3.2:3b",
            temperature=0.5,
            top_k=50,
            top_p=0.8,
            seed=0,
            base_url=base_url
        )

    def split_transcript(self, transcript_text: str, chunk_size=5000, chunk_overlap=200):
        """
        Split transcript into fewer, larger chunks while preserving code blocks.
        """
        code_blocks = re.findall(r"```[\s\S]*?```", transcript_text)
        text_only = re.sub(r"```[\s\S]*?```", "\nCODEBLOCKPLACEHOLDER\n", transcript_text)

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        text_chunks = splitter.create_documents([text_only])

        final_chunks = []
        code_idx = 0
        for chunk in text_chunks:
            content = chunk.page_content
            while "CODEBLOCKPLACEHOLDER" in content and code_idx < len(code_blocks):
                content = content.replace("CODEBLOCKPLACEHOLDER", code_blocks[code_idx], 1)
                code_idx += 1
            final_chunks.append(chunk.__class__(page_content=content))

        print(f"Transcript split into {len(final_chunks)} larger chunks with code preserved.")
        return final_chunks

    def generate_notes_for_chunks(self, chunks, style="detailed"):
        """
        Generate notes for each chunk individually and merge them.
        """
        all_notes = []

        for i, chunk in enumerate(chunks, start=1):
            print(f"Generating notes for chunk {i}/{len(chunks)}...")
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=self.user_prompts[style].format(context=chunk.page_content))
            ]
            result = self.llm.invoke(messages)
            chunk_notes = result.content.strip()
            all_notes.append(f"### Chunk {i} Notes ###\n{chunk_notes}\n\n")

        # Merge all chunk notes into one
        merged_notes = "\n".join(all_notes)

        # Save to file
        filename = f"notes_{style}_merged.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(merged_notes)

        print(f"Merged {style} notes saved as {filename}.")
        return merged_notes

    def generate_notes(self, transcript_text: str, style="detailed"):
        """
        Main method: split transcript, generate notes per chunk, and merge.
        """
        chunks = self.split_transcript(transcript_text)
        merged_notes = self.generate_notes_for_chunks(chunks, style=style)
        return merged_notes

