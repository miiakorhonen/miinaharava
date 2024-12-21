"""
Miinaharava - klassinen peli.

Tässä pelissä sinun tehtävänäsi on päätellä miinojen sijainti vihjeiden avulla ja välttää niihin
astumista. Peli etenee klikkaamalla miinattomia ruutuja niin kauan, kunnes vain miinan sisältävät
ruudut ovat jäljellä. Paljastuvat numeroruudut kertovat ruutua ympäröivien miinojen lukumäärän.

Voit valita kentän leveyden ja pituuden sekä miinojen määrän. Lisäksi voit merkitä miinoja lipulla
painamalla hiiren oikeaa painiketta. Pelaamisen jälkeen voit katsella tilastoja pelatuista peleistä.

Onnea matkaan!
"""

import json
from datetime import datetime
import random
import haravasto

TIEDOSTO_PELITULOKSET = "pelitulokset.json"

tila = {
    "kentta": [],  # sisältää aukaistut, harmaat ruudut ("0") sekä miinat ja numerot
    "kansi": [],  # sisältää aukaisemattomat, valkoiset ruudut (" ")
    "kentan_leveys": 0,
    "kentan_pituus": 0,
    "miinat": 0,
    "aukaistut": 0,
    "aukaisemattomat": 0,
    "vuorot": 0,
    "lopputulos": "",
    "peli_kaynnissa": True,
    "aloitusaika": None,
    "lopetusaika": None
}


def kysy_kokonaisluku(pyynto):
    """
    Kysyy käyttäjältä kokonaislukua käyttäen kysymyksenä parametrina annettua
    merkkijonoa. Virheellisen syötteen kohdalla käyttäjälle näytetään virheilmoitus.
    Käyttäjän antama kelvollinen syöte palautetaan kokonaislukuna.

    :param str pyynto: käyttäjälle esitettävä kysymys
    :return : kelvollinen syöte kokonaislukuna
    """

    while True:
        try:
            kokonaisluku = int(input(pyynto))
            if kokonaisluku > 0:
                return kokonaisluku
            print("Arvon tulee olla positiivinen kokonaisluku. Yritä uudelleen.")
        except ValueError:
            print("Virheellinen syöte. Anna positiivinen kokonaisluku.")


def kysy_kentan_tiedot():
    """
    Kysyy käyttjältä kentän tiedot eli leveyden ja pituuden sekä miinojen määrän.
    Arvot tallennetaan globaaliin tila-sanakirjaan.
    """

    tila["kentan_leveys"] = kysy_kokonaisluku("Anna kentän leveys ruutuina: ")
    tila["kentan_pituus"] = kysy_kokonaisluku("Anna kentän pituus ruutuina: ")
    tila["miinat"] = kysy_kokonaisluku("Anna miinojen määrä: ")

    while tila["miinat"] > tila["kentan_leveys"] * tila["kentan_pituus"]:
        print("Miinoja on liikaa. Yritä uudelleen.")
        tila["miinat"] = kysy_kokonaisluku("Anna miinojen määrä: ")


def alusta_kentta():
    """
    Luo tyhjän kentän ja kannen käyttämällä käyttäjältä kysyttyjä kentän leveyttä ja pituutta sekä
    täyttää ne "tyhjillä" ("0" ja " "). Lisäksi luo listan vapaista ruuduista (jaljella),
    miinoittaa kentan ja laskee miinojen määrän.

    Funktio ei palauta mitään, vaan muokkaa globaalia tila-sanakirjaa.
    """

    kentta = []
    kansi = []
    for _ in range(tila["kentan_pituus"]):  # käydään läpi rivejä
        kentta.append([])
        kansi.append([])
        for _ in range(tila["kentan_leveys"]):  # käydään läpi sarakkeita
            kentta[-1].append("0")
            kansi[-1].append(" ")

    tila["kentta"] = kentta
    tila["kansi"] = kansi

    jaljella = []
    for x in range(tila["kentan_leveys"]):
        for y in range(tila["kentan_pituus"]):
            jaljella.append((x, y))

    miinoita(tila["kentta"], jaljella, tila["miinat"])

    for rivi_nro, rivi in enumerate(tila["kentta"]):
        for sarake_nro, merkki in enumerate(rivi):
            if merkki != "x":
                kentta[rivi_nro][sarake_nro] = laske_miinat(sarake_nro, rivi_nro)


