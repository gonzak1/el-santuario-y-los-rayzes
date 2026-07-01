"""
Genera el save file de Tabletop Simulator para El Santuario y los Rayzes.
Uso: py scripts/generate_tts_save.py
Salida: El Santuario y los Rayzes.json
Copialo a: Documentos/My Games/Tabletop Simulator/Saves/
Luego en TTS: Games > Load > El Santuario y los Rayzes
"""
import json, os

BASE     = "https://raw.githubusercontent.com/gonzak1/el-santuario-y-los-rayzes/main"
BACK_HEX = f"{BASE}/imgs/hexs/back/Back%20Hexagono.png"

_n = [0]
def guid():
    _n[0] += 1
    return f"{_n[0]:06x}"

def tr(x=0, y=1, z=0, rx=0, ry=0, rz=0, sx=1, sy=1, sz=1):
    return {"posX":x,"posY":y,"posZ":z,"rotX":rx,"rotY":ry,"rotZ":rz,
            "scaleX":sx,"scaleY":sy,"scaleZ":sz}

def make_deck(nickname, deck_id, face, back, nw, nh, nc, x, z):
    ids   = [deck_id * 100 + i for i in range(nc)]
    cards = [{"Name":"Card","Nickname":"","CardID":cid,
               "GUID":guid(),"Transform":tr(ry=180,rz=180)} for cid in ids]
    return {
        "Name":"DeckCustom","Nickname":nickname,"GUID":guid(),
        "Transform":tr(x,1,z,ry=180,rz=180),
        "DeckIDs":ids,
        "CustomDeck":{str(deck_id):{
            "FaceURL":face,"BackURL":back,"NumWidth":nw,"NumHeight":nh,
            "BackIsHidden":True,"UniqueBack":False
        }},
        "ContainedObjects":cards
    }

def make_hex_terrain(nickname, face_url, back_url, deck_id, x=0, z=0):
    """CardCustom hexagonal (Type 3). Para tiles de terreno."""
    return {
        "Name": "CardCustom",
        "Nickname": nickname,
        "GUID": guid(),
        "Transform": tr(x, 1, z, ry=180),
        "CardID": deck_id * 100,
        "SidewaysCard": False,
        "CustomDeck": {
            str(deck_id): {
                "FaceURL": face_url,
                "BackURL": back_url,
                "NumWidth": 1,
                "NumHeight": 1,
                "BackIsHidden": True,
                "UniqueBack": False,
                "Type": 3
            }
        }
    }

def make_hex(nickname, url, back, x=0, z=0, scale=0.7):
    """Custom_Tile hexagonal (Type 1). Para sombras dentro de bolsas."""
    return {
        "Name": "Custom_Tile",
        "Nickname": nickname,
        "GUID": guid(),
        "Transform": tr(x, 1, z, ry=180, sx=scale, sz=scale),
        "CustomImage": {
            "ImageURL": url,
            "ImageSecondaryURL": back,
            "ImageScalar": 1.0,
            "WidthScale": 0.0,
            "CustomTile": {"Type": 1, "Thickness": 0.1, "Stackable": False, "Stretch": False}
        }
    }

def make_vida(face_url, back_url):
    """CardCustom circular (Type 4). Frente=Vida, reverso=Vida perdida."""
    deck_id = 9
    return {
        "Name": "CardCustom",
        "Nickname": "Vida",
        "GUID": guid(),
        "Transform": tr(ry=180, sx=0.4, sy=0.4, sz=0.4),
        "CardID": deck_id * 100,
        "SidewaysCard": False,
        "CustomDeck": {
            str(deck_id): {
                "FaceURL": face_url,
                "BackURL": back_url,
                "NumWidth": 1,
                "NumHeight": 1,
                "BackIsHidden": True,
                "UniqueBack": False,
                "Type": 4
            }
        }
    }

