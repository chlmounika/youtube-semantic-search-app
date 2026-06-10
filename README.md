# QueryTube_Infosys_Internship_NOV25
AI_SemanticSearchTube. Building a Semantic Search App with YouTube Data

# 📺 YouTube AI Explorer

YouTube AI Explorer is a web-based application that allows users to ingest YouTube video metadata, search videos using AI-based similarity, and generate short summaries from video transcripts.

## 🚀 Features

- 📥 **Ingest CSV**
  - Upload YouTube metadata CSV file
  - Stores embeddings and metadata for search

- 🔍 **AI Search**
  - Search top 5 relevant YouTube videos
  - Results displayed in card format
  - Click on thumbnail to open YouTube video

- 📝 **Video Summary**
  - Generates medium-length summary from transcript
  - Adjustable summary length
  - Fast and lightweight (no heavy NLP models)

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- Vector Search (Embeddings)

### Frontend
- HTML
- CSS
- JavaScript (Fetch API)
- 
## ⚙️ Installation & Setup

### 1️⃣ Install Dependencies
```bash
pip install fastapi uvicorn

2️⃣ Run Backend Server
uvicorn main:app --reload
Server will start at:
http://127.0.0.1:8000

🌐 Frontend Usage
Open frontend.html in browser
Go to INGEST tab → Upload CSV
Go to SEARCH tab → Enter query
Click on a video card → Opens YouTube
Go to SUMMARY tab → Enter Video ID
📌 API Endpoints
Ingest CSV
POST /ingest
Search Videos
GET /search?query=machine learning&k=5
Video Summary
GET /summarize/{video_id}?max_sentences=4
🎯 Output Example
{
  "video_id": "7IgVGSaQPaw",
  "summary": "Machine Learning Engineering requires mastering several essential skills. A strong foundation in Python is crucial, along with version control using Git. Knowledge of data structures, algorithms, and SQL helps in handling large datasets efficiently. Mathematics and statistics form the backbone of machine learning concepts. Data preprocessing and visualization using tools like Pandas, NumPy, and Matplotlib are important before model building. Core machine learning concepts such as supervised and unsupervised learning, along with libraries like Scikit-learn, TensorFlow, and PyTorch, must be learned. Advanced topics include deep learning, NLP, and computer vision. Finally, deploying models using Flask/Django and Docker is essential to apply models in real-world applications."
}