def kasittele_hiiri(x, y, nappi, muokkausnapit):
    """
    Funktiota kutsutaan, kun pelaaja klikkaa sovellusikkunaa hiirellä. Hiiren vasenta nappia
    painettaessa pelin ollessa käynnissä lasketaan vuoroja ja kutsutaan tarkista_pelin_tila-
    funktiota tai kutsutaan pelin lopettavaa funktiota, jos peli ei ole käynnissä. Hiiren oikeaa
    nappia painamalla käyttäjä voi pelin ollessa käynnissä asettaa kentälle lipun.

    Funktio ei palauta mitään, vaan muokkaa globaalia tila-sanakirjaa.

    :param int x: klikkauksen sijainnin x-koordinaatti
    :param int y: klikkauksen sijainnin y-koordinaatti
    :param int nappi: painettu hiiren nappi (vasen tai oikea)
    :param int muokkausnapit: näppäimistön shift, alt, ctrl jne. näppäimiä
    """

    kansi = tila["kansi"]
    x = int(x / 40)
    y = int(y / 40)

    if nappi == haravasto.HIIRI_VASEN:
        tila["vuorot"] += 1

        if tila["peli_kaynnissa"]:
            if tila["aloitusaika"] is None:
                tila["aloitusaika"] = datetime.now()
            tarkista_pelin_tila(x, y)
        else:
            haravasto.lopeta()

    elif nappi == haravasto.HIIRI_OIKEA:
        if tila["peli_kaynnissa"]:
            kansi[y][x] = "f"


def piirra_kansi():
    """
    Piirtää kaksiulotteisena listana kuvatun miinakentän ruudut näkyviin peli-ikkunaan.
    Funktiota kutsutaan aina kun pelimoottori pyytää ruudun näkymän päivitystä.
    """

    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    for rivi_nro, rivi in enumerate(tila["kansi"]):
        for sarake_nro, merkki in enumerate(rivi):
            haravasto.lisaa_piirrettava_ruutu(merkki, sarake_nro * 40, rivi_nro * 40)
    haravasto.piirra_ruudut()


def miinoita(miinoitettava_kentta, vapaat_ruudut, miinojen_lkm):
    """
    Asettaa kentälle n kpl miinoja satunnaisiin paikkoihin.

    :param list miinoitettava_kentta: kenttää kuvaava lista, johon miinat asetetaan
    :param list vapaat_ruudut: lista, joka sisältää koordinaattipari-monikkoja
    :param int miinojen_lkm: asetettavien miinojen lukumäärä
    """

    for _ in range(miinojen_lkm):
        piste = random.choice(vapaat_ruudut)
        x = piste[0]
        y = piste[1]
        miinoitettava_kentta[y][x] = "x"
        vapaat_ruudut.remove(piste)


def tulvataytto(x, y):
    """
    Suorittaa tulvatäyttöoperaation alkaen annetusta x, y -pisteestä siten, että aukaistaan kaikki
    ympäröivät ja niitä ympäröivät jne. ruudut joka suuntaan niin pitkälle, että saavutetaan
    miinakentän raja tai ensimmäinen numeroruutu, joka myös aukaistaan.

    Funktio ei palauta mitään, vaan muokkaa globaalia tila-sanakirjaa.

    :param int x: klikkauksen sijainnin x-koordinaatti
    :param int y: klikkauksen sijainnin y-koordinaatti
    """

    kentta = tila["kentta"]
    kansi = tila["kansi"]
    koordinaatit = [(x, y)]

    while koordinaatit:
        x, y = koordinaatit.pop(-1)
        kansi[y][x] = kentta[y][x]
        tila["aukaistut"] += 1
        for rivi in range(-1, 2):
            for sarake in range(-1, 2):
                if (0 <= x + sarake < tila["kentan_leveys"] and
                        0 <= y + rivi < tila["kentan_pituus"]):
                    if (kansi[y + rivi][x + sarake] == " " and
                            (x + sarake, y + rivi) not in koordinaatit):
                        if kentta[y + rivi][x + sarake] == "0":
                            koordinaatit.append((x + sarake, y + rivi))
                        elif kentta[y + rivi][x + sarake] != "x":
                            kansi[y + rivi][x + sarake] = kentta[y + rivi][x + sarake]
                            tila["aukaistut"] += 1

    tila["aukaisemattomat"] = (tila["kentan_leveys"] * tila["kentan_pituus"]) - tila["aukaistut"]


