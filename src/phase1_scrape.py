"""
Phase 1 — Scraping OMS & Forbes Afrique
Objectif : collecter des articles récents sur la santé (OMS) et l'innovation (Forbes Afrique).

Sortie principale :
  outputs/raw_articles_oms_forbes.csv  (colonnes: source,title,date,url,text)

Usage :
  pip install -r requirements.txt
  python phase1_scrape.py
"""

import os, re, time, random
from urllib.parse import urljoin, urlparse
from dateutil import parser as dateparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

# --------- Config de base ----------
HEADERS = {"User-Agent": "TextMiningStudentProject/1.0 (+https://example.org)"}
MAX_ARTICLES_PER_SOURCE = 20          # <-- augmente/diminue si nécessaire
OUTPUT_DIR = "outputs"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "raw_articles_oms_forbes.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------- Utilitaires HTTP ----------

def get_html(url, headers=HEADERS, timeout=30, retries=2, backoff=1.3):
    """Télécharge le HTML avec quelques tentatives et un backoff exponentiel simple."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt < retries:
                # on patiente un peu avant de réessayer (respect du site)
                time.sleep((backoff ** attempt) + random.random() * 0.3)
            else:
                print(f"[ERREUR] {url} -> {e}")
                return None

def absolutize(base_url, href):
    """Transforme un lien relatif en lien absolu."""
    return urljoin(base_url, href) if href else None

def is_same_domain(url, base_domain):
    """Vérifie que l'URL appartient au domaine attendu (sécurité et propreté)."""
    try:
        return base_domain in urlparse(url).netloc.lower()
    except Exception:
        return False

def clean_text(s: str) -> str:
    """Nettoyage léger : trim et espaces multiples."""
    return re.sub(r"\s+", " ", (s or "")).strip()

# --------- OMS : liste + parsing ----------

def list_oms_articles(max_links=MAX_ARTICLES_PER_SOURCE):
    """Récupère des liens plausibles d'articles OMS (FR) depuis la page News."""
    base = "https://www.who.int"
    listing = "https://www.who.int/fr/news"
    html = get_html(listing)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        # heuristique: liens FR + 'news'
        if href and ("/fr/" in href) and ("/news" in href):
            url_abs = absolutize(base, href)
            if url_abs and url_abs not in links:
                links.append(url_abs)
    return links[:max_links]

def parse_oms_article(url):
    """Extrait (title, date, text) d'un article OMS."""
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")

    # titre
    title_tag = soup.find(["h1", "title"])
    title = clean_text(title_tag.get_text(" ", strip=True)) if title_tag else ""

    # date (time[datetime] puis meta article:published_time)
    date_iso = None
    t = soup.find("time")
    if t and t.get("datetime"):
        date_iso = t.get("datetime")
    if not date_iso:
        meta = soup.find("meta", {"property": "article:published_time"})
        if meta and meta.get("content"):
            date_iso = meta.get("content")
    try:
        date_str = dateparser.parse(date_iso).isoformat() if date_iso else None
    except Exception:
        date_str = None

    # texte (concat des <p> non trop courts)
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [clean_text(p) for p in paragraphs if len(p.split()) >= 5]
    text = "\n".join(paragraphs)

    return {"source": "OMS", "url": url, "title": title, "date": date_str, "text": text}

# --------- Forbes Afrique : liste + parsing ----------

def list_forbes_articles(max_links=MAX_ARTICLES_PER_SOURCE):
    """Récupère des liens plausibles d'articles Forbes Afrique depuis la homepage."""
    start = "https://www.forbesafrique.com/"
    domain = "forbesafrique.com"
    html = get_html(start)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        url_abs = absolutize(start, href)
        if url_abs and is_same_domain(url_abs, domain):
            # Heuristiques d'articles : année/mois dans l'URL, 'article' dans le slug...
            if re.search(r"/\d{4}/\d{2}/", url_abs) or ("article" in url_abs.lower()) or ("/202" in url_abs):
                if url_abs not in links:
                    links.append(url_abs)
    return links[:max_links]

def parse_forbes_article(url):
    """Extrait (title, date, text) d'un article Forbes Afrique."""
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("h1") or soup.find("title")
    title = clean_text(title_tag.get_text(" ", strip=True)) if title_tag else ""

    # date via <time> ou meta
    date_iso = None
    t = soup.find("time")
    if t and (t.get("datetime") or t.get_text(strip=True)):
        date_iso = t.get("datetime") or t.get_text(strip=True)
    if not date_iso:
        meta = soup.find("meta", {"property": "article:published_time"})
        if meta and meta.get("content"):
            date_iso = meta.get("content")
    try:
        date_str = dateparser.parse(date_iso).isoformat() if date_iso else None
    except Exception:
        date_str = None

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [clean_text(p) for p in paragraphs if len(p.split()) >= 5]
    text = "\n".join(paragraphs)

    return {"source": "Forbes", "url": url, "title": title, "date": date_str, "text": text}

# --------- Orchestration ----------

def main():
    rows = []

    # 1) collecter les liens
    oms_links = list_oms_articles(MAX_ARTICLES_PER_SOURCE)
    print(f"OMS → {len(oms_links)} liens")

    forbes_links = list_forbes_articles(MAX_ARTICLES_PER_SOURCE)
    print(f"Forbes → {len(forbes_links)} liens")

    # 2) parser OMS
    for u in tqdm(oms_links, desc="OMS - Extraction"):
        row = parse_oms_article(u)
        time.sleep(0.8 + random.random() * 0.4)  # respect du site
        if row and row.get("text"):
            rows.append(row)

    # 3) parser Forbes
    for u in tqdm(forbes_links, desc="Forbes - Extraction"):
        row = parse_forbes_article(u)
        time.sleep(0.8 + random.random() * 0.4)
        if row and row.get("text"):
            rows.append(row)

    # 4) consolidation
    df = pd.DataFrame(rows)
    if df.empty:
        print("⚠️ Aucun article valide n'a été extrait.")
        return

    # nettoyage léger + filtrage
    df["title"] = df["title"].fillna("").map(clean_text)
    df["text"] = df["text"].fillna("").map(clean_text)
    df = df[df["text"].str.len() > 100]
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)

    # 5) export
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Exporté: {OUTPUT_CSV} ({len(df)} articles)")

if __name__ == "__main__":
    main()
