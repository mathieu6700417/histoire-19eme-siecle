// Dessins traversants sous les images entières (spec 17, essai 5 : « Révision après visionnage du
// pilote : dessins traversants, simples, sans personnage », 2026-10-14). Sous une image montrée en
// entier (`x.en`), un seul dessin à la plume généré par IA (`x.vig`, ou `p.vig` pour un plan), au
// format de l'écran, est posé à la hauteur de l'image au repos (réduit à la largeur de la scène si
// elle est plus étroite), sur le bas de l'image, centré sur elle : on n'en voit que les
// deux bords, dans les marges (le centre, laissé vide à la génération, est caché par l'image). Les
// deux bords se tracent ensemble, une plume par bord, contours d'abord, à vitesse constante, en
// VIGNETTE_DUREE s : le tracé découvre l'encre du dessin généré (`src`) à travers un masque où l'on
// peint ses tracés ordonnés (`tr`, vignettes_trace.py) ; aucun trait n'est redessiné. Seuls les
// tracés des marges réellement visibles (mesurées sur toute la fenêtre de l'image, rapprochement
// compris) sont gardés et minutés. Une simple éclaircie du fond prolongé sous chaque bord ; sur un
// fond sombre (`v.cl`, annotations du 2026-10-14), le trait est clair et sans éclaircie.
// Le dessin est dans le calque, entre le fond prolongé et l'image (pour un plan : dans son fond noir,
// après son fond prolongé) : il suit le fondu croisé, et un plan qui couvre l'image le couvre aussi.
// Départ : au passage `quand` (`v.t`), jamais avant que l'image soit installée (VIGNETTE_ATTENTE,
// VIGNETTE_ATTENTE_PLAN, fin de l'entrée en scène). Tout dérive de l'instant de la voix (aucune
// transition CSS) : figé en pause, repeint depuis le début après un saut en arrière, même image
// pour les captures à horloge factice. Il s'efface le temps d'un chiffre clé, d'une date républicaine
// ou d'une surimpression de coin (verifier.py refuse ces dernières pendant le dessin). Scène étroite
// (téléphone) : rien. Préférence « réduire les animations » : le dessin paraît entier, sans tracé.
// Le cartouche le signale (« dessin généré par IA », classe `en-vignette`).
// README : « Dessins traversants (spec 17, essai 5) ».
import { FONDU_PLAN, FONDU_REDUIT, VIGNETTE_APRES_ENTREE, VIGNETTE_ATTENTE, VIGNETTE_ATTENTE_PLAN, VIGNETTE_DUREE, VIGNETTE_ECLAIRCIE, VIGNETTE_ECLAIRCIE_L, VIGNETTE_ENCRE, VIGNETTE_ENCRE_CLAIRE,
  VIGNETTE_FIN, VIGNETTE_FONDU_CENTRE, VIGNETTE_MARGE_MIN, VIGNETTE_SCENE_MIN, VIGNETTE_SEUIL } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Vignette } from './types';
import type { Lecteur } from './contexte';

/** Un tracé du fichier : épaisseur (px des tracés), contour ou non, rang, points (x, y), étendue en x, longueur. */
interface Trait { w: number; c: number; i: number; p: Float32Array; x0: number; x1: number; L: number }
interface Traces { l: number; h: number; traits: Trait[] }
/** Tracé gardé pour une place donnée : son minutage (s depuis le départ). */
interface Minute { tr: Trait; a: number; b: number }
/** Dessin d'une image de la diapositive : `xv` vue dérivée pour la caméra, fenêtre [a, b) de l'image
 *  (s de la voix ; b = Infinity pour la dernière), `k` : -1 pour l'image de la diapositive, sinon le
 *  rang du plan. */
interface Entree { v: Vignette; xv: Diapo; a: number; b: number; k: number }
/** État d'un dessin posé : vignette, masque, progression peinte, place et tracés minutés. */
interface Etat { cle: string; masque: HTMLCanvasElement; s: number; fait: Uint8Array; fini: boolean; place: string; ok: boolean; S: Minute[] }