def tarkista_pelin_tila(x, y):
    """
    Tarkistaa, tuliko pelaajalle voitto, häviö vai jatkuuko peli.
    Jos valittu ruutu sisältää miinan, peli päättyy häviöön. Muussa tapauksessa suoritetaan
    tulvatäyttö paljastaen kaikki ympäröivät tyhjät ruudut. Lisäksi tarkastetaan, onko
    aukaisemattomien ruutujen määrä sama miinojen lukumäärän kanssa, jolloin peli päättyy voittoon.
    Jos peli päättyy, otetaan ylös lopetusaika ja tallennetaan pelin tiedot tilastotiedostoon.

    Funktio ei palauta mitään, vaan muokkaa globaalia tila-sanakirjaa.

    :param int x: klikkauksen sijainnin x-koordinaatti
    :param int y: klikkauksen sijainnin y-koordinaatti
    """

    kentta = tila["kentta"]
    kansi = tila["kansi"]

    if kentta[y][x] == "x":
        kansi[y][x] = "x"
        print("Osuit miinaan. Hävisit pelin.\n")
        tila["lopputulos"] = "häviö"

    else:
        tulvataytto(x, y)

    if tila["aukaisemattomat"] == tila["miinat"]:
        print("Onneksi olkoon, voitit pelin!\n")
        tila["lopputulos"] = "voitto"

    if tila["lopputulos"] != "":
        tila["lopetusaika"] = datetime.now()
        tallenna_tilastoon()
        tila["peli_kaynnissa"] = False


def laske_miinat(x, y):
    """
    Laskee klikatun ruudun ympärillä olevien miinojen lukumäärän ja palauttaa sen.

    :param int x: klikkauksen sijainnin x-koordinaatti
    :param int y: klikkauksen sijainnin y-koordinaatti
    :return str miinat: miinojen lukumäärä
    """

    kentta = tila["kentta"]
    tila_pituus = len(kentta)
    tila_leveys = len(kentta[0])
    miinat = 0
    for rivi in range(-1, 2):
        for sarake in range(-1, 2):
            if 0 <= x + sarake < tila_leveys and 0 <= y + rivi < tila_pituus:
                if kentta[y + rivi][x + sarake] == "x":
                    miinat += 1
    return str(miinat)


def lataa_tilasto():
    """
    Lukee JSON-muotoisen datan tiedostosta ja palauttaa sen sisällön sanakirjana. Jos tiedostoa ei
    voida avata tai sen sisältö ei ole kelvollista JSON-muotoa, koodi palauttaa tyhjän sanakirjan
    ({}).

    :return dict tilasto: tiedoston sisältö sanakirjana, jos luku onnistuu
    :return dict {}: tyhjä sanakirja, jos tiedostoa ei löydy tai JSON on virheellinen
    """

    try:
        with open(TIEDOSTO_PELITULOKSET, encoding="utf-8") as lahde:
            tilasto = json.load(lahde)
    except (IOError, json.JSONDecodeError):
        return {}

    return tilasto


