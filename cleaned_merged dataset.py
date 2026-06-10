# task2_add_transcripts_clean.py
import pandas as pd
import re
import time
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

INPUT_CSV = "kaggle_50_videos.csv"            # should be inside the same folder
OUTPUT_CSV = "kaggle_50_videos_cleaned.csv"   # final output

# ---------- helpers ----------
def iso8601_to_seconds(s):
    if not isinstance(s, str) or not s.startswith("PT"):
        return None
    h = m = sec = 0
    mobj = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    if not mobj:
        return None
    if mobj.group(1): h = int(mobj.group(1))
    if mobj.group(2): m = int(mobj.group(2))
    if mobj.group(3): sec = int(mobj.group(3))
    return h*3600 + m*60 + sec

def clean_colname(name):
    name = re.sub(r"[^\w\s]", "", str(name))
    name = re.sub(r"\s+", "_", name.strip())
    return name.lower()

def clean_transcript_text(text):
    if pd.isna(text) or text is None:
        return ""
    s = str(text).lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def fetch_transcript_for_video(video_id, pause=0.05):
    try:
        segs = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([seg.get("text","") for seg in segs])
        time.sleep(pause)
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        return ""
    except Exception:
        return ""

# ---------- main ----------
def main():
    print("Loading", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV, dtype=str)
    print("Initial shape:", df.shape)

    # Normalize column names
    original_cols = list(df.columns)
    rename_map = {c: clean_colname(c) for c in original_cols}
    df.rename(columns=rename_map, inplace=True)
    print("Columns after normalizing:", df.columns.tolist())

    # Ensure id column exists
    if "id" not in df.columns:
        candidates = ["video_id","videoid","vid","video"]
        for cand in candidates:
            if cand in df.columns:
                df.rename(columns={cand: "id"}, inplace=True)
                print(f"Renamed {cand} -> id")
                break

    if "id" not in df.columns:
        raise SystemExit("ERROR: no 'id' column found in CSV. Rename your ID column to 'id' and re-run.")

    # Fetch transcripts if not present
    if "transcript" not in df.columns:
        print("Fetching transcripts (this may take several minutes)...")
        transcripts = []
        for i, vid in enumerate(df["id"].tolist()):
            vid = str(vid).strip()
            if vid == "" or vid.lower() in ["nan", "none"]:
                transcripts.append("")
                continue
            txt = fetch_transcript_for_video(vid, pause=0.05)
            transcripts.append(txt)
            if (i+1) % 10 == 0:
                print(f"  fetched transcripts for {i+1}/{len(df)} videos")
        df["transcript"] = transcripts
    else:
        df["transcript"] = df["transcript"].fillna("")

    # Clean transcript
    print("Cleaning transcripts...")
    df["transcript"] = df["transcript"].apply(clean_transcript_text)

    # Final column cleanup: remove special chars and lowercase in column names
    df.rename(columns={c: clean_colname(c) for c in df.columns}, inplace=True)

    # Convert duration -> seconds if present
    if "duration" in df.columns:
        print("Converting duration to seconds...")
        df["duration_seconds"] = df["duration"].apply(iso8601_to_seconds)
    else:
        print("No 'duration' column found; skipping duration conversion.")

    # Clean text columns
    text_cols = [c for c in ["title","description","tags","channel_title","channel_description"] if c in df.columns]
    print("Cleaning text columns:", text_cols)
    for c in text_cols:
        df[c] = df[c].fillna("").astype(str).apply(lambda s: re.sub(r"[^a-z0-9\s]", " ", s.lower()).strip())

    # Remove duplicates by id
    before = len(df)
    df = df.drop_duplicates(subset=["id"], keep="first")
    after = len(df)
    print(f"Removed {before-after} duplicates (by id). Final shape: {df.shape}")

    # Save final CSV
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print("Saved cleaned CSV:", OUTPUT_CSV)

if __name__ == "__main__":
    main()