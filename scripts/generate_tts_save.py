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
BOARD_IMG = f"{BASE}/imgs/board/plataforma.png"

# ── Plataforma de "supply" ──────────────────────────────────────────────────
# Mazos, hexágonos de repuesto y bolsas se corren hacia afuera de la mesa y
# quedan apoyados sobre esta plataforma (en vez de sobre el paño), para dejar
# el paño completamente libre para el mapa generado.
# Son valores de ajuste manual — no hay forma de medir la mesa real desde acá,
# así que hay que probarlos en TTS e ir afinando:
#   - PLATFORM_Z_SHIFT: cuánto se corre el supply en Z (hacia afuera de la mesa)
#   - PLATFORM_Y:       altura de la plataforma; tiene que quedar apoyada sobre
#                       la madera del borde de la mesa, no a la altura del paño
#   - PLATFORM_Y_LIFT:  cuánto se levanta el supply por encima de la plataforma
#                       para apoyar sobre ella sin atravesarla
#   - PLATFORM_SCALE_X / PLATFORM_SCALE_Z: escala del Custom_Tile en cada eje
#                       (independientes porque el tile usa Stretch=True, así
#                       que no hace falta mantener el aspect ratio de la imagen)
PLATFORM_Z_SHIFT   = 17.0
PLATFORM_Y         = 3.5
PLATFORM_Y_LIFT    = 0.6
PLATFORM_SCALE_X   = 16.0
PLATFORM_SCALE_Z   = 8.0
PLATFORM_CENTER_X  = 0.0
PLATFORM_CENTER_Z  = 9.0 + PLATFORM_Z_SHIFT   # promedio de las filas de supply (5, 9, 13) + shift
SUPPLY_Y = PLATFORM_Y + PLATFORM_Y_LIFT

# ── Asientos (Hands) ─────────────────────────────────────────────────────────
# Juego para 4 jugadores máximo. Se dejan solo estos 4 colores habilitados
# (DisableUnused=True apaga el resto) y los 4 se ubican del mismo lado de la
# mesa ("abajo"), lado opuesto a la plataforma de supply.
# HAND_Z es de ajuste manual, igual que las constantes de la plataforma.
HAND_COLORS = ["Red", "Brown", "White", "Orange"]
HAND_XS     = [-12.0, -4.0, 4.0, 12.0]
HAND_Z      = -20.0

_n = [0]
def guid():
    _n[0] += 1
    return f"{_n[0]:06x}"

def tr(x=0, y=1, z=0, rx=0, ry=0, rz=0, sx=1, sy=1, sz=1):
    return {"posX":x,"posY":y,"posZ":z,"rotX":rx,"rotY":ry,"rotZ":rz,
            "scaleX":sx,"scaleY":sy,"scaleZ":sz}

def make_board():
    """Custom_Tile rectangular (Type 0). Plataforma fija donde se apoya el supply."""
    return {
        "Name": "Custom_Tile",
        "Nickname": "Plataforma",
        "GUID": guid(),
        "Transform": tr(PLATFORM_CENTER_X, PLATFORM_Y, PLATFORM_CENTER_Z, sx=PLATFORM_SCALE_X, sz=PLATFORM_SCALE_Z),
        "Locked": True,
        "CustomImage": {
            "ImageURL": BOARD_IMG,
            "ImageSecondaryURL": BOARD_IMG,
            "ImageScalar": 1.0,
            "WidthScale": 0.0,
            "CustomTile": {"Type": 0, "Thickness": 0.15, "Stackable": False, "Stretch": True}
        }
    }

