"""Web scraping de imagenes de senas LSM/ASL para vocales A,E,I,O,U.

Daniel Jimenez Vallejo - Proyecto Final Vision por Computadora.
Usa icrawler para descargar de Bing Images.
"""
from pathlib import Path
from icrawler.builtin import BingImageCrawler

BASE = Path("data/proyecto-final")  # ruta local de los datos (ajústala en tu máquina)
OUT = BASE / "scraped"
OUT.mkdir(parents=True, exist_ok=True)

# Queries variados por vocal - mezcla LSM (Mexican) y ASL (similar para vocales)
QUERIES = {
    "A": [
        "American Sign Language letter A hand",
        "ASL alphabet A fist hand sign",
        "lengua de senas A vocal mano",
    ],
    "E": [
        "American Sign Language letter E hand",
        "ASL alphabet E fingers curled",
        "sign language vowel E",
    ],
    "I": [
        "American Sign Language letter I hand",
        "ASL alphabet I pinky up",
        "sign language vowel I pinky",
    ],
    "O": [
        "American Sign Language letter O hand",
        "ASL alphabet O round hand",
        "sign language vowel O",
    ],
    "U": [
        "American Sign Language letter U hand",
        "ASL alphabet U two fingers",
        "sign language vowel U two fingers",
    ],
}

MAX_POR_QUERY = 15  # ~45 imgs por vocal -> ~225 imgs totales

def scrape():
    for vocal, queries in QUERIES.items():
        target = OUT / vocal
        target.mkdir(parents=True, exist_ok=True)
        for q in queries:
            print(f"[{vocal}] Buscando: {q}")
            try:
                crawler = BingImageCrawler(
                    storage={"root_dir": str(target)},
                    log_level=40,  # ERROR only
                )
                crawler.crawl(
                    keyword=q,
                    max_num=MAX_POR_QUERY,
                    min_size=(150, 150),
                    file_idx_offset="auto",
                )
            except Exception as e:
                print(f"  Error en '{q}': {e}")
                continue
        n = len(list(target.glob("*")))
        print(f"[{vocal}] Total descargado: {n} imagenes")

    print("\n=== RESUMEN FINAL ===")
    for vocal in QUERIES:
        n = len(list((OUT / vocal).glob("*")))
        print(f"  {vocal}: {n}")

if __name__ == "__main__":
    scrape()
