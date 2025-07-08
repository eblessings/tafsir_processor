````markdown
# Tafsir Processor

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()  

An advanced, memory-efficient processor for Qur’anic **tafsir** XML files.  
It parses complex, irregularly tagged tafsir documents (with `<sura>`, `<aya>`, and `<footer>` elements), applies sophisticated NLP analyses via NLTK and spaCy, and emits clean, structured JSON per sūra—ready for downstream consumption, extension, or data-science workflows.

---

## 📑 Table of Contents

1. [Key Features](#key-features)  
2. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
3. [Project Layout](#project-layout)  
4. [Usage](#usage)  
   - [Basic Run](#basic-run)  
   - [Configuration & Options](#configuration--options)  
5. [Advanced NLP Analysis](#advanced-nlp-analysis)  
6. [Logging & Outputs](#logging--outputs)  
7. [Contributing](#contributing)  
8. [License](#license)  
9. [Contact & Support](#contact--support)  

---

## 🔑 Key Features

- **Resilient XML Parsing**  
  Uses **lxml** with recovery mode to handle minor markup errors and irregular structures.

- **Per-Sūra JSON Output**  
  Clean, hierarchical JSON files—one per sūra—containing metadata, raw & cleaned text, markers, footnotes, and NLP results.

- **Dual NLP Engines**  
  - **NLTK** for tokenization, stop-word removal, frequency distributions, and keyword extraction.  
  - **spaCy** for named-entity recognition (NER) and noun-chunk extraction.

- **Marker-Footer Matching**  
  Automatically links `{1}`, `{2}`, … markers in aya text to their corresponding `<footer>` commentary.

- **Memory-Conscious Processing**  
  Incorporates streaming, chunked parsing, and explicit garbage collection to keep RAM footprint low.

- **Extensible & Configurable**  
  Tweak regex patterns, enable/disable specific analyses, or plug in new NLP modules with minimal changes.

---

## 🚀 Getting Started

### Prerequisites

- **Python** ≥ 3.7  
- **pip** ≥ 20.0  

(Optional but recommended)  
- A POSIX-compatible shell (Linux / macOS / WSL on Windows)

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-username>/tafsir-processor.git
   cd tafsir-processor
````

2. **(Optional) Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows PowerShell
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

> **Note:** On first run, the script will auto-download required NLTK corpora (`punkt`, `stopwords`, etc.) if missing.

---

## 📂 Project Layout

```text
tafsir-processor/
├── data/
│   └── maududi-tafsir.xml        # Sample/input tafsir XML file
├── output/
│   └── sura_<index>.json         # Generated per-sūra JSON files
├── logs/
│   └── tafsir_processor.log      # Processing & error logs
├── src/
│   └── tafsir_processor.py       # Core processing script
├── requirements.txt              # Python dependency list
└── README.md                     # This documentation
```

---

## 🛠️ Usage

### Basic Run

1. Place your tafsir XML (`.xml`) file in `data/` (e.g. `data/maududi-tafsir.xml`).

2. Execute the processor:

   ```bash
   python -m src.tafsir_processor \
     --input data/maududi-tafsir.xml \
     --output output/ \
     --log logs/tafsir_processor.log
   ```

3. Inspect JSON outputs in `output/` and logs in `logs/`.

### Configuration & Options

Run `--help` to see all available flags:

```bash
python -m src.tafsir_processor --help
```

Common options:

| Flag                     | Description                                                        | Default              |
| ------------------------ | ------------------------------------------------------------------ | -------------------- |
| `--input <path>`         | Path to input XML file                                             | `data/*.xml`         |
| `--output <dir>`         | Directory to write JSON files                                      | `output/`            |
| `--log <file>`           | Path to write processing logs                                      | `logs/processor.log` |
| `--disable-nltk`         | Skip NLTK-based analysis                                           | *false*              |
| `--disable-spacy`        | Skip spaCy NER & noun-chunk extraction                             | *false*              |
| `--gc-threshold <bytes>` | Force garbage collection after this many bytes processed per chunk | `100e6`              |
| `--verbose`              | Print detailed progress to console                                 | *false*              |

---

## 📊 Advanced NLP Analysis

* **NLTK Pipeline**

  1. Tokenize aya text.
  2. Remove stop words & punctuation.
  3. Compute frequency distribution & extract top 10 keywords.

* **spaCy Pipeline**

  1. Load `en_core_web_sm`.
  2. Perform NER: PERSON, ORG, GPE, etc.
  3. Extract noun chunks for thematic insight.

*All analysis results are embedded under each aya’s `"analysis"` field in the JSON.*

---

## 📥 Logging & Outputs

* **Logs**
  Detailed debug, info, and error messages are written to the specified log file.
* **JSON Schema**
  Each `sura_<n>.json` follows:

  ```json
  {
    "sura_index": 1,
    "name": "...",
    "theme": "...",
    "aya": [
      {
        "aya_index": "1-3",
        "text_raw": "...",
        "text_clean": "...",
        "markers": [1,2,3],
        "footers": {
          "1": "...",
          "...": "..."
        },
        "analysis": {
          "keywords": [...],
          "frequency": {...},
          "entities": [...],
          "noun_chunks": [...]
        }
      },
      ...
    ]
  }
  ```

---

## 🤝 Contributing

We welcome improvements! To contribute:

1. **Fork** this repository.
2. **Create** a new branch:

   ```bash
   git checkout -b feature/my-feature
   ```
3. **Commit** your changes with clear messages.
4. **Push** your branch and open a **Pull Request**.

Please ensure all checks pass and include tests for new features.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 📬 Contact & Support

– **Issues & Bugs:** Open an issue on GitHub.
– **Questions & Discussions:** Use the Discussions tab or email **[youremail@example.com](mailto:youremail@example.com)**.

Happy processing!

```
```
