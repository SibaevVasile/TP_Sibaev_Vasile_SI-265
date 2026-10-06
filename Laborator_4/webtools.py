# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265
"""webtools: funcții reutilizabile pentru analiza unui site web.

Doar cereri GET / HEAD, mereu cu timeout. Modulul poate fi importat
(`import webtools`) sau rulat direct (`python webtools.py`) pentru autotest.
"""

import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Exercițiul 47: constantă de modul, folosită în fetch()
DEFAULT_HEADERS = {"User-Agent": "WebLab-Sibaev-Vasile"}

SECURITY_HEADERS = (
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
)


# --------------------------------------------------------------------------
# Partea 3: funcții de bază
# --------------------------------------------------------------------------
def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarcă url cu GET și returnează obiectul răspuns.

    Folosește DEFAULT_HEADERS și un timeout (implicit TIMEOUT secunde).
    """
    return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title> din șirul html.

    Nu face operații de rețea. Returnează un șir gol dacă titlul lipsește.
    """
    start_tag = "<title>"
    start = html.find(start_tag)
    end = html.find("</title>")
    if start == -1 or end == -1 or end < start:
        return ""
    return html[start + len(start_tag):end].strip()


def page_exists(url: str) -> bool:
    """Returnează True dacă url răspunde cu un cod de stare < 400.

    Orice eroare de rețea (DNS, timeout, conexiune) duce la False,
    nu la oprirea programului.
    """
    try:
        return fetch(url).status_code < 400
    except requests.RequestException:
        return False


def check_paths(base: str, paths: list) -> dict:
    """Returnează {cale: cod_de_stare} pentru fiecare cale din paths.

    Dacă o cerere eșuează, valoarea este None. Pauză de 1 s între cereri.
    """
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(1)
        try:
            results[path] = get_status(base.rstrip("/") + path)
        except requests.RequestException:
            results[path] = None
    return results


def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului `name` de la url, sau `default`."""
    return fetch(url).headers.get(name, default)


def security_headers(url: str) -> dict:
    """Returnează {antet: True/False} pentru cele 5 antete de securitate."""
    headers = fetch(url).headers
    return {name: name in headers for name in SECURITY_HEADERS}


def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers() și returnează ex. '3/5'."""
    return f"{sum(1 for ok in results.values() if ok)}/{len(results)}"


def fetch_robots(base: str):
    """Returnează textul /robots.txt de la base sau None dacă lipsește."""
    try:
        response = fetch(base.rstrip("/") + "/robots.txt")
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.text


def disallowed_paths(robots_text) -> list:
    """Returnează lista valorilor Disallow: din robots_text.

    Acceptă și None (returnează lista goală). Ignoră valorile goale.
    """
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:
                paths.append(value)
    return paths


def response_times(*urls: str) -> dict:
    """Returnează {url: secunde} pentru oricâte url-uri. Pauză 1 s între cereri."""
    times = {}
    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(1)
        start = time.perf_counter()
        try:
            fetch(url)
            times[url] = round(time.perf_counter() - start, 3)
        except requests.RequestException:
            times[url] = None
    return times


def log(message: str, **details) -> None:
    """Afișează mesajul urmat de fiecare detaliu: 'mesaj | k=v | k=v'."""
    parts = [message] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(parts))


# --------------------------------------------------------------------------
# Partea 4: funcții cu module standard
# --------------------------------------------------------------------------
def extract_links(html: str) -> list:
    """Returnează legăturile href din html, fără duplicate, în ordinea apariției."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))


def split_links(links: list, domain: str, base: str = None):
    """Împarte legăturile în (interne, externe) față de `domain`.

    Legăturile relative sunt completate cu urljoin() față de `base`
    (implicit https://<domain>). Sunt ignorate mailto:, javascript:, tel: și #.
    """
    base = base or f"https://{domain}"
    internal, external = [], []
    for link in links:
        full = urljoin(base, link)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc == domain:
            internal.append(full)
        else:
            external.append(full)
    return internal, external


class ImageFinder(HTMLParser):
    """Colectează atributul src al fiecărui tag <img> într-o listă `images`."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Apelată automat de HTMLParser.feed() pentru fiecare tag de deschidere."""
        if tag == "img":  # HTMLParser dă tag-urile deja cu litere mici
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 (hex) a corpului paginii de la url."""
    return hashlib.sha256(fetch(url).content).hexdigest()


def save_headers(url: str, filename: str = "headers.json") -> dict:
    """Salvează antetele de la url în filename (JSON) și returnează dicționarul."""
    headers = dict(fetch(url).headers)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(headers, file, indent=2)
    return headers


def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 a lui hostname (interogare DNS)."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
    expires = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires - time.time()) // 86400)


# --------------------------------------------------------------------------
# Partea 5: proiectul final
# --------------------------------------------------------------------------
def redirect_chain(url: str) -> list:
    """Returnează lista redirecționărilor ['301 -> https://...'] pentru url."""
    response = fetch(url)
    chain = [f"{hop.status_code} -> {hop.headers.get('Location', '?')}"
             for hop in response.history]
    return chain


def site_report(url: str, output: str = "report.json") -> dict:
    """Colectează informații despre site, le afișează și le salvează în JSON.

    Include: stare, URL final, titlu, IP, redirecționări de la http://,
    scor antete de securitate, zile până la expirarea certificatului,
    numărul de legături interne/externe și căile interzise din robots.txt.
    """
    host = urlparse(url).netloc
    report = {"url": url}

    response = fetch(url)
    report["status"] = response.status_code
    report["final_url"] = response.url
    report["title"] = get_title(response.text)
    links = extract_links(response.text)
    internal, external = split_links(links, host, base=response.url)
    report["links_internal"] = len(internal)
    report["links_external"] = len(external)
    report["headers_score"] = score_headers(
        {name: name in response.headers for name in SECURITY_HEADERS})

    try:
        report["ip"] = resolve(host)
    except OSError:
        report["ip"] = None

    time.sleep(1)
    try:
        report["redirects"] = redirect_chain("http://" + host)
    except requests.RequestException:
        report["redirects"] = []

    try:
        report["cert_days_left"] = cert_days_left(host)
    except (OSError, ssl.SSLError):
        report["cert_days_left"] = None

    time.sleep(1)
    report["disallowed"] = disallowed_paths(fetch_robots(url))

    redirects = ", ".join(report["redirects"]) or "niciuna"
    cert = report["cert_days_left"]
    cert_text = f"{cert} de zile rămase" if cert is not None else "indisponibil"
    print(f"=== Raport site: {url} ===")
    print(f"Cod de stare:      {report['status']}")
    print(f"URL final:         {report['final_url']}")
    print(f"Titlu:             {report['title']}")
    print(f"Adresă IP:         {report['ip']}")
    print(f"Redirecționări:    {redirects}")
    print(f"Scor securitate:   {report['headers_score']}")
    print(f"Certificat:        {cert_text}")
    print(f"Legături:          {report['links_internal']} interne, "
          f"{report['links_external']} externe")
    print(f"Căi interzise:     {', '.join(report['disallowed']) or 'niciuna'}")

    with open(output, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print(f"Salvat în {output}")
    return report


# Exercițiul 46: autotestul rulează doar la `python webtools.py`
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))
