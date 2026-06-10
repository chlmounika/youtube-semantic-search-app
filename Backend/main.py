import csv
import os
import faiss
import numpy as np
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# MODEL & STORAGE
# ----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384

INDEX_PATH = "index.faiss"
META_PATH = "metadata.npy"

index = None
metadata = []

# ----------------------------
# LOAD / SAVE INDEX
# ----------------------------
def load_index():
    global index, metadata
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(INDEX_PATH)
        metadata = list(np.load(META_PATH, allow_pickle=True))
    else:
        index = faiss.IndexFlatL2(DIM)
        metadata = []

def save_index():
    faiss.write_index(index, INDEX_PATH)
    np.save(META_PATH, np.array(metadata, dtype=object))

load_index()

# ----------------------------
# INGEST CSV
# ----------------------------
@app.post("/ingest")
def ingest_csv():
    global index, metadata

    texts = []
    metadata.clear()
    index.reset()

    with open("kaggle_newembeddings1.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            text = f"{row['title']} {row['channel_title']} {row.get('description','')}"
            texts.append(text)

            metadata.append({
                "video_id": row["video_id"],
                "title": row["title"],
                "channel_title": row["channel_title"],
                "transcript": row.get("transcript", ""),
                "thumbnail": row.get("thumbnail_default", ""),
                "view_count": row.get("viewCount", ""),
                "duration": row.get("duration", "")
            })

    embeddings = model.encode(texts)
    index.add(np.array(embeddings).astype("float32"))
    save_index()

    return {
        "message": "CSV ingested successfully",
        "total_vectors": index.ntotal
    }

# ----------------------------
# SEARCH API
# ----------------------------
@app.get("/search")
def search_videos(query: str, k: int = 5):
    if index.ntotal == 0:
        return {"error": "Vector DB is empty. Ingest CSV first."}

    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        meta = metadata[idx]

        results.append({
            "rank": rank + 1,
            "video_id": meta["video_id"],
            "title": meta["title"],
            "channel_title": meta["channel_title"],
            "similarity": float(1 / (1 + distances[0][rank])),
            "thumbnail": meta["thumbnail"],
            "view_count": meta["view_count"],
            "duration": meta["duration"]
        })

    return {
        "query": query,
        "results": results
    }

# ----------------------------
# SUMMARY API
# ----------------------------
@app.get("/summarize/{video_id}")
def summarize(video_id: str):
    for item in metadata:
        if item["video_id"] == video_id:
            transcript = item.get("transcript", "")

            if not transcript:
                return {"error": "Transcript not found"}

            parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
            summarizer = TextRankSummarizer()

            summary_sentences = summarizer(parser.document, 5)

            summary = " ".join(str(sentence) for sentence in summary_sentences)

            return {
              "video_id": video_id,
               "summary": summary
            }

    return {"error": "Video ID not found"}

