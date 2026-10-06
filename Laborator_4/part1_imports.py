# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265

import time
BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# ---------------------------------------------------------------------------
# Exercițiul 1. Primul import
# ---------------------------------------------------------------------------
print("=== Exercițiul 1 ===")
import requests
import urllib.request

print("Versiunea requests:", requests.__version__)

# requests este un pachet EXTERN (scris de terți, nu vine cu Python), de aceea
# trebuie descărcat și instalat cu `pip install requests` din PyPI.
# urllib face parte din BIBLIOTECA STANDARD, care se instalează odată cu
# Python, deci este deja disponibil și nu are nevoie de pip.


# ---------------------------------------------------------------------------
# Exercițiul 2. Două stiluri de import
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 2 ===")
# Stilul 1: import requests
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (import requests):", response.status_code)
time.sleep(1)

# Stilul 2: from requests import get
from requests import get

response = get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (from requests import get):", response.status_code)

# Avantaj "import requests": se vede mereu de unde vine funcția (requests.get),
#   deci nu apar confuzii de nume cu alte funcții numite "get".
# Avantaj "from requests import get": codul este mai scurt, fără prefix.
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 3. Alias-uri
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 3 ===")
import requests as rq

response = rq.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (rq.get):", response.status_code)

# Un alias face codul mai ușor de citit când numele complet e lung sau când
#   alias-ul este o convenție cunoscută de toată lumea
#   (import numpy as np, import pandas as pd).
# Un alias îl face mai greu de citit când este ales arbitrar sau prea scurt
#   (rq, x, r), pentru că cititorul trebuie să ghicească ce reprezintă,
#   sau când alt cod folosește alt alias pentru același modul.
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 4. Doar biblioteca standard
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 4 ===")
req = urllib.request.Request(BASE_URL, headers={"User-Agent": "WebLab-Sibaev-Vasile"})
with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
    print("Status:", resp.status)
    body = resp.read().decode("utf-8")  # .read() dă bytes -> .decode() dă str
    print(body[:200])


# ---------------------------------------------------------------------------
# Exercițiul 5. Priviți în interiorul unui modul
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 5 ===")
print(dir(requests))

# Trei nume alese din rezultat:
#   get      -> este o FUNCȚIE (requests.get(url, ...))
#   Session  -> este o CLASĂ (requests.Session())
#   exceptions -> este un MODUL (submodulul requests.exceptions)
for name in ("get", "Session", "exceptions"):
    print(name, "->", type(getattr(requests, name)).__name__)


# ---------------------------------------------------------------------------
# Exercițiul 6. Citiți documentația
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 6 ===")
help(requests.get)
# În help() găsim parametrul "timeout" (timpul maxim de așteptare, în secunde),
# transmis prin **kwargs către requests.request().
time.sleep(1)
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cerere cu timeout=%s -> %s" % (TIMEOUT, response.status_code))
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 7. Cronometrarea unei cereri
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 7 ===")
start = time.perf_counter()
response = requests.get(BASE_URL, timeout=TIMEOUT)
duration = time.perf_counter() - start

print(f"time.perf_counter():  {duration:.3f} s")
print(f"response.elapsed:     {response.elapsed.total_seconds():.3f} s")
# perf_counter măsoară tot timpul scurs în programul nostru (inclusiv
# pregătirea cererii și citirea corpului), iar response.elapsed măsoară doar
# intervalul dintre trimiterea cererii și primirea antetelor răspunsului.
# De aceea prima valoare este de obicei puțin mai mare.


# ---------------------------------------------------------------------------
# Exercițiul 8. Când un import eșuează
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 8 ===")
try:
    import bs4  
    print("bs4 este instalat, versiunea", bs4.__version__)
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")


# ---------------------------------------------------------------------------
# Verificați-vă: modul vs. pachet vs. bibliotecă
# ---------------------------------------------------------------------------
# - MODUL: un singur fișier .py (ex.: time.py, webtools.py).
# - PACHET: un director cu mai multe module, de obicei cu __init__.py
#   (ex.: requests, urllib).
# - BIBLIOTECĂ: termen general, o colecție de cod reutilizabil pentru o
#   anumită sarcină; poate fi un modul sau un pachet
#   (ex.: "biblioteca standard", "biblioteca requests").
