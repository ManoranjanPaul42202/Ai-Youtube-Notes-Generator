import json
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class NotesGenerator:
    def __init__(self, base_url="http://localhost:11434") -> None:
        # System & user templates for different note styles
        self.system_prompt = """You are an expert note taker. You receive a transcription of a YouTube video. 
        Your job is to generate well-structured notes that capture all important ideas clearly."""

        self.user_prompts = {
            "bullet": """Convert the following transcript into clear, concise bullet point notes.
            Each bullet should represent one key idea.
            Transcript:
            {context}""",

            "summary": """Summarize the following transcript into a short but comprehensive summary. 
            Use paragraphs and preserve important facts and examples.
            Transcript:
            {context}""",

            "detailed": """Convert the following transcript into structured and detailed notes.
            Organize the notes with headings and subheadings like:
            I. Introduction
            II. Key Concepts
            III. Examples
            IV. Key Takeaways
            Transcript:
            {context}"""
        }

        # Embeddings and LLM setup
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=base_url,
        )

        self.llm = ChatOllama(
            model="llama3.2:3b",
            temperature=0.6,
            top_k=80,
            top_p=0.9,
            seed=0,
            base_url=base_url,
        )

    def load_transcript(self, transcript_text: str):
        """Store the transcript in memory for processing."""
        print("Loading transcript...")
        self.transcript = transcript_text
        print("Transcript loaded successfully.")
        return self.transcript

    def split_transcript(self, chunk_size=700, chunk_overlap=50):
        """Split transcript into manageable chunks for better embeddings & processing."""
        print("Splitting transcript into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self.chunks = splitter.create_documents([self.transcript])
        print(f"Transcript split into {len(self.chunks)} chunks.")
        return self.chunks

    def create_index(self):
        """Embed transcript chunks and create FAISS vector index."""
        print("Creating FAISS Index...")
        self.index = FAISS.from_documents(documents=self.chunks, embedding=self.embeddings)
        print("Index created successfully.")
        return self.index

    def get_relevant_chunks(self, topic="", k=5):
        """Retrieve top chunks related to a topic (or all if no topic given)."""
        if not topic.strip():
            # If no specific topic, just use all chunks
            return self.chunks
        print(f"Retrieving top {k} relevant chunks for topic: {topic}")
        return self.index.similarity_search(topic, k=k)

    # def generate_notes(self, style="detailed", topic=""):
    #     """Generate notes from transcript based on selected style (bullet, summary, detailed)."""
    #     if style not in self.user_prompts:
    #         raise ValueError(f"Invalid style '{style}'. Must be one of {list(self.user_prompts.keys())}")

    #     # Step 1: Retrieve relevant chunks
    #     relevant_docs = self.get_relevant_chunks(topic=topic, k=6)
    #     context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    #     # Step 2: Build chat messages
    #     messages = [
    #         SystemMessage(content=self.system_prompt),
    #         HumanMessage(content=self.user_prompts[style].format(context=context_text))
    #     ]

    #     # Step 3: Generate notes using LLM
    #     print(f"Generating {style} notes...")
    #     result = self.llm.invoke(messages)
    #     notes_text = result.content.strip()

    #     # Optional: Save notes to file
    #     filename = f"notes_{style}.txt"
    #     with open(filename, "w", encoding="utf-8") as f:
    #         f.write(notes_text)

    #     print(f"{style.capitalize()} notes generated and saved as {filename}.")
    #     return notes_text

    def generate_notes(self, transcript_text: str, style="detailed", topic=""):
        """
        Generate notes from a given transcript text passed directly from the dashboard.
        Style can be one of: 'bullet', 'summary', or 'detailed'.
        Optionally, a topic can be provided to focus on specific sections.
        """
        if style not in self.user_prompts:
            raise ValueError(f"Invalid style '{style}'. Must be one of {list(self.user_prompts.keys())}")

        # Step 1: Split transcript into chunks (temporary, not stored globally)
        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
        chunks = splitter.create_documents([transcript_text])

        # Step 2: Create temporary FAISS index from these chunks
        index = FAISS.from_documents(documents=chunks, embedding=self.embeddings)

        # Step 3: Retrieve relevant chunks (or all if no topic)
        if topic.strip():
            relevant_docs = index.similarity_search(topic, k=6)
        else:
            relevant_docs = chunks

        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Step 4: Build messages for the LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self.user_prompts[style].format(context=context_text))
        ]

        # Step 5: Generate notes using LLM
        print(f"Generating {style} notes from provided transcript...")
        result = self.llm.invoke(messages)
        notes_text = result.content.strip()

        # Step 6: Save notes to file (optional)
        filename = f"notes_{style}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(notes_text)

        print(f"{style.capitalize()} notes generated and saved as {filename}.")
        return notes_text