def make_bag(nickname, content, x, z):
    return {
        "Name": "Infinite_Bag",
        "Nickname": nickname,
        "GUID": guid(),
        "Transform": tr(x, 1, z, sx=0.7, sy=0.7, sz=0.7),
        "ColorDiffuse": {"r": 0.6, "g": 0.35, "b": 0.1},
        "ContainedObjects": [content]
    }

objects = []

# ── MAZOS ──────────────────────────────────────────────────────────────────
S = f"{BASE}/imgs/sheets"
M = f"{BASE}/imgs/mazos"
for did, name, face, back, nw, nh, nc, x in [
    (1, "Iniciales", f"{S}/iniciales.png",     f"{M}/iniciales/back/back_neutro.png",           3, 2,  5, -10.0),
    (2, "Bosque",    f"{S}/bosque.png",         f"{M}/bosque/back/back_bosque.png",              3, 4, 10,  -4.0),
    (3, "Claro",     f"{S}/claro.png",          f"{M}/claro/back/back_claro.png",                3, 3,  8,  -0.5),
    (4, "Montaña",   f"{S}/monta%C3%B1a.png",   f"{M}/monta%C3%B1a/back/back_monta%C3%B1a.png", 3, 3,  8,   3.0),
    (5, "Río",       f"{S}/rio.png",            f"{M}/rio/back/back_rio.png",                   3, 2,  6,   6.5),
    (6, "Ruinas",    f"{S}/ruinas.png",         f"{M}/ruinas/back/back_ruinas.png",             3, 3,  9,  10.0),
]:
    objects.append(make_deck(name, did, face, back, nw, nh, nc, x, z=5))

# ── HEXÁGONOS DE TERRENO ───────────────────────────────────────────────────
H = f"{BASE}/imgs/hexs"
for i, (name, file) in enumerate([
    ("Hex Campamento", "Hex%20Campamento.png"),
    ("Hex Santuario",  "Hex%20Santuario.png"),
    ("Hex Bosque",     "Hex%20Bosque.png"),
    ("Hex Claro",      "Hex%20Claro.png"),
    ("Hex Montaña",    "Hex%20Monta%C3%B1a.png"),
    ("Hex Río",        "Hex%20Rio.png"),
    ("Hex Ruinas",     "Hex%20Ruinas.png"),
    ("Hex Negro",      "Hex%20Negro.png"),
]):
    objects.append(make_hex_terrain(name, f"{H}/{file}", BACK_HEX, deck_id=10+i, x=-12.25+i*3.5, z=9))

# ── SOMBRAS — bolsas infinitas ─────────────────────────────────────────────
SO = f"{BASE}/imgs/sombras"
for i, sx in enumerate([-0.5, 3.0, 6.5], start=1):
    tile = make_hex(f"Sombra {i}", f"{SO}/Sombra%20{i}.png", BACK_HEX, scale=0.7)
    objects.append(make_bag(f"Sombra {i}", tile, x=sx, z=13))

# ── VIDA — bolsa infinita, frente=Vida, reverso=Vida perdida ──────────────
TK = f"{BASE}/imgs/tokens"
objects.append(make_bag("Vida", make_vida(f"{TK}/Vida.png", f"{TK}/Vida%20perdida.png"), x=-6.5, z=13))

# ── GUARDAR ────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "El Santuario y los Rayzes.json")
save = {
    "SaveName": "El Santuario y los Rayzes",
    "GameMode": "", "Date": "", "VersionNumber": "", "GameType": "", "GameComplexity": "",
    "Tags": [], "Gravity": 0.5, "PlayArea": 0.5,
    "Table": "Table_RPG", "Sky": "Sky_Museum",
    "Note": "", "Rules": "", "XmlUI": "", "LuaScript": "", "LuaScriptState": "",
    "ObjectStates": objects
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(save, f, indent=2, ensure_ascii=False)
print(f"Generado: {out}")
print(r"Copialo a: Documentos\My Games\Tabletop Simulator\Saves")
