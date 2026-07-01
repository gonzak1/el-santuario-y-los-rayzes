/* Prototipo de generación de mapa hex con cierre 3/6
   - Mazo chico: 8 Bosque, 4 Claro, 3 Ruinas, 2 Río, 1 Santuario (18 losetas) + Campamento
   - Montañas de cierre son "tokens" (no cuentan al mazo), pero se dibujan
   - Sin servidor, todo en memoria
*/

(() => {
  const HEX_SIZE = 28; // radio del hex
  const COLORS = {
    Campamento: 'campamento',
    Bosque: 'bosque',
    Claro: 'claro',
    Ruinas: 'ruinas',
    'Río': 'rio',
    Santuario: 'santuario',
    Montaña: 'montana',
    Cierre: 'cierre',
  };

  // --- Utilidades de hex axial (q,r) con orientación pointy-top ---
  const DIRS = [
    [ 1,  0], [ 1, -1], [ 0, -1],
    [-1,  0], [-1,  1], [ 0,  1],
  ];
  const key = (q, r) => `${q},${r}`;
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const neighbors = (q, r) => DIRS.map(d => add([q, r], d));

  function axialToPixel(q, r, size = HEX_SIZE) {
    const x = size * Math.sqrt(3) * (q + r / 2);
    const y = size * 1.5 * r;
    return [x, y];
  }
  function hexPolygonPoints(cx, cy, size = HEX_SIZE) {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const angle = Math.PI / 180 * (60 * i - 30); // pointy-top
      const x = cx + size * Math.cos(angle);
      const y = cy + size * Math.sin(angle);
      pts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
    }
    return pts.join(' ');
  }
  const distance = (a, b) => {
    // axial distance
    const dq = a[0] - b[0], dr = a[1] - b[1];
    const ds = -dq - dr;
    return (Math.abs(dq) + Math.abs(dr) + Math.abs(ds)) / 2;
  };

  // --- Estructuras de datos del mapa ---
  class Tile {
    constructor(q, r, tipo, opts = {}) {
      this.q = q; this.r = r;
      this.tipo = tipo; // Campamento, Bosque, Claro, Ruinas, Río, Santuario, Montaña
      this.blocker = !!opts.blocker; // Montaña "token" de cierre
    }
  }

  class MapState {
    constructor() {
      this.tiles = new Map(); // key -> Tile
      this.deck = [];         // tipos restantes por colocar (no incluye Campamento ni Montaña-token)
      this.maxDist = 0;       // máxima distancia alcanzada por losetas jugables
    }
    has(q, r) { return this.tiles.has(key(q, r)); }
    get(q, r) { return this.tiles.get(key(q, r)); }
    set(tile) {
      this.tiles.set(key(tile.q, tile.r), tile);
      if (!tile.blocker && tile.tipo !== 'Montaña') {
        const d = distance([0,0], [tile.q, tile.r]);
        if (d > this.maxDist) this.maxDist = d;
      }
    }
    frontier() {
      // Huecos adyacentes a losetas jugables (no-blocker)
      const f = new Set();
      for (const t of this.tiles.values()) {
        if (t.blocker) continue; // los bloqueos no abren frontera
        for (const [nq, nr] of neighbors(t.q, t.r)) {
          if (!this.has(nq, nr)) f.add(key(nq, nr));
        }
      }
      return Array.from(f).map(k => k.split(',').map(Number));
    }
  }

  // --- Generación del mazo chico ---
  function makeDeck() {
    const arr = [];
    arr.push(...Array(8).fill('Bosque'));
    arr.push(...Array(4).fill('Claro'));
    arr.push(...Array(3).fill('Ruinas'));
    arr.push(...Array(2).fill('Río'));
    arr.push('Santuario');
    return shuffle(arr);
  }
  function shuffle(a) {
    const arr = a.slice();
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // --- Reglas de cierre 3/6 y elegibilidad simple ---
  function applyClosureAround(state, q, r) {
    const toCheck = [[q, r], ...neighbors(q, r)];
    for (const [cq, cr] of toCheck) {
      const t = state.get(cq, cr);
      if (!t) continue;
      const threshold = (t.tipo === 'Campamento' || t.tipo === 'Santuario') ? 5 : 4;

      // Contar vecinos ya colocados (incluye Montaña-token)
      const neigh = neighbors(cq, cr);
      let placed = 0;
      const emptySlots = [];
      for (const [nq, nr] of neigh) {
        if (state.has(nq, nr)) placed++;
        else emptySlots.push([nq, nr]);
      }
      if (placed >= threshold) {
        // Dejar 1 hueco abierto para que el mapa respire lateralmente
        const openCount = 1; // probá con 2 si querés aún más ramificación
        emptySlots.sort((a, b) => distance([0,0], b) - distance([0,0], a)); // primero los más alejados
        for (const [nq, nr] of emptySlots.slice(openCount)) {
          if (!state.has(nq, nr)) {
            state.set(new Tile(nq, nr, 'Montaña', { blocker: true }));
          }
        }
      }
    }
  }

  function nextEligibleType(state, targetPos, deck) {
    // Regla simple: Santuario solo si distancia >= 4; si no, reinsertar al final y tomar otra
    if (deck.length === 0) return null;
    const [q, r] = targetPos;
    const d = distance([0,0], [q, r]);
    if (deck[0] === 'Santuario' && d < 4) {
      // mover Santuario a ~final (a 3–5 posiciones desde el final si se puede)
      const s = deck.shift();
      const ins = Math.max(deck.length - 3, 0) + Math.floor(Math.random() * 3);
      deck.splice(ins, 0, s);
      // tomar la nueva primera
    }
    return deck.shift() || null;
  }

  // --- Algoritmo de expansión ---
  function generateMap() {
    const state = new MapState();
    state.deck = makeDeck();

    // Colocar campamento
    state.set(new Tile(0, 0, 'Campamento'));

    // Iterar mientras queden losetas de mazo y haya frontera
    while (state.deck.length > 0) {
      const frontier = state.frontier();
      if (frontier.length === 0) break;

      // Elegir un hueco de la frontera, sesgando a mayor distancia
      const maxD = Math.max(...frontier.map(p => distance([0,0], p)));
      const candidates = frontier.filter(p => distance([0,0], p) >= (maxD - 2));
      const [q, r] = candidates[Math.floor(Math.random() * candidates.length)];

      // Tomar tipo elegible
      const tipo = nextEligibleType(state, [q, r], state.deck);
      if (!tipo) break;

      // Colocar loseta jugable
      state.set(new Tile(q, r, tipo));

      // Aplicar cierre local 3/6 (threshold 4 para Campamento/Santuario)
      applyClosureAround(state, q, r);

      // (Opcional) Anti-relleno atrás suave: si frontera se va muy atrás, el cierre la irá tapando naturalmente      
    }

    finalSeal(state);

    return state;
  }

  // --- Render SVG ---
  function render(state, opts = {}) {
    const showCoords = !!opts.showCoords;
    const svg = document.getElementById('map');
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    // Obtener bounds para encuadre
    const coords = Array.from(state.tiles.values()).map(t => [t.q, t.r]);
    const pts = coords.map(([q, r]) => axialToPixel(q, r));
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const minX = Math.min(...xs) - HEX_SIZE * 1.6;
    const maxX = Math.max(...xs) + HEX_SIZE * 1.6;
    const minY = Math.min(...ys) - HEX_SIZE * 1.6;
    const maxY = Math.max(...ys) + HEX_SIZE * 1.6;
    svg.setAttribute('viewBox', `${minX} ${minY} ${maxX - minX} ${maxY - minY}`);

    // Dibujar tiles
    for (const t of state.tiles.values()) {
      const [cx, cy] = axialToPixel(t.q, t.r);
      const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      poly.setAttribute('points', hexPolygonPoints(cx, cy));
      poly.setAttribute('class', `hex ${COLORS[t.tipo] || 'bosque'}`);
      svg.appendChild(poly);

      if (showCoords) {
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', cx);
        label.setAttribute('y', cy + (t.blocker ? 0 : 0));
        label.setAttribute('class', 'hex-label');
        const short =
          t.tipo === 'Montaña' && t.blocker ? 'M' :
          t.tipo === 'Cierre' ? 'X' :                // <--- NUEVO
          t.tipo[0];
        label.textContent = `${short}  ${t.q},${-t.r}`;
        svg.appendChild(label);
      }
    }
  }

  // --- UI ---
  function regenerate() {
    const state = generateMap();
    render(state, { showCoords: document.getElementById('showCoords').checked });
  }

  function finalSeal(state) {
  // Recolecta TODOS los huecos adyacentes a cualquier loseta (incluyendo bloqueos)
  const border = new Set();
  for (const t of state.tiles.values()) {
    for (const [nq, nr] of neighbors(t.q, t.r)) {
      const k = key(nq, nr);
      if (!state.tiles.has(k)) border.add(k);
    }
  }
  // Coloca hex "Cierre" (negros) que son bloqueadores y no cuentan como loseta del mazo
  for (const k of border) {
    const [q, r] = k.split(',').map(Number);
    state.set(new Tile(q, r, 'Cierre', { blocker: true }));
  }
}


  document.getElementById('regen').addEventListener('click', regenerate);
  document.getElementById('showCoords').addEventListener('change', regenerate);

  // Primera generación
  regenerate();
})();