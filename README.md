# 🏥 Healthcare AI Chatbot

A full-featured Healthcare AI Assistant built with **Streamlit**, **Hugging Face Transformers**, and **SQLite**.

## ✨ Features

| Feature | Description |
|---|---|
| 💬 FAQ Chatbot | Conversational AI for general health questions |
| 🔬 Disease Explainer | Plain-English explanations of any disease |
| 💊 Medicine Lookup | Drug info, side effects & interactions |
| 📄 Report Summarizer | Upload PDF/image reports → AI summary |
| 📊 History Dashboard | SQLite-backed query history & stats |

The app is locked to a single professional dark theme (`.streamlit/config.toml`)
so colors are always readable — no light/dark contrast bugs.

## 🚀 Run locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
streamlit run app.py
```

Opens at http://localhost:8501

## 🚢 Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (see commands below).
2. Go to https://share.streamlit.io → **New app**.
3. Pick your repo, branch `main`, main file `app.py`.
4. Deploy. `packages.txt` (tesseract-ocr) and `requirements.txt` are picked up automatically.

First load will take a minute while the AI model downloads — this is normal.

## 📁 Project Structure

```
healthcare_chatbot/
├── app.py
├── requirements.txt
├── packages.txt
├── .streamlit/config.toml
├── pages/
│   ├── 1_💬_FAQ_Chatbot.py
│   ├── 2_🔬_Disease_Explainer.py
│   ├── 3_💊_Medicine_Lookup.py
│   ├── 4_📄_Report_Summarizer.py
│   └── 5_📊_History.py
├── utils/
│   ├── styles.py
│   ├── ai_model.py
│   ├── database.py
│   └── report_parser.py
└── data/   (SQLite db, auto-created)
```

## ⚠️ Disclaimer

Educational / portfolio project only — not a substitute for professional medical advice.

## 📄 License

MIT
