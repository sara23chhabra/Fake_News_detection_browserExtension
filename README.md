# AI-Based Fake News Credibility Analyzer

A fully free, local-running browser extension (Chrome & Edge compatible) that analyzes online news articles to estimate their credibility based on source reputation, writing quality, and cross-source verification.

> ⚠️ **Disclaimer**: This tool estimates credibility based on journalistic indicators and independent reporting frequency. It does **not** perform absolute fact verification or claim that any article is definitively true or false.

## Features

- 📊 **Source Reputation Analysis** - Evaluates credibility based on the news source's track record
- ⚡ **Sensationalism Detection** - Identifies clickbait phrases, emotional language, and excessive formatting
- ✓ **Cross-Source Corroboration** - Checks if the story is reported by multiple independent trusted sources
- 📝 **Article Summarization** - Generates concise 2-4 sentence summaries using AI
- 🎯 **Explainable Scoring** - Transparent breakdown of how the score is calculated

## System Architecture

┌─────────────────────────────────────────────────────────────┐
│                    Browser Extension                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ popup.js │  │popup.html│  │background│  │ content  │    │
│  │          │  │          │  │   .js    │  │script.js │    │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────┘    │
│       │                                                      │
└───────┼──────────────────────────────────────────────────────┘
        │ HTTP POST /analyze
        ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    main.py (FastAPI)                  │   │
│  └──────────────────────────────────────────────────────┘   │
│       │              │              │              │         │
│  ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐  │
│  │extractor│  │summarizer │  │sensatio-│  │corroboration│  │
│  │   .py   │  │    .py    │  │nalism.py│  │     .py     │  │
│  └─────────┘  └───────────┘  └─────────┘  └─────────────┘  │
│       │                            │              │         │
│  ┌────▼────────────────────────────▼──────────────▼────┐   │
│  │                  credibility.py                      │   │
│  │         Final Score = Source - Penalty + Bonus       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Chrome or Microsoft Edge browser
- pip (Python package manager)

### Step 1: Set Up the Backend

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Step 2: Install the Browser Extension

1. **Open Chrome/Edge extensions page:**
   - Chrome: Navigate to `chrome://extensions/`
   - Edge: Navigate to `edge://extensions/`

2. **Enable Developer Mode:**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the extension:**
   - Click "Load unpacked"
   - Select the `extension` folder from this project

4. **Pin the extension:**
   - Click the puzzle piece icon in the toolbar
   - Pin "Fake News Credibility Analyzer"

## Usage

1. Navigate to any news article in your browser
2. Click the Credibility Analyzer extension icon
3. Wait for the analysis to complete (may take a few seconds on first use as the AI model loads)
4. View the results:
   - **Credibility Score** (0-100)
   - **Label** (High / Medium / Low)
   - **Summary** of the article
   - **Score Breakdown** showing each factor

## How Credibility is Calculated

### Formula
```
Final Score = Source Reputation - Sensationalism Penalty + Corroboration Bonus
```

### Components

| Component | Range | Description |
|-----------|-------|-------------|
| **Source Reputation** | 0-100 | Base score from source database |
| **Sensationalism Penalty** | 0-30 | Deducted for clickbait/emotional language |
| **Corroboration Bonus** | 0-15 | Added when story is verified by other sources |

### Credibility Labels

| Score | Label | Interpretation |
|-------|-------|----------------|
| 75-100 | **High** | Article appears credible |
| 50-74 | **Medium** | Exercise caution, verify claims |
| 0-49 | **Low** | Significant credibility concerns |

### Source Categories

| Category | Score Range | Examples |
|----------|-------------|----------|
| Trusted | 85-95 | BBC, Reuters, The Hindu |
| Moderate | 60-75 | Regional news outlets |
| Low Reliability | 30-50 | Tabloids |
| Satire | 10-20 | The Onion, Babylon Bee |

### Sensationalism Indicators

- Clickbait phrases ("You won't believe...", "SHOCKING...")
- Excessive capitalization (>50% caps in title)
- Multiple exclamation marks (!!)
- Emotional/sensational words

### Cross-Source Verification

The system searches RSS feeds from trusted sources to check if the same story is being reported independently:

- **3+ sources confirm**: +15 bonus
- **1-2 sources confirm**: +5 bonus
- **No confirmation**: 0 (no penalty applied)

## API Reference

### POST /analyze

Analyze an article for credibility.

**Request:**
```json
{
  "url": "https://example.com/news-article"
}
```

**Response:**
```json
{
  "title": "Article Title",
  "summary": "2-4 sentence summary...",
  "credibility_score": 74,
  "credibility_label": "Medium",
  "source_score": 60,
  "sensationalism_penalty": 8,
  "corroboration_bonus": 20,
  "corroborated_sources": ["bbc.com", "thehindu.com"],
  "explanation": "Detailed explanation..."
}
```

### GET /health

Check if the backend is running.

## Project Structure

```
DTL new-version/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── extractor.py         # Article extraction (newspaper3k)
│   ├── summarizer.py        # Text summarization (HuggingFace)
│   ├── credibility.py       # Score calculation
│   ├── sensationalism.py    # Clickbait detection
│   ├── corroboration.py     # Cross-source verification
│   ├── sources.py           # Source reputation database
│   └── requirements.txt     # Python dependencies
├── extension/
│   ├── manifest.json        # Extension config (Manifest V3)
│   ├── popup.html           # UI layout
│   ├── popup.js             # UI logic
│   ├── popup.css            # Styling
│   ├── content_script.js    # Page interaction
│   ├── background.js        # Service worker
│   └── icons/               # Extension icons
└── README.md
```

## Technical Details

### Technologies Used

- **Backend**: Python, FastAPI, Uvicorn
- **Article Extraction**: newspaper3k
- **Summarization**: HuggingFace Transformers (BART/T5)
- **RSS Parsing**: feedparser
- **Browser Extension**: Manifest V3, Chrome APIs

### Performance Notes

- First analysis may take 30-60 seconds as the ML model loads
- Subsequent analyses are faster (5-15 seconds)
- Corroboration check adds ~2-5 seconds
- Use `/analyze/quick` endpoint to skip corroboration

## Ethical Considerations

This tool is designed for educational and research purposes. Please understand:

1. **Not a fact-checker**: We estimate credibility based on indicators, not verify individual claims
2. **Source bias**: The source database reflects common assessments but may have biases
3. **Algorithmic limitations**: No algorithm can perfectly assess credibility
4. **Human judgment**: Always apply critical thinking alongside automated analysis

## Troubleshooting

### Common Issues

**"Backend not running" error:**
- Ensure the Python server is running on port 8000
- Check if firewall is blocking localhost connections

**"Failed to extract article":**
- Some websites block automated access
- Try reloading the page and analyzing again

**Slow first analysis:**
- The ML model downloads and loads on first use
- Subsequent analyses will be much faster

## License

This project is for educational purposes. Feel free to modify and use for academic work.

## Contributing

Contributions are welcome! Areas for improvement:
- Expanding the source reputation database
- Improving sensationalism detection
- Adding more RSS feeds for corroboration
- Enhancing the UI/UX
