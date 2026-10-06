# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265

import argparse
import csv
import time
from datetime import datetime

import webtools  # Ex. 44: importul întregului modul
# Ex. 45: importarea anumitor nume; ele se apelează fără prefix.
from webtools import get_title, security_headers, DEFAULT_HEADERS, site_report

# Ex. 45: dacă main.py ar avea și o funcție proprie get_title, definiția
# locală ar SUPRASCRIE numele importat (câștigă ultima atribuire în ordinea
# execuției), iar get_title(...) ar apela funcția din main.py, nu pe cea din
# webtools. Cu `import webtools` nu există conflict: webtools.get_title
# și get_title rămân distincte.

# Ex. 46: `python webtools.py` -> __name__ == "__main__" în webtools, deci
# autotestul rulează. `python main.py` doar IMPORTĂ webtools; atunci
# __name__ == "webtools", condiția e falsă și autotestul nu rulează.


def save_csv(results: dict, filename: str = "report.csv") -> None:
    """Ex. 49: salvează rezultatul check_paths() în CSV (path, status, checked_at)."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status, datetime.now().isoformat()])

def main() -> None:
    # Ex. 48: argument din linia de comandă
    parser = argparse.ArgumentParser(description="Analizează un site web.")
    parser.add_argument("url", help="URL-ul site-ului web ex: https://cybercor.org")
    args = parser.parse_args()
    url = args.url.rstrip("/")

    # Ex. 44
    print("Titlu:", webtools.get_title(webtools.fetch(url).text))
    time.sleep(1)
    # Ex. 45
    print("Titlu (from import):", get_title(webtools.fetch(url).text))
    time.sleep(1)
    print("Antete de securitate:", security_headers(url))
    time.sleep(1)
    # Ex. 47
    print("DEFAULT_HEADERS:", DEFAULT_HEADERS)
    print()

    # Ex. 49
    results = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    save_csv(results)
    print("Salvat în report.csv:", results)
    time.sleep(1)
    print()

    # Ex. 50
    site_report(url)


if __name__ == "__main__":
    main()
