# Laborator 5: teste pentru decoder
# Student: Șibaev Vasile, grupa SI-265

from arsenal.forensics.decode import (
    citibil, desfa, desface_cu_xor, desface_straturi, ghici_strat, sparge_hash,
    xor_brute,
)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_strat():
    assert ghici_strat("%2Fetc") == "url"
    assert ghici_strat("48656c6c6f") == "hex"
    assert ghici_strat("U2FsdXQ=") == "base64"
    assert ghici_strat("Salut lume!") == "necunoscut"


def test_hex_si_url():
    assert desfa("48656c6c6f") == ("hex", b"Hello")
    assert desfa("%2Fetc%2Fpasswd") == ("url", b"/etc/passwd")


def test_straturi_multiple():
    # text -> base64 -> hex
    import base64
    val = base64.b64encode(b"FLAG{test}").decode().encode().hex()
    straturi, text, binar = desface_straturi(val)
    assert straturi == ["hex", "base64"]
    assert text == "FLAG{test}"
    assert binar is None


def test_xor_cu_cheie_de_un_octet():
    clar = b"Aceasta este un mesaj de test"
    criptat = bytes(b ^ 0x37 for b in clar)
    cheie, text = xor_brute(criptat)[0]
    assert cheie == 0x37
    assert text == clar.decode()


def test_hash_prin_dictionar():
    import hashlib
    h = hashlib.md5(b"sunshine").hexdigest()
    assert sparge_hash(h, ["abc", "sunshine"]) == ("md5", "sunshine")
    assert sparge_hash(h, ["abc", "xyz"]) == ("md5", None)


def test_citibil():
    assert citibil(b"abc 123")
    assert not citibil(b"\x00\x01")


def test_base64_peste_xor():
    import base64
    clar = b"FLAG{lant_complet_despicat}"
    val = base64.b64encode(bytes(b ^ 0x80 for b in clar)).decode()
    straturi, text, cheie = desface_cu_xor(val)
    assert cheie == 0x80
    assert text == clar.decode()
    assert straturi == ["base64", "xor(0x80)"]


def test_text_simplu_nu_e_confundat():
    straturi, text, cheie = desface_cu_xor("Salut lume!")
    assert straturi == [] and text == "Salut lume!" and cheie is None
