#!/usr/bin/env python3
# scrape_to_md.py
# Uso: python scrape_to_md.py links.md output_dir

import sys, re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:

    from markdownify import markdownify as html_to_md

except:

    try:

        import html2text
        h = html2text.HTML2Text(); h.body_width = 0
        def html_to_md(html): return h.handle(html)

    except:

        def html_to_md(html):

            return BeautifulSoup(html, "html.parser").get_text("\n\n")

def fetch(url, retries=3, delay=5):

    for i in range(retries):

        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"}, timeout=30)

            r.raise_for_status()
            r.encoding = r.encoding or "utf-8"

            return r.text


        except Exception as e:

        if i < retries - 1:
                print(f"   fallo {i+1}/{retries}, reintento en {delay}s…")
                time.sleep(delay)

        else:
                raise


def clean_article_div(div, base_url):

    for tag in div.select("script, style, iframe, noscript"): tag.decompose()

    for a in div.find_all("a", href=True): a['href'] = urljoin(base_url, a['href'])

    for img in div.find_all("img", src=True): img['src'] = urljoin(base_url, img['src'])

    return str(div)

def extract_main_contents(html, base_url):

    soup = BeautifulSoup(html, "html.parser")

    main = soup.find(id="main_contents") or soup.find("article")

    return clean_article_div(main, base_url) if main else None



def postprocess(md: str) -> str:

    # filtro de quitar
    md = md.replace("Top", "").replace("column", "")

    # saltos de linea en plan bien
    md = re.sub(r"\n{2,}", "\n\n", md)
    return md.strip()


def main():

    if len(sys.argv) < 3:

        print("Uso: python scrape_to_md.py links.md output_dir")
        sys.exit(1)

    links_file, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)


    md_text = links_file.read_text(encoding="utf-8")

    urls = re.findall(r"\((https?://[^\)]+)\)", md_text)
    print(f"Encontradas {len(urls)} URLs")

    combined = []

    for i, url in enumerate(urls, start=1):

        try:
            print(f"[{i}] Descargando {url}")
            html = fetch(url)
            main_html = extract_main_contents(html, url)


            if not main_html:
                print(f"[{i}] main_contents no encontrado")
                continue

            md = html_to_md(main_html)
            md = postprocess(md)

            file_path = out_dir / f"{i}.md"
            file_path.write_text(f"<!-- source: {url} -->\n\n{md}\n", encoding="utf-8")
            combined.append((url, md))
            print(f"[{i}] Guardado {file_path.name}")

        except Exception as e:
            print(f"[{i}] ERROR {url} -> {e}")


        # esperar 10s antes del siguiente
        time.sleep(10)

    allf = out_dir / "all_articles.md"
    with allf.open("w", encoding="utf-8") as f:

        for idx, (url, md) in enumerate(combined):
            f.write(f"<!-- source: {url} -->\n\n{md}\n")

            if idx != len(combined)-1: f.write("\n---\n\n")
    print(f"Combinado: {allf}")


if __name__ == "__main__":
    main()
