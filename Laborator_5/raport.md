# Raport Laborator 5: forensics și steganografie

Student: Șibaev Vasile, grupa SI-265

Toate rezultatele de mai jos au fost produse de codul din acest folder, rulat pe fișierele din `probe/`.

## Lucrarea A. Decoderul universal

### A1-A4. Mesajul cu straturi (`probe/mesaj.txt`)

Intrare: `TkRZMFl6UXhORGMzWWpjek56UTNNall4TnpRM05UY3lOamsxWmpZME5qVTFa...`

Straturile desfăcute, în ordine: **base64 -> base64 -> hex**

Mesajul ascuns: **FLAG{straturi_de_encoding}**

### A5. XOR cu cheie de un octet (`probe/xor.bin`)

Cheia găsită: **128** (`0x80`)

Textul în clar: **Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}**

(încă 16 chei dau octeți imprimabili, dar fără sens)

### A6. Hash-uri sparte prin dicționar (`probe/hashuri.txt`)

| Hash (început) | Algoritm | Parola |
|---|---|---|
| `5f4dcc3b5aa765d6...` | md5 | password |
| `8621ffdbc5698829...` | md5 | dragon |
| `d8578edf8458ce06...` | md5 | qwerty |
| `0d107d09f5bbe40c...` | md5 | letmein |
| `d0763edaa9d9bd2a...` | md5 | monkey |

Algoritmul se alege după lungime: 32 = md5, 40 = sha1, 64 = sha256. Hash-ul nu se „decriptează”: se hash-uiește fiecare cuvânt din dicționar și se compară.

## Lucrarea B. Forensics pe fișiere și steganografie

### B1. Tipul real al fișierelor

| Fișier | Extensie | Tip real (magic bytes) |
|---|---|---|
| ascuns.png | .png | png |
| challenge.bin | .bin | text (fără semnătură) |
| challenge_hint.txt | .txt | text (fără semnătură) |
| foto.jpg | .jpg | jpeg |
| hashuri.txt | .txt | text (fără semnătură) |
| mesaj.txt | .txt | text (fără semnătură) |
| wordlist.txt | .txt | text (fără semnătură) |
| xor.bin | .bin | binar (semnătură necunoscută) |

Tipul se citește din primii octeți (magic bytes), nu din extensie. Fișierele text nu au semnătură; `xor.bin` este binar (octeți criptați).

### B2. strings din `probe/ascuns.png`

În tot fișierul sunt 6 șiruri imprimabile. În coada lui, după chunk-ul `IEND` (adică după sfârșitul imaginii PNG), apar:

```
secret.txtFLAG{ascuns_prin_carving}
secret.txtPK
```

Numele `secret.txt` indică un fișier lipit după imagine.

### B3. Metadate EXIF și GPS din `probe/foto.jpg`

```
Model = iPhone 13
DateTime = 2026:09:14 10:30:00
Make = Apple
```

GPS brut: `{'GPSLatitudeRef': 'N', 'GPSLatitude': (47.0, 1.0, 0.0), 'GPSLongitudeRef': 'E', 'GPSLongitude': (28.0, 51.0, 27.0)}`

Coordonate în grade zecimale: **47.016667, 28.857500**

Locația pe hartă: https://www.openstreetmap.org/?mlat=47.016667&mlon=28.857500

Concluzie OSINT: poza dezvăluie unde a fost făcută. De aceea se șterge EXIF înainte de publicare.

### B4. Fișierul ascuns (file carving)

Semnătura ZIP (`PK\x03\x04`) a fost găsită la octetul **781**; tot ce urmează a fost salvat ca `gasit.zip`. Conținut:

`secret.txt`:

```
FLAG{ascuns_prin_carving}
```

### B5-B6. Steganografie LSB

Mesajul ascuns în `stego.png`: `FLAG{LSB_STEGANOGRAPHY}` (192 biți, cu un octet 0 la final).

Diferența maximă dintre un canal al pozei originale și al celei cu mesaj: **1**, deci poza arată identic cu ochiul liber.

Mesajul dezvăluit înapoi din `stego.png`: **FLAG{LSB_STEGANOGRAPHY}**

`stego.png` se salvează în PNG (fără pierdere); un JPG ar recompresa imaginea și ar distruge biții ascunși.

## Vârful sălii: `challenge.bin`

Lanțul desfăcut: **base64 -> xor(0x80)**

Cheia XOR: **128** (`0x80`)

Textul în clar: **FLAG{lant_complet_despicat}**

Verificare: md5 al textului clar = `8c4eb02d9dcef7d0ff91d8e4c7fea91b`, se potrivește cu cel din `challenge_hint.txt`.