def tallenna_tilastoon():
    """
    Tallentaa pelitilastot JSON-tiedostoon. Ennen tallentamista lasketaan pelin kesto minuuteissa,
    muodostetaan tietorakenne (tiedot-sanakirja) pelin tilastojen tallennukseen, ladataan
    aikaisemmin tallennetut tilastot tiedostosta ja lisätään uusi tilasto vanhoihin tilastoihin.
    Jos tiedostoa ei voida avata, tulostetaan virheilmoitus.

    Funktio ei palauta mitään.
    """

    kesto = tila["lopetusaika"] - tila["aloitusaika"]
    kesto_min = kesto.total_seconds() / 60

    tiedot = {
        tila["aloitusaika"].strftime("%Y-%m-%d %H:%M:%S"): {
            "kentan_leveys": tila["kentan_leveys"],
            "kentan_pituus": tila["kentan_pituus"],
            "miinat": tila["miinat"],
            "vuorot": tila["vuorot"],
            "lopputulos": tila["lopputulos"],
            "aloitusaika": tila["aloitusaika"].strftime("%Y-%m-%d %H:%M:%S"),
            "lopetusaika": tila["lopetusaika"].strftime("%Y-%m-%d %H:%M:%S"),
            "kesto": f"{kesto_min:.2f}"
        }}

    ladattu_tiedosto = lataa_tilasto()

    ladattu_tiedosto.update(tiedot)

    try:
        with open(TIEDOSTO_PELITULOKSET, "w", encoding="utf-8") as kohde:
            json.dump(ladattu_tiedosto, kohde)
    except IOError:
        print("Kohdetiedostoa ei voitu avata. Tallennus epäonnistui")


def main():
    """
    Alustaa ja käynnistää pelin käyttämällä Haravasto-kirjastoa graafisen käyttöliittymän
    toteuttamiseen. Funktiossa alustetaan pelitilan muuttujat, ladataan tarvittavat kuvat, luodaan
    pelin ikkuna, asetetaan hiiri- ja piirtokäsittelijät sekä käynnistetään peli.

    Funktio ei palauta mitään.
    """

    tila["peli_kaynnissa"] = True
    tila["aukaistut"] = 0
    tila["aukaisemattomat"] = 0
    tila["vuorot"] = 0
    tila["lopputulos"] = ""
    tila["aloitusaika"] = None
    tila["lopetusaika"] = None
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(len(tila["kentta"][0]) * 40, len(tila["kentta"]) * 40)
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    haravasto.aseta_piirto_kasittelija(piirra_kansi)
    haravasto.aloita()


def uusi_peli():
    """
    Funktiota kutsutaan, jos pelaaja valitsee haluavansa pelata uuden pelin. Funktiossa kutsutaan
    kysy_kentan_tiedot, alusta_kentta sekä main-funtkioita.

    Funktio ei palauta mitään.
    """

    kysy_kentan_tiedot()
    alusta_kentta()
    main()


def katso_tilastoja():
    """
    Funktiota kutsutaan, jos pelaaja valitsee haluavansa katsella pelitilastoja. Funktio lataa
    pelitilastot ja tulostaa niistä tietoja terminaaliin muotoiltuna tekstinä. Jos tiedostoa ei ole
    olemassa tai se on tyhjä, tulostetaan virheilmoitus.

    Funktio ei palauta mitään.
    """

    ladattu_tiedosto = lataa_tilasto()

    if not ladattu_tiedosto:
        print("Tulostiedostoa ei ole olemassa tai se on tyhjä. Tilastoja ei voitu tulostaa.\n")

    for peli in ladattu_tiedosto.values():
        print(f"Pelin ajankohta: {peli['aloitusaika']}")
        print(f"Kesto minuuteissa: {peli['kesto']}")
        print(f"Kesto vuoroissa: {peli['vuorot']}")
        print(f"Lopputulos: {peli['lopputulos']}")
        print(f"Kentän koko (pituus x leveys): {peli['kentan_pituus']} x {peli['kentan_leveys']}")
        print(f"Miinojen määrä: {peli['miinat']}")
        print()


print("\nTervetuloa pelaamaan Miinaharavaa! Valitse seuraavista vaihtoehdoista:")
print("(U)usi peli")
print("(T)ilastojen katsominen")
print("(L)opeta\n")
while True:
    valinta = input("Kirjoita valintasi: ").strip().lower()
    if valinta in ["u", "uusi peli"]:
        uusi_peli()
    elif valinta in ["t", "tilastojen katsominen"]:
        katso_tilastoja()
    elif valinta in ["l", "lopeta"]:
        break
    else:
        print("Valitsemaasi toimintoa ei ole olemassa.")
