# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# Ex. 21 -------------------------------------------------------------------
def fetch(url, timeout=10):
    """Descarcă url cu GET și returnează obiectul răspuns.

    Ex. 21: prima funcție. Ex. 23: parametrul `timeout` are valoare implicită.
    """
    return requests.get(url, timeout=timeout)


# Ex. 22 -------------------------------------------------------------------
def get_status(url: str) -> int:
    """Returnează doar codul de stare HTTP pentru adresa url (Ex. 22 + 26)."""
    return fetch(url).status_code


# Ex. 24 + 25 ----------------------------------------------------------------
def get_title(html: str) -> str:
    """Returnează titlul paginii dintr-un șir HTML.

    Primește codul HTML (str), nu face nicio operație de rețea și
    returnează textul dintre <title> și </title>, fără spații la capete.
    Dacă titlul lipsește, returnează un șir gol.
    """
    start_tag = "<title>"
    start = html.find(start_tag)
    end = html.find("</title>")
    if start == -1 or end == -1:
        return ""
    return html[start + len(start_tag):end].strip()


# Ex. 27 -------------------------------------------------------------------
def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu succes (cod < 400), altfel False.

    Nu se oprește cu eroare: excepțiile de rețea sunt prinse și dau False.
    """
    try:
        return fetch(url).status_code < 400
    except requests.RequestException:
        return False


# Ex. 28 -------------------------------------------------------------------
def check_paths(base: str, paths: list) -> dict:
    """Returnează un dicționar {cale: cod_de_stare} pentru fiecare cale.

    Face o pauză de 1 secundă între cereri. La eroare de rețea, valoarea e None.
    """
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(1)
        try:
            results[path] = get_status(base + path)
        except requests.RequestException:
            results[path] = None
    return results


# Ex. 29 -------------------------------------------------------------------
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului `name` de la url sau `default` dacă lipsește."""
    return fetch(url).headers.get(name, default)


# Ex. 30 -------------------------------------------------------------------
def security_headers(url: str) -> dict:
    """Verifică cele 5 antete de securitate și returnează {antet: True/False}."""
    wanted = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
    ]
    headers = fetch(url).headers
    return {name: name in headers for name in wanted}


# Ex. 31 -------------------------------------------------------------------
def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers() și returnează un șir ca '3/5'."""
    present = sum(1 for ok in results.values() if ok)
    return f"{present}/{len(results)}"


# Ex. 32 -------------------------------------------------------------------
def fetch_robots(base: str):
    """Returnează textul din /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(base + "/robots.txt")
    except requests.RequestException:
        return None
    return response.text if response.status_code == 200 else None


def disallowed_paths(robots_text) -> list:
    """Returnează lista tuturor valorilor `Disallow:`; acceptă și None."""
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


# Ex. 33 -------------------------------------------------------------------
def response_times(*urls) -> dict:
    """Returnează {url: secunde} pentru oricâte adrese primește.

    *urls colectează argumentele poziționale într-un tuplu.
    """
    times = {}
    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(1)
        start = time.perf_counter()
        fetch(url)
        times[url] = round(time.perf_counter() - start, 3)
    return times


# Ex. 34 -------------------------------------------------------------------
def log(message, **details):
    """Afișează mesajul urmat de fiecare detaliu, separate prin ' | '.

    **details colectează argumentele cu nume într-un dicționar.
    """
    parts = [str(message)] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(parts))


# ---------------------------------------------------------------------------
# Apeluri de demonstrație (fiecare funcție este apelată cel puțin o dată)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Ex. 21 ===")
    print(fetch(BASE_URL).status_code)
    time.sleep(1)

    print("\n=== Ex. 22 ===")
    for path in ("/", "/robots.txt", "/sitemap.xml"):
        print(path, get_status(BASE_URL + path))
        time.sleep(1)

    print("\n=== Ex. 23 ===")
    print("timeout implicit:", fetch(BASE_URL).status_code)
    time.sleep(1)
    print("timeout=3:", fetch(BASE_URL, timeout=3).status_code)
    time.sleep(1)

    print("\n=== Ex. 24 ===")
    print(get_title(fetch(BASE_URL).text))
    time.sleep(1)

    print("\n=== Ex. 25 ===")
    help(get_title)

    print("\n=== Ex. 26 ===")
    try:
        get_status(123)
    except Exception as err:
        print("Eroare:", type(err).__name__, "-", err)
    # Adnotările de tip NU ne opresc: Python nu le verifică la rulare, ele sunt
    # doar documentație/ajutor pentru editor și pentru instrumente ca mypy.
    # Eroarea vine din requests (URL fără schemă), nu din adnotare.

    print("\n=== Ex. 27 ===")
    print(page_exists(BASE_URL))
    print(page_exists("https://this-domain-does-not-exist.invalid"))
    time.sleep(1)

    print("\n=== Ex. 28 ===")
    print(check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))
    time.sleep(1)

    print("\n=== Ex. 29 ===")
    print(get_header(BASE_URL, name="Server"))
    time.sleep(1)

    print("\n=== Ex. 30 ===")
    sec = security_headers(BASE_URL)
    for header, present in sec.items():
        print(f"{header}: {present}")
    time.sleep(1)

    print("\n=== Ex. 31 ===")
    print(score_headers(sec))
    time.sleep(1)
    print(score_headers(security_headers(BASE_URL)))
    time.sleep(1)

    print("\n=== Ex. 32 ===")
    robots = fetch_robots(BASE_URL)
    print(disallowed_paths(robots))
    print(disallowed_paths(None))  # funcționează și cu None
    time.sleep(1)

    print("\n=== Ex. 33 ===")
    print(response_times(BASE_URL, BASE_URL + "/robots.txt"))

    print("\n=== Ex. 34 ===")
    log("verificat", url=BASE_URL, status=200)

    # Verificați-vă: print() în interiorul unei funcții doar AFIȘEAZĂ valoarea pe
    # ecran (funcția returnează None și rezultatul nu mai poate fi folosit
    # în cod). return DĂ valoarea înapoi apelantului, care o poate stoca, testa,
    # transmite altei funcții (ex.: score_headers(security_headers(url))).
