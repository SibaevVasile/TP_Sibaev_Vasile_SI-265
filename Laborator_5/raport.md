# Raport Laborator 5: forensics și steganografie

Student: Șibaev Vasile, grupa SI-265

Toate rezultatele de mai jos au fost produse de codul din acest folder, rulat pe fișierele din `probe/`.

## Lucrarea A. Decoderul universal

### A1-A4. Mesajul cu straturi (`probe/mesaj.txt`)

Intrare: `526b78425233747a64484a68644856796156396b5a56396a62325268636d...`

Straturile desfăcute, în ordine: **hex -> url -> base64**

Mesajul ascuns: **FLAG{straturi_de_codare!}**

### A5. XOR cu cheie de un octet (`probe/xor.bin`)

Cheia găsită: **43** (`0x2b`)

Textul în clar: **Mesaj XOR: parola este 'trandafir' iar cheia are un singur octet**

(încă 14 chei dau octeți imprimabili, dar fără sens)

### A6. Hash-uri sparte prin dicționar (`probe/hashuri.txt`)

| Hash (început) | Algoritm | Parola |
|---|---|---|
| `0571749e2ac330a7...` | md5 | sunshine |
| `af8978b1797b72ac...` | sha1 | dragon |
| `203b70b5ae883932...` | sha256 | trustno1 |

Algoritmul se alege după lungime: 32 = md5, 40 = sha1, 64 = sha256. Hash-ul nu se „decriptează”: se hash-uiește fiecare cuvânt din dicționar și se compară.

## Lucrarea B. Forensics pe fișiere și steganografie

### B1. Tipul real al fișierelor

| Fișier | Extensie | Tip real (magic bytes) |
|---|---|---|
| ascuns.png | .png | png |
| foto.jpg | .jpg | jpeg |
| hashuri.txt | .txt | 3035373137343965 |
| mesaj.txt | .txt | 3532366237383432 |
| wordlist.txt | .txt | 3132333435360a70 |
| xor.bin | .bin | 664e584a410b7364 |

Pentru fișierele text, coloana arată primii 8 octeți în hex (nu au o semnătură cunoscută).

### B2. strings din `probe/ascuns.png`

În tot fișierul sunt 16 șiruri imprimabile. În coada lui, după chunk-ul `IEND` (adică după sfârșitul imaginii PNG), apar:

```
pF]k{D
secret.txts
rLN-.Q
pF]k{D
secret.txtPK
```

Numele `secret.txt` indică un fișier lipit după imagine.

### B3. Metadate EXIF și GPS din `probe/foto.jpg`

```
Make = UTM-LAB
Model = Telefon-Demo
Software = pregateste.py
DateTimeOriginal = 2026:09:30 14:22:05
```

GPS brut: `{'GPSLatitudeRef': 'N', 'GPSLatitude': (47.0, 0.0, 37.8), 'GPSLongitudeRef': 'E', 'GPSLongitude': (28.0, 51.0, 49.7)}`

Coordonate în grade zecimale: **47.010500, 28.863806**

Locația pe hartă: https://www.openstreetmap.org/?mlat=47.010500&mlon=28.863806

Concluzie OSINT: poza dezvăluie unde a fost făcută. De aceea se șterge EXIF înainte de publicare.

### B4. Fișierul ascuns (file carving)

Semnătura ZIP (`PK\x03\x04`) a fost găsită la octetul **1704**; tot ce urmează a fost salvat ca `gasit.zip`. Conținut:

`secret.txt`:

```
FLAG{fisier_lipit_la_coada}
Acest fisier era ascuns dupa IEND.
```

### B5-B6. Steganografie LSB

Mesajul ascuns în `stego.png`: `FLAG{LSB_STEGANOGRAPHY}` (192 biți, cu un octet 0 la final).

Diferența maximă dintre un canal al pozei originale și al celei cu mesaj: **1**, deci poza arată identic cu ochiul liber.

Mesajul dezvăluit înapoi din `stego.png`: **FLAG{LSB_STEGANOGRAPHY}**

`stego.png` se salvează în PNG (fără pierdere); un JPG ar recompresa imaginea și ar distruge biții ascunși.
