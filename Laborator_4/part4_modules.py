# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265

import hashlib
import json
import re
import socket
import ssl
import time
import urllib.parse
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# Ex. 35 -------------------------------------------------------------------
def show_url_parts(url: str) -> None:
    """Afișează componentele unui URL, obținute cu urllib.parse.urlparse()."""
    parts = urllib.parse.urlparse(url)
    print("scheme:  ", parts.scheme)
    print("netloc:  ", parts.netloc)
    print("path:    ", parts.path)
    print("query:   ", parts.query)
    print("fragment:", parts.fragment)


# Ex. 36 -------------------------------------------------------------------
def join_examples(base: str, links: list) -> list:
    """Transformă legăturile relative în URL-uri complete cu urljoin()."""
    return [urllib.parse.urljoin(base, link) for link in links]


# Ex. 37 -------------------------------------------------------------------
def extract_links(html: str) -> list:
    """Returnează legăturile href din html, fără duplicate (ordinea se păstrează)."""
    found = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(found))


# Ex. 38 -------------------------------------------------------------------
def split_links(links: list, domain: str):
    """Returnează (interne, externe): legăturile de pe `domain` și de pe alte site-uri.

    Fiecare legătură este mai întâi completată cu urljoin(), apoi se compară
    urlparse().netloc cu domeniul. Schemele non-http (mailto:, tel:...) sunt omise.
    """
    base = f"https://{domain}"
    internal, external = [], []
    for link in links:
        full = urljoin(base, link)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        (internal if parsed.netloc == domain else external).append(full)
    return internal, external


# Ex. 39 -------------------------------------------------------------------
class ImageFinder(HTMLParser):
    """Parser care colectează atributul src al fiecărui tag <img>."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Apelată de HTMLParser pentru fiecare tag de deschidere (nu direct de noi)."""
        if tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


# Ex. 40 -------------------------------------------------------------------
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 (hexazecimal) a conținutului paginii."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


# Ex. 42 -------------------------------------------------------------------
def resolve(hostname: str) -> str:
    """Returnează adresa IP (IPv4) a unui nume de domeniu."""
    return socket.gethostbyname(hostname)


# Ex. 43 -------------------------------------------------------------------
def cert_days_left(hostname: str) -> int:
    """Returnează numărul de zile rămase până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            cert = tls_sock.getpeercert()
    expires = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires - time.time()) // 86400)


if __name__ == "__main__":
    print("=== Ex. 35 ===")
    show_url_parts("https://cybercor.org/path?x=1#top")

    print("\n=== Ex. 36 ===")
    for full in join_examples(BASE_URL, ["/about", "contact.html", "../index.html"]):
        print(full)

    print("\n=== Ex. 37 + 38 ===")
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    links = extract_links(response.text)
    print(len(links), "legături unice")
    internal, external = split_links(links, "cybercor.org")
    print(len(internal), "interne,", len(external), "externe")

    print("\n=== Ex. 39 (test pe HTML cunoscut) ===")
    test_html = """
<html><body>
  <img src="/logo.png" alt="Logo">
  <IMG SRC="poza.jpg">
  <img alt="imagine fără src">
  <img src="https://cdn.example.com/banner.webp" />
  <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""
    finder = ImageFinder()
    finder.feed(test_html)
    print(finder.images)

    assert finder.images == [
        "/logo.png",                            # imagine obișnuită
        "poza.jpg",                             # tag scris cu majuscule
        "https://cdn.example.com/banner.webp",  # tag care se închide singur
    ], "Parserul nu a găsit exact imaginile așteptate"
    print("Testul a trecut!")

    print("\n=== Ex. 39 (pagina reală) ===")
    finder = ImageFinder()
    finder.feed(response.text)
    print(len(finder.images), "imagini găsite")
    for src in finder.images:
        print(src)
    print("Număr de '<img' în text:", response.text.lower().count("<img"))
    # O listă goală nu înseamnă neapărat o greșeală: imaginile pot fi puse
    # prin CSS sau SVG. Verificați și cu Ctrl+U în browser.
    time.sleep(1)

    print("\n=== Ex. 40 ===")
    first = page_fingerprint(BASE_URL)
    time.sleep(1)
    second = page_fingerprint(BASE_URL)
    print(first)
    print(second)
    print("Identice:", first == second)
    # Amprentele ar fi diferite dacă pagina s-a schimbat între cereri (conținut
    # dinamic: oră, token CSRF, anunțuri, contor de vizite) sau dacă
    # site-ul a fost actualizat între cele două rulări.
    time.sleep(1)

    print("\n=== Ex. 41 ===")
    with open("headers.json", "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2)
    with open("headers.json", encoding="utf-8") as file:
        loaded = json.load(file)
    print("Content-Type:", loaded.get("Content-Type", "lipsește"))

    print("\n=== Ex. 42 ===")
    print("cybercor.org ->", resolve("cybercor.org"))

    print("\n=== Ex. 43 ===")
    print("Zile rămase:", cert_days_left("cybercor.org"))

    # Verificați-vă: handle_starttag() este apelată de HTMLParser însuși, în
    # interiorul metodei feed(). Noi doar o definim; parserul o cheamă
    # automat la fiecare tag de deschidere întâlnit (principiul "callback").
