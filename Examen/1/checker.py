import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    if path.startswith("/"):
        return "https://" + host + path
    else:
        return "https://" + host + "/" + path


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    if url.startswith("https://"):
        return True
    else:
        return False


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url, timeout=5)
        print("Status:", r.status_code)
        print("Content-Type:", r.headers.get("Content-Type"))
    except Exception as e:
        print("Eroare:", e)


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        server = r.headers.get("Server")
        if server is None:
            server = "unknown"  
        return {
            "status": r.status_code,
            "content_type": r.headers.get("Content-Type"),
            "length": len(r.content),
            "server": server
        }
    except Exception as e:
        return {"status": None, "error": "Eroare la conexiune"}


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    rezultate = []
    reusite = 0
    esuate = 0

    for site in SITES:
        rez = check_site(site)
        rezultate.append((site, rez))
        if rez.get("status") == 200:
            reusite += 1
        else:
            esuate += 1

    bune = []
    for item in rezultate:
        site = item[0]
        rez = item[1]
        if rez.get("status") == 200:
            bune.append((site, rez))

    bune.sort(key=lambda x: x[1]["length"], reverse=True)

    for item in bune:
        site = item[0]
        rez = item[1]
        print(site, "->", rez["status"], ",", rez["length"], "octeți")

    print("Reușite:", reusite, "Eșuate:", esuate)


def check_headers(url):
    """Verifică anteturile de securitate și returnează un dicționar cu present, missing, score."""
    try:
        r = requests.get(url, timeout=5)
       
        anteturi_primite = {}
        for k, v in r.headers.items():
            anteturi_primite[k.lower()] = v

        present = []
        missing = []

        for h in SECURITY_HEADERS:
            if h.lower() in anteturi_primite:
                present.append(h)
            else:
                missing.append(h)

        score = int((len(present) / len(SECURITY_HEADERS)) * 100)

        return {
            "present": present,
            "missing": missing,
            "score": score
        }
    except Exception as e:
        return {"status": None, "error": "Eroare la conexiune"}

def retry_check(url, attempts=3):
    """Încearcă de cel mult attempts ori în caz de eroare / status >= 500."""
    incercari_facute = 0
    ultimul_status = None
    ultima_eroare = None

    while incercari_facute < attempts:
        incercari_facute += 1
        try:
            r = requests.get(url, timeout=5)
            ultimul_status = r.status_code
         
            if ultimul_status < 500:
                return {
                    "status": ultimul_status,
                    "attempts": incercari_facute
                }
        except Exception as e:
            ultimul_status = None
            ultima_eroare = str(e)

    rezultat = {
        "status": ultimul_status,
        "attempts": incercari_facute
    }
    
    if ultimul_status is None and ultima_eroare:
        rezultat["error"] = ultima_eroare
    return rezultat
