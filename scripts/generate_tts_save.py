"""
Genera el save file de Tabletop Simulator para El Santuario y los Rayzes.
Uso: py scripts/generate_tts_save.py
Salida: El Santuario y los Rayzes.json
Copialo a: Documentos\My Games\Tabletop Simulator\Saves\
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

def make_hex(nickname, url, back, x, z):
    return {
        "Name":"Custom_Tile","Nickname":nickname,"GUID":guid(),
        "Transform":tr(x,1,z,ry=180,sx=1.8,sz=1.8),
        "CustomImage":{"ImageURL":url,"ImageSecondaryURL":back,
                       "CustomTile":{"Type":1,"Thickness":0.1,"Stackable":False,"Stretch":True}}
    }

def make_vida_token(face_url, back_url):
    return {
        "Name":"Custom_Tile","Nickname":"Vida","GUID":guid(),
        "Transform":tr(ry=180),
        "CustomImage":{"ImageURL":face_url,"ImageSecondaryURL":back_url,
                       "CustomTile":{"Type":2,"Thickness":0.1,"Stackable":True,"Stretch":True}}
    }

def make_bag(nickname, content, x, z):
    return {
        "Name":"Infinite_Bag","Nickname":nickname,"GUID":guid(),
        "Transform":tr(x,1,z),
        "ContainedObjects":[content]
    }

objects = []

# ── MAZOS ──────────────────────────────────────────────────────────────────
S = f"{BASE}/imgs/sheets"
M = f"{BASE}/imgs/mazos"
for did, name, face, back, nw, nh, nc, x in [
    (1, "Iniciales", f"{S}/iniciales.png",     f"{M}/iniciales/back/back_neutro.png",           3, 2,  5, -12.5),
    (2, "Bosque",    f"{S}/bosque.png",         f"{M}/bosque/back/back_bosque.png",              3, 4, 10,  -7.5),
    (3, "Claro",     f"{S}/claro.png",          f"{M}/claro/back/back_claro.png",                3, 3,  8,  -2.5),
    (4, "Montaña",   f"{S}/monta%C3%B1a.png",   f"{M}/monta%C3%B1a/back/back_monta%C3%B1a.png", 3, 3,  8,   2.5),
    (5, "Río",       f"{S}/rio.png",            f"{M}/rio/back/back_rio.png",                   3, 2,  6,   7.5),
    (6, "Ruinas",    f"{S}/ruinas.png",         f"{M}/ruinas/back/back_ruinas.png",             3, 3,  9,  12.5),
]:
    objects.append(make_deck(name, did, face, back, nw, nh, nc, x, z=-7))

# ── HEXÁGONOS DE TERRENO ───────────────────────────────────────────────────
H = f"{BASE}/imgs/hexs"
for i, (name, file) in enumerate([
    ("Hex Bosque",     "Hex%20Bosque.png"),
    ("Hex Campamento", "Hex%20Campamento.png"),
    ("Hex Claro",      "Hex%20Claro.png"),
    ("Hex Montaña",    "Hex%20Monta%C3%B1a.png"),
    ("Hex Negro",      "Hex%20Negro.png"),
    ("Hex Río",        "Hex%20Rio.png"),
    ("Hex Ruinas",     "Hex%20Ruinas.png"),
    ("Hex Santuario",  "Hex%20Santuario.png"),
]):
    objects.append(make_hex(name, f"{H}/{file}", BACK_HEX, x=-12.25+i*3.5, z=0))

# ── SOMBRAS — bolsas infinitas de tiles hex ────────────────────────────────
SO = f"{BASE}/imgs/sombras"
for i in range(1, 4):
    tile = make_hex(f"Sombra {i}", f"{SO}/Sombra%20{i}.png", BACK_HEX, 0, 0)
    objects.append(make_bag(f"Sombra {i}", tile, x=-6+(i-1)*6, z=7))

# ── VIDAS (una bolsa infinita, frente=Vida, reverso=Vida perdida) ──────────
TK = f"{BASE}/imgs/tokens"
tok = make_vida_token(f"{TK}/Vida.png", f"{TK}/Vida%20perdida.png")
objects.append(make_bag("Vida", tok, x=12, z=7))

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
print(f"Copialo a: Documentos\\My Games\\Tabletop Simulator\\Saves\\")
