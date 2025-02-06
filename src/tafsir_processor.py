#!/usr/bin/env python3
"""
Enhanced Tafsir Processor with Robust XML Parsing and Advanced NLP Analysis

This script processes the main tafsir file in XML format. It now uses lxml with the recover
option enabled so that minor XML errors (such as mismatched tags) do not prevent processing.

The XML file is expected to have a structure similar to:

<qurantafseer name="Sayyid Abul Ala Maududi">
    <sura index="1">
        <aya index="0" text ="1. Surah Al Fatihah (The Opening) Name {surah-name-description-text} Theme {surah-theme-text}" />
        <aya index="1-3" text="In the name of Allah, the Compassionate, the Merciful. {1} Praise is only for Allah, {2} the Lord of the Universe, {3} the All-Compassionate, the All-Merciful, {4} the Master of the Day of Judgment. {5}" />
        <footer index="1" text="{verse(s)-commentary-text}" />
        <!-- additional footer elements -->
    </sura>
    <sura index="2">
        <!-- sura 2 content -->
    </sura>
    <!-- more sura elements -->
</qurantafseer>

Dependencies:
    - Python 3.7+
    - lxml
    - nltk
    - spacy
    - en_core_web_sm (spaCy model)

Usage:
    Ensure your tafsir XML file is in the 'data/' folder (e.g., data/maududi-tafsir.xml)
    and run:
        python -m src.tafsir_processor
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import datetime
import asyncio
from dataclasses import dataclass, field
import gc

# Use lxml for robust XML parsing
try:
    from lxml import etree as LET
except ImportError:
    raise ImportError("lxml is required. Please install it via 'pip install lxml'")

# Advanced NLP libraries
import nltk
import spacy

# -------------------------------
# Setup Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="tafsir_processor.log",
    filemode="a",
)
logger = logging.getLogger("TafsirProcessor")

# -------------------------------
# Constants and Directories
# -------------------------------
INPUT_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Download Required NLTK Resources
# -------------------------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

# -------------------------------
# Load spaCy Model (en_core_web_sm)
# -------------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error("Error loading spaCy model: en_core_web_sm. Install it with 'python -m spacy download en_core_web_sm'", exc_info=True)
    raise e

# -------------------------------
# Dataclass for Tafsir Content (if needed)
# -------------------------------
@dataclass
class TafsirContent:
    verse_id: str
    raw_text: str
    markers: List[str] = field(default_factory=list)
    footers: Dict[str, str] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)

# -------------------------------
# Main Processor Class
# -------------------------------
class MemoryEfficientProcessor:
    def __init__(self):
        self.nlp = nlp  # spaCy model

    def process_tafsir_file(self, file_path: Path) -> None:
        """
        Parse the XML tafsir file using lxml with recovery enabled, process each sura element,
        and save the refined analysis.
        """
        logger.info(f"Starting to process tafsir XML file: {file_path}")
        try:
            # Create a parser with recover enabled
            parser = LET.XMLParser(recover=True)
            tree = LET.parse(str(file_path), parser)
            root = tree.getroot()
            qurantafseer_name = root.attrib.get("name", "Unknown")

            # Process each sura element
            for sura in root.findall("sura"):
                sura_index = sura.attrib.get("index")
                sura_info: Dict[str, str] = {}
                aya_entries: List[Dict[str, Any]] = []

                # Collect footer elements into a mapping (keyed by their index)
                footer_mapping: Dict[str, str] = {}
                for child in sura.findall("footer"):
                    f_index = child.attrib.get("index")
                    f_text = child.attrib.get("text")
                    if f_index and f_text:
                        footer_mapping[f_index] = f_text

                # Process each aya element
                for aya in sura.findall("aya"):
                    aya_index = aya.attrib.get("index")
                    text_attr = aya.attrib.get("text")
                    if not text_attr:
                        continue
                    # The aya with index="0" is treated as sura-level info
                    if aya_index == "0":
                        sura_info = self.parse_sura_info(text_attr)
                    else:
                        # Extract markers from the text (e.g., {1}, {2}, etc.)
                        markers = re.findall(r"\{(\d+)\}", text_attr)
                        # Clean the text by removing marker placeholders
                        clean_text = re.sub(r"\{\d+\}", "", text_attr).strip()
                        aya_entry = {
                            "aya_index": aya_index,
                            "raw_text": text_attr,
                            "clean_text": clean_text,
                            "markers": markers,
                            "footers": {},
                            "analysis": {}
                        }
                        # Associate markers with corresponding footer commentary
                        for marker in markers:
                            if marker in footer_mapping:
                                aya_entry["footers"][marker] = footer_mapping[marker]
                        # Perform advanced NLP analysis on the clean text
                        advanced_results = self.advanced_analysis(clean_text)
                        aya_entry["analysis"] = advanced_results
                        aya_entry["analysis"]["themes"] = self.extract_themes(clean_text)
                        aya_entry["analysis"]["advanced_analysis_timestamp"] = datetime.datetime.now().isoformat()
                        aya_entries.append(aya_entry)

                # Build the sura-level output structure
                sura_output = {
                    "qurantafseer": qurantafseer_name,
                    "sura_index": int(sura_index) if sura_index and sura_index.isdigit() else sura_index,
                    "sura_info": sura_info,
                    "ayah": aya_entries,
                    "metadata": {
                        "processed_timestamp": datetime.datetime.now().isoformat(),
                        "version": "2.0"
                    }
                }
                # Save the sura output to a file
                self.save_sura_analysis(sura_output)
                gc.collect()
            logger.info("Completed processing the tafsir XML file.")
        except Exception as e:
            logger.error(f"Error processing tafsir file {file_path}: {e}", exc_info=True)
            raise

    def parse_sura_info(self, text: str) -> Dict[str, str]:
        """
        Parse sura-level information from the aya with index="0".
        Attempts multiple regex patterns to capture sura name, description,
        theme, historical background, and topics.
        """
        text = text.strip()
        patterns = [
            # Pattern for simple sura info: sura number, name, description and theme.
            (r"^\d+\.\s*(.+?)\s+Name\s*\{(.+?)\}\s+Theme\s*\{(.+?)\}", ["name", "description", "theme"]),
            # Pattern for sura info with historical background and topics interconnection.
            (r"^\d+\.\s*(.+?)\s+Name\s*\{(.+?)\}\s+Historical Background\s*\{(.+?)\}\s+Theme:?\s*\{(.+?)\}\s+Topics and their Interconnection\s*\{(.+?)\}", 
             ["name", "description", "historical_background", "theme", "topics_interconnection"])
        ]
        for pattern, keys in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return {k: match.group(i+1).strip() for i, k in enumerate(keys)}
        return {"raw": text}

    def advanced_analysis(self, text: str) -> Dict[str, Any]:
        """
        Apply advanced NLP techniques using NLTK and spaCy on the text.
        Returns a dictionary with keywords, named_entities, noun_chunks, and frequency distribution.
        """
        results: Dict[str, Any] = {}
        try:
            # --- NLTK-based Analysis ---
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize

            stop_words = set(stopwords.words("english"))
            tokens = word_tokenize(text.lower())
            words = [word for word in tokens if word.isalpha() and word not in stop_words]
            freq_dist = {}
            if words:
                freq_counts = {}
                for word in words:
                    freq_counts[word] = freq_counts.get(word, 0) + 1
                freq_dist = dict(sorted(freq_counts.items(), key=lambda item: item[1], reverse=True)[:20])
                keywords = list(freq_dist.keys())
            else:
                keywords = []
            results["keywords"] = keywords
            results["freq_dist"] = freq_dist

            # --- spaCy-based Analysis ---
            doc = self.nlp(text)
            named_entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            results["named_entities"] = named_entities
            results["noun_chunks"] = noun_chunks

        except Exception as e:
            logger.error(f"Error in advanced NLP analysis: {e}", exc_info=True)
        return results

    def extract_themes(self, text: str) -> List[str]:
        """
        Extract themes from the text using heuristic patterns.
        """
        try:
            themes = []
            theme_patterns = {
                "divine mercy": r"mercy|compassion|forgiveness",
                "prophethood": r"prophet|messenger|revelation",
                "law": r"law|commandment|decree",
                "parables": r"parable|example|story",
            }
            lower_text = text.lower()
            for theme, pattern in theme_patterns.items():
                if re.search(pattern, lower_text):
                    themes.append(theme)
            return themes
        except Exception as e:
            logger.error(f"Error extracting themes: {e}", exc_info=True)
            return []

    def save_sura_analysis(self, sura_analysis: Dict) -> None:
        """
        Save the sura analysis to a refined JSON file.
        File name format: sura_<sura_index>.json
        """
        try:
            sura_index = sura_analysis.get("sura_index", "unknown")
            output_file = OUTPUT_DIR / f"sura_{sura_index}.json"
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(sura_analysis, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved sura analysis for sura {sura_index} to {output_file}")
        except Exception as e:
            logger.error(f"Error saving sura analysis for sura {sura_analysis.get('sura_index')}: {e}", exc_info=True)

# -------------------------------
# Main Async Function
# -------------------------------
async def main():
    processor = MemoryEfficientProcessor()
    try:
        # Expect the tafsir XML file to be named "maududi-tafsir.xml" in the data/ folder.
        tafsir_file = INPUT_DIR / "maududi-tafsir.xml"
        if not tafsir_file.exists():
            logger.error(f"Tafsir file not found: {tafsir_file}")
            return

        processor.process_tafsir_file(tafsir_file)
        logger.info("Processing complete.")
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
