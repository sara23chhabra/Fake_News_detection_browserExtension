# Methodology Block Diagram

## System Architecture Overview

```mermaid
flowchart TB
    subgraph USER["👤 User"]
        A[Opens News Article in Browser]
    end

    subgraph EXT["🌐 Browser Extension"]
        B[Click Extension Icon]
        C[Extract Page URL]
        D[Send Request to Backend]
        E[Display Results]
    end

    subgraph API["⚙️ FastAPI Backend"]
        F["/analyze Endpoint"]
    end

    subgraph EXTRACT["📄 Article Extraction"]
        G[newspaper3k Library]
        G1[Extract Title]
        G2[Extract Full Text]
        G3[Extract Metadata]
    end

    subgraph SUMMARIZE["🤖 AI Summarization"]
        H[HuggingFace Transformers]
        H1["BART-Large-CNN Model"]
        H2[Generate 2-4 Sentence Summary]
    end

    subgraph CREDIBILITY["📊 Credibility Analysis"]
        subgraph SOURCE["Source Reputation"]
            I1[Lookup Domain in Database]
            I2["Score: 0-100"]
        end
        
        subgraph SENSATIONAL["Sensationalism Detection"]
            J1[Check Clickbait Phrases]
            J2[Check Emotional Words]
            J3[Check Excessive Caps]
            J4["Penalty: 0-30"]
        end
        
        subgraph CORROBORATE["Cross-Source Corroboration"]
            K1[Extract Keywords]
            K2[Search RSS Feeds]
            K3[Calculate Similarity]
            K4["Bonus: 0-15"]
        end
    end

    subgraph SCORE["🎯 Final Score Calculation"]
        L["Score = Source - Sensationalism + Corroboration"]
        M{Score Range}
        M1["🟢 High: 75-100"]
        M2["🟡 Medium: 50-74"]
        M3["🔴 Low: 0-49"]
    end

    A --> B --> C --> D --> F
    F --> G --> G1 & G2 & G3
    G1 & G2 --> H --> H1 --> H2
    G1 & G2 --> I1 --> I2
    G1 & G2 --> J1 & J2 & J3 --> J4
    G1 & H2 --> K1 --> K2 --> K3 --> K4
    I2 & J4 & K4 --> L --> M
    M --> M1 & M2 & M3
    M1 & M2 & M3 --> E
```

---

## Detailed Methodology Flow

```mermaid
flowchart LR
    subgraph INPUT["Input"]
        URL["Article URL"]
    end

    subgraph PHASE1["Phase 1: Extraction"]
        EX1["Download Page"]
        EX2["Parse HTML"]
        EX3["Extract Content"]
    end

    subgraph PHASE2["Phase 2: Processing"]
        PR1["Text Cleaning"]
        PR2["Tokenization"]
        PR3["Summarization"]
    end

    subgraph PHASE3["Phase 3: Analysis"]
        direction TB
        AN1["Source Check"]
        AN2["Sensationalism Check"]
        AN3["Corroboration Check"]
    end

    subgraph PHASE4["Phase 4: Scoring"]
        SC1["Combine Scores"]
        SC2["Apply Formula"]
        SC3["Generate Label"]
    end

    subgraph OUTPUT["Output"]
        OUT["Credibility Report"]
    end

    URL --> EX1 --> EX2 --> EX3
    EX3 --> PR1 --> PR2 --> PR3
    PR3 --> AN1 & AN2 & AN3
    AN1 & AN2 & AN3 --> SC1 --> SC2 --> SC3 --> OUT
```

---

## Credibility Scoring Formula

```mermaid
flowchart LR
    subgraph INPUTS["Score Components"]
        S["Source Score<br/>(0-100)"]
        P["Sensationalism Penalty<br/>(0-30)"]
        B["Corroboration Bonus<br/>(0-15)"]
    end

    subgraph FORMULA["Formula"]
        F["Final = S - P + B"]
    end

    subgraph CLAMP["Clamping"]
        C["Clamp to 0-100"]
    end

    subgraph LABELS["Labels"]
        L1["≥75: High 🟢"]
        L2["50-74: Medium 🟡"]
        L3["<50: Low 🔴"]
    end

    S --> F
    P --> F
    B --> F
    F --> C --> L1 & L2 & L3
```

---

## Cross-Source Corroboration Process

```mermaid
flowchart TB
    A["Article Title + Summary"] --> B["Extract Keywords"]
    B --> C["Remove Stop Words"]
    C --> D["Filter by Length ≥4"]
    
    D --> E["For Each Trusted RSS Feed"]
    
    subgraph FEEDS["Trusted RSS Feeds (12 sources)"]
        F1["BBC"]
        F2["Reuters"]
        F3["Guardian"]
        F4["Al Jazeera"]
        F5["The Hindu"]
        F6["..."]
    end
    
    E --> F1 & F2 & F3 & F4 & F5 & F6
    
    F1 & F2 & F3 & F4 & F5 & F6 --> G["Fetch Recent Entries"]
    G --> H["Extract Entry Keywords"]
    H --> I["Calculate Similarity"]
    
    I --> J{"Similarity ≥ 15%?"}
    J -->|Yes| K["Add to Matches"]
    J -->|No| L["Skip"]
    
    K --> M{"Count Matches"}
    M -->|"≥3"| N["+15 Bonus"]
    M -->|"1-2"| O["+5 Bonus"]
    M -->|"0"| P["+0 (No Penalty)"]
```

---

## Sensationalism Detection Flow

```mermaid
flowchart TB
    A["Article Title + Text"] --> B["Analyze Title"]
    
    B --> C["Check Clickbait Phrases"]
    C --> C1["'You won't believe...'"]
    C --> C2["'SHOCKING revelation...'"]
    C --> C3["'What happens next...'"]
    
    B --> D["Check Caps Abuse"]
    D --> D1{">50% UPPERCASE?"}
    D1 -->|Yes| D2["-3 to -5 points"]
    D1 -->|No| D3["0 points"]
    
    B --> E["Check Punctuation"]
    E --> E1{"!! or ?? or !?"}
    E1 -->|Yes| E2["-1 to -3 points"]
    E1 -->|No| E3["0 points"]
    
    A --> F["Check Sensational Words"]
    F --> F1["'bombshell', 'explosive'"]
    F --> F2["'devastating', 'shocking'"]
    
    C1 & C2 & C3 --> G["-3 each (max -12)"]
    F1 & F2 --> H["-2 each (max -10)"]
    
    G & H & D2 & D3 & E2 & E3 --> I["Total Penalty (max -30)"]
```
