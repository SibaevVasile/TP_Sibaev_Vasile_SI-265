# Laborator: funcții, metode și importuri pe web
# Student: Șibaev Vasile, grupa SI-265

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# ---------------------------------------------------------------------------
# Exercițiul 9. Elementele de bază ale răspunsului
# ---------------------------------------------------------------------------
print("=== Exercițiul 9 ===")
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("status_code:", response.status_code)  # atribut
print("ok:", response.ok)                    # atribut (bool; în requests e property)
print("url:", response.url)                  # atribut
print("encoding:", response.encoding)        # atribut
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 10. Tratarea erorilor cu o metodă
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 10 ===")
response.raise_for_status()  # metodă: nu face nimic dacă codul e 2xx
print("Pagina principală este în regulă.")

time.sleep(1)
try:
    bad = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    bad.raise_for_status()  # ridică HTTPError pentru 4xx / 5xx
    print("Pagina a fost găsită (neașteptat).")
except requests.HTTPError as err:
    print("Ups, pagina cerută nu a putut fi încărcată:", err)
time.sleep(1)
# Observație: cybercor.org este o aplicație JavaScript care returnează pagina
# principală (200) pentru orice adresă, deci nu ridică HTTPError pentru
# pagini inexistente. raise_for_status() funcționează doar dacă serverul
# trimite un cod 4xx/5xx.

# ---------------------------------------------------------------------------
# Exercițiul 11. Toate antetele
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 11 ===")
for name, value in response.headers.items():
    print(f"{name}: {value}")


# ---------------------------------------------------------------------------
# Exercițiul 12. Metode de dicționar
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 12 ===")
print("Server:", response.headers.get("Server", "lipsește"))
print("Content-Type:", response.headers.get("Content-Type", "lipsește"))
print("content-type (litere mici):", response.headers.get("content-type", "lipsește"))
# Observație: se obține același rezultat. response.headers este un
# CaseInsensitiveDict: numele antetelor nu țin cont de majuscule/minuscule
# (așa cere și standardul HTTP), spre deosebire de un dict obișnuit.


# ---------------------------------------------------------------------------
# Exercițiul 13. Înlănțuirea metodelor de șir
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 13 ===")
count = response.text.lower().count("cyber")
print("Cuvântul 'cyber' apare de", count, "ori")
# Se pot înlănțui deoarece .lower() returnează un șir nou (str), iar orice str
# are metoda .count(). Rezultatul fiecărei metode este obiectul pe care se
# aplică următoarea.


# ---------------------------------------------------------------------------
# Exercițiul 14. Găsirea titlului
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 14 ===")
html = response.text
start = html.find("<title>") + len("<title>")
end = html.find("</title>")
if start >= len("<title>") and end != -1:
    print("Titlu:", html[start:end].strip())
else:
    print("Titlul nu a fost găsit.")


# ---------------------------------------------------------------------------
# Exercițiul 15. Numărarea liniilor
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 15 ===")
lines = html.splitlines()
print("Număr de linii:", len(lines))
if lines:
    print("Lungimea celei mai lungi linii:", len(max(lines, key=len)))


# ---------------------------------------------------------------------------
# Exercițiul 16. Verificarea HTTPS
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 16 ===")
if response.url.startswith("https://"):
    print("Conexiune securizată")
else:
    print("Conexiune nesecurizată")
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 17. Urmărirea redirecționărilor
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 17 ===")
r = requests.get("http://cybercor.org", timeout=TIMEOUT)
for hop in r.history:
    print(hop.status_code, hop.url)
print("URL final:", r.url)
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 18. HEAD versus GET
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 18 ===")
head_resp = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
get_resp = requests.get(BASE_URL, timeout=TIMEOUT)
print("len(content) HEAD:", len(head_resp.content))
print("len(content) GET: ", len(get_resp.content))
# HEAD cere serverului doar antetele, fără corp, deci .content este gol (0
# octeți). GET returnează și corpul (HTML-ul paginii). HEAD e util pentru a
# verifica rapid dacă o pagină există, fără a descărca conținutul.
time.sleep(1)


# ---------------------------------------------------------------------------
# Exercițiul 19. Cookie-uri
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 19 ===")
if len(get_resp.cookies) == 0:
    print("Niciun cookie setat")
else:
    for cookie in get_resp.cookies:
        print(cookie.name, "| secure =", cookie.secure)


# ---------------------------------------------------------------------------
# Exercițiul 20. Sesiuni
# ---------------------------------------------------------------------------
print("\n=== Exercițiul 20 ===")
session = requests.Session()
session.headers.update({"User-Agent": "WebLab-Sibaev-Vasile"})
echo = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)  # doar httpbin
print(echo.json())
sent = echo.json()["headers"].get("User-Agent")
print("User-Agent primit de server:", sent)
print("Antetul a fost trimis:", sent == "WebLab-Sibaev-Vasile")


# ---------------------------------------------------------------------------
# Verificați-vă: response.text vs response.json()
# ---------------------------------------------------------------------------
# response.text este un ATRIBUT (o valoare deja calculată/decodificată, o
# proprietate), deci se citește fără paranteze. response.json() este o METODĂ:
# execută o acțiune (parsează corpul ca JSON și poate ridica o eroare dacă
# nu e JSON valid), deci se apelează cu paranteze.