export function installerVignette(lec: Lecteur) {
  const { scene } = lec;
  Object.assign(lec, { creerVignette, majVignette, marquerVignette, prechargerVignette, preparerVignette });
  const traces = new Map<string, Traces | 'attente' | 'echec'>();
  const encres = new Map<string, HTMLImageElement>();
  const etats = new WeakMap<HTMLElement, Etat>();
  const parDiapo = new WeakMap<Diapo, Entree[]>();

  /** Élément d'un dessin : deux éclaircies (une par bord) et le canevas. */
  function creerVignette(k = -1) {
    const b = document.createElement('div');
    b.className = 'lecteur__vignette';
    b.hidden = true;
    b.dataset.k = String(k);
    b.setAttribute('aria-hidden', 'true');
    b.innerHTML = '<i class="lecteur__eclaircie"></i><i class="lecteur__eclaircie"></i><canvas></canvas>';
    return b;
  }
  /** Élément du dessin de l'entrée `e` dans le calque `c` (celui d'un plan est dans son fond noir). */
  const boite = (c: HTMLElement, e: Entree) => (e.k < 0 ? c.querySelector<HTMLElement>(':scope > .lecteur__vignette')
    : c.querySelector<HTMLElement>(`.lecteur__plans .lecteur__vignette[data-k="${e.k}"]`));

  /** Tracés compacts → points absolus (chaque tracé : épaisseur × 10, début et fin d'origine (non
   *  lus : le lecteur minute lui-même), contour, x0, y0, puis les écarts au point précédent). */
  function decoder(j: { l: number; h: number; t: number[][] }): Traces {
    const traits = j.t.map((s, i) => {
      const n = (s.length - 4) / 2, p = new Float32Array(n * 2);
      let L = 0, x0 = s[4], x1 = s[4];
      p[0] = s[4]; p[1] = s[5];
      for (let q = 1; q < n; q++) {
        p[2 * q] = p[2 * q - 2] + s[4 + 2 * q]; p[2 * q + 1] = p[2 * q - 1] + s[5 + 2 * q];
        L += Math.hypot(p[2 * q] - p[2 * q - 2], p[2 * q + 1] - p[2 * q - 1]);
        x0 = Math.min(x0, p[2 * q]); x1 = Math.max(x1, p[2 * q]);
      }
      return { w: s[0] / 10, c: s[3], i, p, x0, x1, L };
    });
    return { l: j.l, h: j.h, traits };
  }
  /** Fichiers arrivés pendant la pause : l'image figée doit les montrer sans attendre la reprise. */
  const arrive = () => { if (lec.lance && !lec.joue) lec.rendre(); };
  function charger(v: Vignette) {
    if (!encres.has(v.src)) {
      const im = new Image();
      im.decoding = 'async';
      im.onload = arrive;
      im.src = v.src;
      encres.set(v.src, im);
    }
    if (!traces.has(v.tr)) {
      traces.set(v.tr, 'attente');
      fetch(v.tr).then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
        .then((j) => { traces.set(v.tr, decoder(j)); arrive(); })
        // Sans tracés, le dessin paraît entier à son départ (comme en mouvement réduit).
        .catch(() => { traces.set(v.tr, 'echec'); arrive(); });
    }
  }

  /** Dessins de la diapositive : celui de son image (image entière seulement), puis ceux des plans. */
  function entrees(x: Diapo): Entree[] {
    let E = parDiapo.get(x);
    if (E) return E;
    E = [];
    const P = x.plans ?? [], fin = x.duree || 6;
    if (x.vig && x.en) E.push({ v: x.vig, xv: lec.principal(x), a: 0, b: P[0]?.t ?? Infinity, k: -1 });
    P.forEach((p, k) => {
      if (!p.vig || !p.en) return;
      const b = P[k + 1]?.t ?? Infinity;
      E!.push({ v: p.vig, xv: lec.planDe(x, p, isFinite(b) ? b + FONDU_PLAN : fin), a: p.t, b, k });
    });
    parDiapo.set(x, E);
    return E;
  }
  /** Instant (s de la voix) où le trait commence. */
  function debut(e: Entree) {
    const arrivee = lec.plan(e.xv)[0]?.a ?? 0;
    const d = Math.max(e.k >= 0 ? e.a + VIGNETTE_ATTENTE_PLAN : VIGNETTE_ATTENTE, arrivee + VIGNETTE_APRES_ENTREE);
    return e.v.t != null ? Math.max(d, e.v.t) : d;
  }
  /** Chiffre clé, date républicaine, surimpressions de coin (médaillon, portraits, objet, manuscrit) :
   *  le dessin s'efface le temps de leur passage, puis revient. Rend le facteur d'opacité à `t`. */
  function effacement(x: Diapo, t: number) {
    const f = mouvementReduit.matches ? FONDU_REDUIT : VIGNETTE_FONDU_CENTRE;
    let k = 1;
    for (const w of [x.chiffre, x.dateRep, x.lieu, x.portraits, x.objet, x.manuscrit]) {
      if (!w) continue;
      k = Math.min(k, 1 - adoucir((t - (w.a - f)) / f) * (1 - adoucir((t - w.b) / f)));
    }
    return k;
  }

  function etat(b: HTMLElement) {
    let et = etats.get(b);
    if (!et) {
      et = { cle: '', masque: document.createElement('canvas'), s: -1, fait: new Uint8Array(0), fini: false, place: '', ok: false, S: [] };
      etats.set(b, et);
    }
    return et;
  }
  const cacher = (b: HTMLElement) => { if (!b.hidden) b.hidden = true; };

  /** Pose le dessin `e` (départ `d`) : à la hauteur de l'image au repos, centré sur elle ; bords de
   *  l'image mesurés sur toute sa fenêtre (mêmes calculs que la caméra) ; éclaircie sous chaque bord ;
   *  tracés des marges visibles gardés et minutés, une plume par bord. Rend faux si la place manque. */
  function placer(b: HTMLElement, e: Entree, d: number, T: Traces | 'echec') {
    const et = etat(b), W = scene.clientWidth, H = scene.clientHeight;
    const cle = `${W}x${H}|${e.v.src}|${d}|${T === 'echec' ? 0 : T.traits.length}`;
    if (et.place === cle) return et.ok;
    et.place = cle;
    et.ok = false;
    et.s = -1;
    if (W < VIGNETTE_SCENE_MIN || !H) return false;
    const xv = e.xv, u = xv.u;
    const s0 = Math.max(W / xv.l, H / xv.h), IW = (xv.l * s0) / (u[2] - u[0]), IH = (xv.h * s0) / (u[3] - u[1]);
    const bords = (t: number) => {
      const p = lec.parametres(W, H, IW, IH, u, lec.cadreA(xv, t), 1, true);
      return { x: p.tx + p.s * IW * u[0], y: p.ty + p.s * IH * u[1], w: p.s * IW * (u[2] - u[0]), h: p.s * IH * (u[3] - u[1]) };
    };
    // Au repos (fin de l'arrivée : l'image entière, avant le rapprochement) : hauteur et centre du dessin.
    const r = bords(lec.plan(xv)[0]?.a ?? 0);
    const fin = isFinite(e.b) ? e.b + FONDU_PLAN : Math.max(d, xv.duree || 6);
    let g = W, dr = 0;
    for (let k = 0; k <= 6; k++) {
      const q = bords(d + ((fin - d) * k) / 6);
      g = Math.min(g, q.x); dr = Math.max(dr, q.x + q.w);
    }
    if (Math.max(g, W - dr) < VIGNETTE_MARGE_MIN * r.h) return false;
    // Le dessin a la hauteur de l'image au repos ; sur une scène plus étroite que lui, il est réduit à
    // la largeur de la scène (ses deux bords restent visibles), posé sur le bas de l'image.
    const wd = Math.min((r.h * e.v.l) / e.v.h, W), hd = (wd * e.v.h) / e.v.l, left = r.x + r.w / 2 - wd / 2, top = r.y + r.h - hd;
    const can = b.querySelector('canvas')!, ecl = b.querySelectorAll<HTMLElement>('.lecteur__eclaircie');
    Object.assign(can.style, { left: `${left.toFixed(1)}px`, top: `${top.toFixed(1)}px`, width: `${wd.toFixed(1)}px`, height: `${hd.toFixed(1)}px` });
    // Éclaircie de chaque bord : accolée à l'image (les objets sont dessinés près d'elle), large de la
    // marge au plus et de VIGNETTE_ECLAIRCIE_L hauteurs d'image (scène très large : pas de projecteur),
    // centrée un peu sous le milieu (le dessin pose sur une ligne de sol).
    [[g, g, -1], [dr, W - dr, 1]].forEach(([bord, m, sens], j) => {
      const el = ecl[j], l = Math.min(1.15 * m, VIGNETTE_ECLAIRCIE_L * hd);
      el.hidden = m < 4 || Boolean(e.v.cl);
      const x0 = sens < 0 ? bord + 0.1 * l - l : bord - 0.1 * l;
      Object.assign(el.style, { left: `${x0.toFixed(1)}px`, width: `${l.toFixed(1)}px`, top: `${(top + 0.14 * hd).toFixed(1)}px`, height: `${(0.84 * hd).toFixed(1)}px` });
    });
    // Tracés des marges visibles (en px des tracés), une plume par bord, contours d'abord.
    et.S = [];
    if (T !== 'echec') {
      const k = T.l / wd, gT = (g - left) * k, dT = (dr - left) * k, visG = -left * k, visD = (W - left) * k;
      const ordre = (a: Trait, c: Trait) => (c.c - a.c) || (a.i - c.i);
      const garde = T.traits.filter((s) => (s.x0 < gT && s.x1 > visG) || (s.x1 > dT && s.x0 < visD));
      for (const G of [garde.filter((s) => s.x0 < gT).sort(ordre), garde.filter((s) => s.x0 >= gT).sort(ordre)]) {
        const total = G.reduce((t, s) => t + Math.max(s.L, 1), 0) || 1;
        let acc = 0;
        for (const s of G) { const a = (acc / total) * VIGNETTE_DUREE; acc += Math.max(s.L, 1); et.S.push({ tr: s, a, b: (acc / total) * VIGNETTE_DUREE }); }
      }
    }
    et.fait = new Uint8Array(et.S.length);
    et.ok = true;
    return true;
  }

  /** Peint le dessin à `s` s de son départ : tracés commencés peints dans le masque (à l'échelle des
   *  tracés), encre découverte par le masque, puis teinte d'encre. En fin de tracé (VIGNETTE_FIN),
   *  le dessin entier rattrape les rares points que le masque a manqués. */
  function dessiner(b: HTMLElement, v: Vignette, T: Traces | 'echec', ink: HTMLImageElement, s: number) {
    const et = etat(b), can = b.querySelector('canvas')!, M = et.masque;
    if (et.cle !== v.src || can.width !== ink.naturalWidth || can.height !== ink.naturalHeight) {
      can.width = M.width = ink.naturalWidth;
      can.height = M.height = ink.naturalHeight;
      et.cle = v.src; et.s = -1; et.fini = false;
    }
    const x = can.getContext('2d')!;
    if (T === 'echec' || s >= VIGNETTE_DUREE + VIGNETTE_FIN) {
      if (!et.fini) {
        x.globalCompositeOperation = 'source-over';
        x.clearRect(0, 0, can.width, can.height);
        x.drawImage(ink, 0, 0);
        x.globalCompositeOperation = 'source-in';
        x.fillStyle = v.cl ? VIGNETTE_ENCRE_CLAIRE : VIGNETTE_ENCRE;
        x.fillRect(0, 0, can.width, can.height);
        x.globalCompositeOperation = 'source-over';
        et.fini = true;
      }
      et.s = s;
      return;
    }
    const mx = M.getContext('2d')!;
    if (s < et.s - 1e-3 || et.fini || et.s < 0) {
      // Saut en arrière, retour depuis le dessin entier ou nouvelle place : le masque repart de zéro.
      mx.setTransform(1, 0, 0, 1, 0, 0);
      mx.clearRect(0, 0, M.width, M.height);
      et.fait.fill(0);
      et.fini = false;
    }
    const k = M.width / T.l;
    mx.setTransform(k, 0, 0, k, 0, 0);
    mx.strokeStyle = '#fff';
    mx.lineCap = mx.lineJoin = 'round';
    et.S.forEach((m, i) => {
      if (et.fait[i] || s < m.a) return;
      const tr = m.tr, f = Math.min(1, (s - m.a) / Math.max(1e-3, m.b - m.a)), p = tr.p;
      let reste = f * tr.L;
      mx.lineWidth = tr.w;
      mx.beginPath();
      mx.moveTo(p[0], p[1]);
      for (let j = 2; j < p.length && reste > 0; j += 2) {
        const ax = p[j - 2], ay = p[j - 1], bx = p[j], by = p[j + 1], l = Math.hypot(bx - ax, by - ay);
        if (l <= reste) { mx.lineTo(bx, by); reste -= l; } else { const q = reste / l; mx.lineTo(ax + (bx - ax) * q, ay + (by - ay) * q); reste = 0; }
      }
      if (tr.L < 0.5) mx.lineTo(p[0] + 0.1, p[1]);
      mx.stroke();
      if (f >= 1) et.fait[i] = 1;
    });
    x.globalCompositeOperation = 'source-over';
    x.clearRect(0, 0, can.width, can.height);
    x.drawImage(ink, 0, 0);
    x.globalCompositeOperation = 'destination-in';
    x.drawImage(M, 0, 0);
    if (s > VIGNETTE_DUREE) {
      x.globalCompositeOperation = 'destination-over';
      x.globalAlpha = Math.min(1, (s - VIGNETTE_DUREE) / VIGNETTE_FIN);
      x.drawImage(ink, 0, 0);
      x.globalAlpha = 1;
    }
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = v.cl ? VIGNETTE_ENCRE_CLAIRE : VIGNETTE_ENCRE;
    x.fillRect(0, 0, can.width, can.height);
    x.globalCompositeOperation = 'source-over';
    et.s = s;
  }

  /** Vide le dessin du calque (nouvelle diapositive) et charge ceux de `x`. */
  function preparerVignette(c: HTMLElement, x: Diapo) {
    const b = c.querySelector<HTMLElement>(':scope > .lecteur__vignette');
    if (b) { cacher(b); etat(b).place = ''; }
    for (const e of entrees(x)) charger(e.v);
  }

  /** À chaque rendu du calque visible, à l'instant `t` de la voix : chaque dessin de la diapositive
   *  dont le tracé a commencé et dont l'image n'est pas couverte, peint à sa progression. Rend
   *  l'opacité du dessin montré (0 : aucun). */
  function majVignette(c: HTMLElement, x: Diapo, t: number) {
    const E = entrees(x), galerie = (lec.enSuite || lec.suiteFini) && lec.galerieDe(x);
    const o = effacement(x, t), f = mouvementReduit.matches ? FONDU_REDUIT : FONDU_PLAN;
    let montre = 0;
    for (const e of E) {
      const b = boite(c, e);
      if (!b) continue;
      const d = debut(e);
      // Avant son départ, sous le plan suivant (une fois le fondu fini), pendant une galerie : rien.
      if (t < d || t >= e.b + f || galerie || scene.clientWidth < VIGNETTE_SCENE_MIN || o <= 0.001) { cacher(b); continue; }
      charger(e.v);
      const ink = encres.get(e.v.src)!, T = traces.get(e.v.tr);
      if (!ink.complete || !ink.naturalWidth || !T || T === 'attente' || !placer(b, e, d, T)) { cacher(b); continue; }
      const s = mouvementReduit.matches ? Infinity : t - d;
      dessiner(b, e.v, T, ink, s);
      const ecl = mouvementReduit.matches ? 1 : adoucir(s / VIGNETTE_ECLAIRCIE);
      b.querySelectorAll<HTMLElement>('.lecteur__eclaircie').forEach((el) => { el.style.opacity = ecl.toFixed(3); });
      b.style.opacity = o.toFixed(3);
      if (b.hidden) b.hidden = false;
      // Mention du cartouche : le dessin de l'image montrée (celle de la diapositive, ou le plan entré).
      if (e.k < 0 ? t < e.b : t >= e.a) montre = Math.max(montre, o);
    }
    return montre;
  }

  /** Mention « dessin généré par IA » du cartouche : montrée tant que le dessin est à l'écran. */
  let marque = false;
  function marquerVignette(o: number) {
    const oui = o > VIGNETTE_SEUIL;
    if (oui !== marque) { marque = oui; lec.lecteur.classList.toggle('en-vignette', oui); }
  }

  // Encre et tracés des diapositives à venir, chargés d'avance.
  function prechargerVignette(x: Diapo) {
    for (const e of entrees(x)) charger(e.v);
  }
}