def make_deck(nickname, deck_id, face, back, nw, nh, nc, x, z):
    ids   = [deck_id * 100 + i for i in range(nc)]
    cards = [{"Name":"Card","Nickname":"","CardID":cid,
               "GUID":guid(),"Transform":tr(ry=180,rz=180)} for cid in ids]
    return {
        "Name":"DeckCustom","Nickname":nickname,"GUID":guid(),
        "Transform":tr(x,SUPPLY_Y,z,ry=180,rz=180),
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
        "Transform": tr(x, SUPPLY_Y, z, ry=180),
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
        "Transform": tr(x, SUPPLY_Y, z, ry=180, sx=scale, sz=scale),
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

PAWN_COLORS = [
    # nombre, ColorDiffuse RGB, MaterialIndex (0=White,1=Red,2=Orange,3=Yellow,4=Green,5=Blue,6=Purple,7=Pink,8=Black)
    ("Bordo",        (0.45, 0.08, 0.12), 1),
    ("Verde oscuro", (0.05, 0.25, 0.15), 4),
    ("Azul marino",  (0.05, 0.10, 0.35), 5),
    ("Gris oscuro",  (0.18, 0.18, 0.18), 8),
]

def make_pawn(nickname, rgb, material_index):
    """PlayerPawn (Figurine). El color real lo define MaterialIndex; ColorDiffuse lo afina/oscurece."""
    return {
        "Name": "PlayerPawn",
        "Nickname": nickname,
        "GUID": guid(),
        "Transform": tr(ry=180),
        "ColorDiffuse": {"r": rgb[0], "g": rgb[1], "b": rgb[2]},
        "MaterialIndex": material_index
    }

def make_generar_bag(x, z):
    lua = (
        'function onLoad()\n'
        '  self.createButton({\n'
        '    click_function="doGenerar",\n'
        '    function_owner=self,\n'
        '    label="Generar Mapa",\n'
        '    position={0,1.2,2.5},\n'
        '    rotation={0,0,0},\n'
        '    width=1300, height=320, font_size=130,\n'
        '    color={1,1,1},\n'
        '    font_color={0.15,0.08,0.03},\n'
        '    tooltip="Genera un nuevo mapa aleatorio"\n'
        '  })\n'
        'end\n'
        'function doGenerar(obj,color)\n'
        '  Global.call("onGenerateMap")\n'
        'end\n'
    )
    return {
        "Name": "Bag",
        "Nickname": "Mapa",
        "GUID": guid(),
        "Transform": tr(x, SUPPLY_Y, z, ry=180, sx=0.7, sy=0.7, sz=0.7),
        "ColorDiffuse": {"r": 0.2, "g": 0.45, "b": 0.15},
        "LuaScript": lua,
        "ContainedObjects": [make_pawn(name, rgb, mi) for name, rgb, mi in PAWN_COLORS]
    }

def make_bag(nickname, content, x, z):
    return {
        "Name": "Infinite_Bag",
        "Nickname": nickname,
        "GUID": guid(),
        "Transform": tr(x, SUPPLY_Y, z, sx=0.7, sy=0.7, sz=0.7),
        "ColorDiffuse": {"r": 0.6, "g": 0.35, "b": 0.1},
        "ContainedObjects": [content]
    }

objects = []

# ── PLATAFORMA — apoya sobre el borde de la mesa, contiene todo el supply ──
objects.append(make_board())

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
    objects.append(make_deck(name, did, face, back, nw, nh, nc, x, z=5 + PLATFORM_Z_SHIFT))

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
    objects.append(make_hex_terrain(name, f"{H}/{file}", BACK_HEX, deck_id=10+i, x=-12.25+i*3.5, z=9 + PLATFORM_Z_SHIFT))

# ── SOMBRAS — bolsas infinitas ─────────────────────────────────────────────
SO = f"{BASE}/imgs/sombras"
for i, sx in enumerate([-0.5, 3.0, 6.5], start=1):
    tile = make_hex(f"Sombra {i}", f"{SO}/Sombra%20{i}.png", BACK_HEX, scale=0.7)
    objects.append(make_bag(f"Sombra {i}", tile, x=sx, z=13 + PLATFORM_Z_SHIFT))

# ── VIDA — bolsa infinita, frente=Vida, reverso=Vida perdida ──────────────
TK = f"{BASE}/imgs/tokens"
objects.append(make_bag("Vida", make_vida(f"{TK}/Vida.png", f"{TK}/Vida%20perdida.png"), x=-6.5, z=13 + PLATFORM_Z_SHIFT))

# ── BOLSA GENERAR MAPA ─────────────────────────────────────────────────────
objects.append(make_generar_bag(x=10.0, z=13 + PLATFORM_Z_SHIFT))

# ── LUA SCRIPT — Generador de Mapa ────────────────────────────────────────
LUA_SCRIPT = (
    'local BASE="https://raw.githubusercontent.com/gonzak1/el-santuario-y-los-rayzes/main/imgs/hexs/"\n'
    'local BACK=BASE.."back/Back%20Hexagono.png"\n'
    'local URLS={\n'
    '  Campamento=BASE.."Hex%20Campamento.png",\n'
    '  Bosque=BASE.."Hex%20Bosque.png",\n'
    '  Claro=BASE.."Hex%20Claro.png",\n'
    '  Ruinas=BASE.."Hex%20Ruinas.png",\n'
    '  Rio=BASE.."Hex%20Rio.png",\n'
    '  Santuario=BASE.."Hex%20Santuario.png",\n'
    '  Montana=BASE.."Hex%20Monta%C3%B1a.png",\n'
    '  Cierre=BASE.."Hex%20Negro.png",\n'
    '}\n'
    'local HEX_SIZE=1.55\n'
    'local MAP_X,MAP_Z=0,0\n'
    'local DIRS={{1,0},{1,-1},{0,-1},{-1,0},{-1,1},{0,1}}\n'
    'local _guids,_did={},500\n'
    '\n'
    'local function hk(q,r) return q..","..r end\n'
    'local function nbs(q,r)\n'
    '  local t={} for _,d in ipairs(DIRS) do t[#t+1]={q+d[1],r+d[2]} end return t\n'
    'end\n'
    'local function dist(q1,r1,q2,r2)\n'
    '  local dq,dr=q1-q2,r1-r2\n'
    '  return(math.abs(dq)+math.abs(dr)+math.abs(-dq-dr))/2\n'
    'end\n'
    'local function a2w(q,r)\n'
    '  return MAP_X+HEX_SIZE*1.5*q, MAP_Z+HEX_SIZE*math.sqrt(3)*(r+q/2)\n'
    'end\n'
    'local function shuf(t)\n'
    '  for i=#t,2,-1 do local j=math.random(i) t[i],t[j]=t[j],t[i] end\n'
    'end\n'
    'local function makeDeck()\n'
    '  local d={}\n'
    '  for _=1,8 do d[#d+1]="Bosque" end\n'
    '  for _=1,4 do d[#d+1]="Claro" end\n'
    '  for _=1,3 do d[#d+1]="Ruinas" end\n'
    '  for _=1,2 do d[#d+1]="Rio" end\n'
    '  d[#d+1]="Santuario" shuf(d) return d\n'
    'end\n'
    '\n'
    'local ms\n'
    'local function ms_has(q,r) return ms.t[hk(q,r)]~=nil end\n'
    'local function ms_get(q,r) return ms.t[hk(q,r)] end\n'
    'local function ms_set(q,r,tipo,blk)\n'
    '  ms.t[hk(q,r)]={q=q,r=r,tipo=tipo,blocker=blk or false}\n'
    '  if not blk and tipo~="Montana" then\n'
    '    local d=dist(0,0,q,r) if d>ms.maxD then ms.maxD=d end\n'
    '  end\n'
    'end\n'
    'local function frontier()\n'
    '  local seen,res={},{}\n'
    '  for _,t in pairs(ms.t) do\n'
    '    if not t.blocker then\n'
    '      for _,nb in ipairs(nbs(t.q,t.r)) do\n'
    '        local k=hk(nb[1],nb[2])\n'
    '        if not ms.t[k] and not seen[k] then seen[k]=true res[#res+1]={nb[1],nb[2]} end\n'
    '      end\n'
    '    end\n'
    '  end return res\n'
    'end\n'
    'local function closure(q,r)\n'
    '  local ch={{q,r}} for _,nb in ipairs(nbs(q,r)) do ch[#ch+1]=nb end\n'
    '  for _,p in ipairs(ch) do\n'
    '    local cq,cr=p[1],p[2] local t=ms_get(cq,cr)\n'
    '    if t then\n'
    '      local thr=(t.tipo=="Campamento" or t.tipo=="Santuario") and 5 or 4\n'
    '      local pl,em=0,{}\n'
    '      for _,nb in ipairs(nbs(cq,cr)) do\n'
    '        if ms_has(nb[1],nb[2]) then pl=pl+1 else em[#em+1]=nb end\n'
    '      end\n'
    '      if pl>=thr then\n'
    '        table.sort(em,function(a,b) return dist(0,0,a[1],a[2])>dist(0,0,b[1],b[2]) end)\n'
    '        for i=2,#em do\n'
    '          local nq,nr=em[i][1],em[i][2]\n'
    '          if not ms_has(nq,nr) then ms_set(nq,nr,"Montana",true) end\n'
    '        end\n'
    '      end\n'
    '    end\n'
    '  end\n'
    'end\n'
    'local function pickType(deck,q,r)\n'
    '  if #deck==0 then return nil end\n'
    '  if deck[1]=="Santuario" and dist(0,0,q,r)<4 then\n'
    '    local s=table.remove(deck,1)\n'
    '    local ins=math.max(#deck-3,0)+math.random(3)\n'
    '    table.insert(deck,math.min(ins,#deck+1),s)\n'
    '  end\n'
    '  return table.remove(deck,1)\n'
    'end\n'
    'local function finalSeal()\n'
    '  local seen,brd={},{}\n'
    '  for _,t in pairs(ms.t) do\n'
    '    for _,nb in ipairs(nbs(t.q,t.r)) do\n'
    '      local k=hk(nb[1],nb[2])\n'
    '      if not ms.t[k] and not seen[k] then seen[k]=true brd[#brd+1]={nb[1],nb[2]} end\n'
    '    end\n'
    '  end\n'
    '  for _,p in ipairs(brd) do ms_set(p[1],p[2],"Cierre",true) end\n'
    'end\n'
    'local function generate()\n'
    '  ms={t={},maxD=0} local deck=makeDeck()\n'
    '  ms_set(0,0,"Campamento",false)\n'
    '  while #deck>0 do\n'
    '    local f=frontier() if #f==0 then break end\n'
    '    local maxD=0\n'
    '    for _,p in ipairs(f) do local d=dist(0,0,p[1],p[2]) if d>maxD then maxD=d end end\n'
    '    local c={}\n'
    '    for _,p in ipairs(f) do if dist(0,0,p[1],p[2])>=maxD-2 then c[#c+1]=p end end\n'
    '    local p=c[math.random(#c)]\n'
    '    local tipo=pickType(deck,p[1],p[2]) if not tipo then break end\n'
    '    ms_set(p[1],p[2],tipo,false) closure(p[1],p[2])\n'
    '  end\n'
    '  finalSeal()\n'
    'end\n'
    'local function clearMap()\n'
    '  for _,g in ipairs(_guids) do local o=getObjectFromGUID(g) if o then o.destruct() end end\n'
    '  _guids={}\n'
    'end\n'
    'local function spawnTile(tipo,q,r)\n'
    '  local url=URLS[tipo] if not url then return end\n'
    '  local wx,wz=a2w(q,r) _did=_did+1 local did=_did\n'
    '  local rz=(tipo=="Campamento" or tipo=="Cierre") and 0 or 180\n'
    '  local d={Name="CardCustom",Nickname=tipo,\n'
    '    Transform={posX=wx,posY=1.5,posZ=wz,rotX=0,rotY=180,rotZ=rz,scaleX=1,scaleY=1,scaleZ=1},\n'
    '    CardID=did*100,SidewaysCard=false,\n'
    '    CustomDeck={[tostring(did)]={FaceURL=url,BackURL=BACK,\n'
    '      NumWidth=1,NumHeight=1,BackIsHidden=true,UniqueBack=false,Type=3}}}\n'
    '  spawnObjectJSON({json=JSON.encode(d),callback_function=function(o)\n'
    '    o.setDescription("mapa") _guids[#_guids+1]=o.getGUID()\n'
    '  end})\n'
    'end\n'
    'function onGenerateMap()\n'
    '  math.randomseed(math.floor(os.time()))\n'
    '  clearMap() generate()\n'
    '  for _,t in pairs(ms.t) do spawnTile(t.tipo,t.q,t.r) end\n'
    'end\n'
)

# ── GUARDAR ────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "El Santuario y los Rayzes.json")
save = {
    "SaveName": "El Santuario y los Rayzes",
    "GameMode": "", "Date": "", "VersionNumber": "", "GameType": "", "GameComplexity": "",
    "Tags": [], "Gravity": 0.5, "PlayArea": 1.0,
    "Table": "Table_RPG", "Sky": "Sky_Museum",
    "Note": "", "Rules": "", "XmlUI": "", "LuaScript": LUA_SCRIPT, "LuaScriptState": "",
    "Hands": {
        "Enable": True,
        "DisableUnused": True,
        "Hiding": "Default",
        "HandTransforms": [
            {"Color": color, "Transform": tr(x, 1, HAND_Z)}
            for color, x in zip(HAND_COLORS, HAND_XS)
        ]
    },
    "ObjectStates": objects
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(save, f, indent=2, ensure_ascii=False)
print(f"Generado: {out}")
print(r"Copialo a: Documentos\My Games\Tabletop Simulator\Saves")
