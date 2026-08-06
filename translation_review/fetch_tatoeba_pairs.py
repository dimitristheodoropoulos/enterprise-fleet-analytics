"""
fetch_tatoeba_pairs.py (v2)

Downloads three real Tatoeba export files and joins them locally to build
real English<->Greek sentence pairs with real human translations:

  - ell_sentences.tsv.bz2      (id, lang, greek_text)
  - eng_sentences.tsv.bz2      (id, lang, english_text)
  - ell-eng_links.tsv.bz2      (sentence_id, translation_id) pairs

Tatoeba's sentences.tsv format is: id <TAB> lang <TAB> text
Its links.tsv format is: sentence_id <TAB> translation_id
(the link is directional but for our purposes we just need any pair where
one id resolves in the Greek set and the other in the English set)
"""

import bz2
import csv
import json
import os
import requests

BASE = "https://downloads.tatoeba.org/exports"
FILES = {
    "ell_sentences": f"{BASE}/per_language/ell/ell_sentences.tsv.bz2",
    "eng_sentences": f"{BASE}/per_language/eng/eng_sentences.tsv.bz2",
    "links": f"{BASE}/per_language/ell/ell-eng_links.tsv.bz2",
}

HERE = os.path.dirname(__file__)


def download(name: str, url: str) -> str:
    path = os.path.join(HERE, f"{name}.tsv")
    if os.path.exists(path):
        print(f"{name}: already downloaded, skipping.")
        return path
    print(f"Downloading {name} from {url} ...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    decompressed = bz2.decompress(resp.content)
    with open(path, "wb") as f:
        f.write(decompressed)
    print(f"  -> saved {path} ({len(decompressed)/1024:.0f} KB)")
    return path


def load_sentences(path: str) -> dict:
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            sid, _lang, text = row[0], row[1], row[2]
            out[sid] = text
    return out


def load_links(path: str) -> list:
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 2:
                continue
            pairs.append((row[0], row[1]))
    return pairs


def build_pairs(el_sentences, en_sentences, links, n=20, min_len=20, max_len=140):
    picked = []
    seen_en = set()
    for a, b in links:
        # figure out which side is Greek and which is English
        if a in el_sentences and b in en_sentences:
            el_text, en_text = el_sentences[a], en_sentences[b]
        elif b in el_sentences and a in en_sentences:
            el_text, en_text = el_sentences[b], en_sentences[a]
        else:
            continue

        if en_text in seen_en:
            continue
        if not (min_len <= len(en_text) <= max_len):
            continue

        seen_en.add(en_text)
        picked.append({"en": en_text.strip(), "el_reference": el_text.strip()})
        if len(picked) >= n:
            break

    return picked


if __name__ == "__main__":
    paths = {name: download(name, url) for name, url in FILES.items()}

    print("Loading and joining...")
    el_sentences = load_sentences(paths["ell_sentences"])
    en_sentences = load_sentences(paths["eng_sentences"])
    links = load_links(paths["links"])

    print(f"  Greek sentences: {len(el_sentences)}")
    print(f"  English sentences: {len(en_sentences)}")
    print(f"  Links: {len(links)}")

    pairs = build_pairs(el_sentences, en_sentences, links, n=20)

    print(f"\nSampled {len(pairs)} EN->EL sentence pairs:\n")
    for i, p in enumerate(pairs, 1):
        print(f"{i}. EN: {p['en']}")
        print(f"   EL (human reference): {p['el_reference']}\n")

    out_json = os.path.join(HERE, "sampled_pairs.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
    print(f"Saved -> {out_json}")