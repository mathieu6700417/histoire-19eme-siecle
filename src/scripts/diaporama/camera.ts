// Image et caméra : taille du calque, marges couvertes par les surimpressions, vue (zone utile),
// plan des transitions, cadre à l'instant t (`cadreA`), cadre d'un intermède. Lit `lec.D`, marges.
// Spec 12, « Caméra calée sur la narration », « Caméra calme et lente », « Caméra plus vivante ».
// README : « Caméra : format et pièges », « Zone utile », « Marges des surimpressions du bas ».
import { DUREE_MIN, ECART_MIN, MICRO, MISE_EN_ROUTE, OUVERTURE, POUSSEE, RAMPE_RECUL, RECUL_OUVERTURE, RETARD, SOUFFLE, TENUE_MIN, VISE_GLISSE, VISE_ZOOM } from './constantes';
import { ampleur, echelle, profil, souffle, trajet } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Rect, SuiteChant } from './types';
import type { Lecteur } from './contexte';

export function installerCamera(lec: Lecteur) {
  const { $, D, elActe, elLegende, elMusique, elSt, lecteur, scene } = lec;
  Object.assign(lec, { cadre, cadreA, cadreIntermede, majBasSurimpressions, mesurerMarges, parametres,
    plan, transformation, vue });
  // --- Image : taille, caméra, entrée ----------------------------------------------------
  // L'image couvre toute la scène (recadrée, jamais de bandes vides) ; la caméra montre le
  // cadre visé en entier dans la zone que ne couvrent ni le cartouche ni les bandeaux.
  function cadre(c: HTMLElement, x: Diapo) {
    const W = scene.clientWidth, H = scene.clientHeight;
    // La zone utile couvre la scène (zoom au besoin) : jamais de bord ni de bande hors de l'œuvre.
    const s = Math.max(W / x.l, H / x.h);
    c.style.width = `${W}px`;
    c.style.height = `${H}px`;
    const img = c.querySelector('img')!;
    img.style.width = `${(x.l * s) / (x.u[2] - x.u[0])}px`;
    img.style.height = `${(x.h * s) / (x.u[3] - x.u[1])}px`;
    if (x.ap) {
      const imgA = c.querySelector<HTMLImageElement>('.lecteur__apres img')!, A = x.ap, sa = Math.max(W / A.l, H / A.h);
      imgA.style.width = `${(A.l * sa) / (A.u[2] - A.u[0])}px`;
      imgA.style.height = `${(A.h * sa) / (A.u[3] - A.u[1])}px`;
    }
    lec.placerTuiles(c, x);
  }

  // Hauteurs couvertes en haut (cartouche, acte en plein écran) et en bas (sous-titre,
  // progression et contrôles en plein écran) : le cadre visé est placé entre les deux.
  // Le cartouche est mesuré sans sa transformation (glissement d'entrée) : offsetTop/Height.
  let marges = { haut: 0, bas: 0 }; // zones couvertes, constantes pendant une diapositive
  let basLieu = 0; // hauteur couverte en bas par le médaillon de lieu (s'il était affiché)
  lec.basCotes = { gauche: 0, droite: 0 }; // bas couvert de chaque côté (manuscrit)
  lec.hautBrut = 0; // haut couvert (cartouche), sans la réduction qui garde 55 % à la caméra
  let basBandes = 0; // bas couvert par les bandeaux (plein écran : sous-titre, progression, contrôles)
  /** Plein écran (spec 12, « Marges des surimpressions du bas ») : contrôles masqués, le
   *  sous-titre descend à leur place et les surimpressions du bas avec lui, à la marge des
   *  cartouches du bas de l'écran ; contrôles visibles, elles se posent juste au-dessus d'eux.
   *  La caméra n'en dépend pas (marges mesurées avec tous les bandeaux). */
  function majBasSurimpressions() {
    const pe = document.fullscreenElement === lecteur;
    const prog = $('.lecteur__progression'), ctl = $('.lecteur__controles');
    const descente = pe ? prog.offsetHeight + ctl.offsetHeight : 0;
    lecteur.style.setProperty('--descente-st', `${descente}px`);
    const masques = pe && lecteur.classList.contains('inactif');
    scene.style.setProperty('--surimp-bas', `${Math.round(masques ? Math.max(0, basBandes - descente) : basBandes)}px`);
  }
  const surimpressions = [elActe, elLegende, elMusique, elSt, $('.lecteur__progression'), $('.lecteur__controles')];
  function mesurerMarges() {
    const s = scene.getBoundingClientRect();
    let haut = 0, bas = 0;
    for (const el of surimpressions) {
      let r: { top: number; bottom: number; left: number; right: number; width: number; height: number } = el.getBoundingClientRect();
      if (el === elMusique && !el.classList.contains('est-visible')) continue;
      if (el === elSt && r.height) {
        // Sans la descente du sous-titre (contrôles masqués) : la place réservée reste constante.
        const ty = new DOMMatrix(getComputedStyle(el).transform === 'none' ? undefined : getComputedStyle(el).transform).m42;
        r = { top: r.top - ty, bottom: r.bottom - ty, left: r.left, right: r.right, width: r.width, height: r.height };
      }
      if (el === elLegende || el === elMusique) {
        const top = s.top + scene.clientTop + el.offsetTop, left = s.left + scene.clientLeft + el.offsetLeft;
        r = { top, left, bottom: top + el.offsetHeight, right: left + el.offsetWidth, width: el.offsetWidth, height: el.offsetHeight };
      }
      if (!r.height || !r.width || r.bottom <= s.top || r.top >= s.bottom || r.right <= s.left || r.left >= s.right) continue;
      if ((r.top + r.bottom) / 2 < s.top + s.height / 2) haut = Math.max(haut, r.bottom - s.top + 4);
      else bas = Math.max(bas, s.bottom - r.top + 4);
    }
    // La frise en surimpression se pose au-dessus des bandeaux du bas (plein écran).
    scene.style.setProperty('--frise-bas', `${Math.round(bas)}px`);
    basBandes = bas;
    majBasSurimpressions();
    // Marge du bas des surimpressions de coin (celle des cartouches du haut) : la place réservée
    // à la caméra la compte avec tous les bandeaux, contrôles compris, même masqués (constante).
    const margeY = parseFloat(getComputedStyle(elLegende).top) || 8;
    // Médaillon de lieu : sa place est réservée pour toute la diapositive (et non le temps de son
    // affichage) : une zone couverte qui change en cours de route ferait bouger la caméra d'un
    // coup (mesures du 2026-10-08 : jusqu'à 10 fois le plafond de vitesse en 0,9 s).
    basLieu = lec.elLieu && D.diapos[lec.i].lieu ? lec.elLieu.offsetHeight + margeY + bas + 4 : 0;
    // Rangée de portraits (en bas à gauche) : même principe, place réservée pour toute la
    // diapositive, mesurée sans la frise (qui la fait monter le temps de son passage).
    const basPortraits = lec.elPortraits && D.diapos[lec.i].portraits
      ? lec.elPortraits.offsetHeight + margeY + bas + 4 : 0;
    // Objet de musée (coin bas) : même principe, place réservée pour toute la diapositive.
    const basObjet = lec.elObjet && D.diapos[lec.i].objet
      ? lec.elObjet.offsetHeight + margeY + bas + 4 : 0;
    // Bas occupé de chaque côté (le manuscrit se pose au-dessus de celui de son côté seulement).
    const objetGauche = D.diapos[lec.i].objet?.cote === 'gauche';
    lec.basCotes = { gauche: Math.max(bas, basPortraits, objetGauche ? basObjet : 0), droite: Math.max(bas, basLieu, objetGauche ? 0 : basObjet) };
    bas = Math.max(bas, basLieu, basPortraits, basObjet);
    // La zone libre garde au moins 55 % de la hauteur.
    const k = Math.min(1, (0.45 * s.height) / Math.max(1, haut + bas));
    marges = { haut: haut * k, bas: bas * k };
    lec.hautBrut = haut;
    lec.tailleManuscrit();
  }

  /** Transformation CSS qui montre `r` en entier dans la zone utile, l'image couvrant toujours
   *  la scène. Un cadre trop haut pour la zone est montré depuis son bord supérieur (têtes).
   *  `f` ≥ 1 : agrandissement supplémentaire (recul d'entrée) autour du centre de la zone
   *  utile ; il se compose avec la caméra et garde la scène couverte. */
  function transformation(c: HTMLElement, x: Diapo, r: Rect, f = 1, img = c.querySelector('img')!) {
    const W = c.clientWidth, H = c.clientHeight;
    // Taille posée par `cadre` (offsetWidth l'arrondirait au pixel : zoom faussé de quelques millièmes).
    const IW = parseFloat(img.style.width) || img.offsetWidth || W, IH = parseFloat(img.style.height) || img.offsetHeight || H;
    return css(parametres(W, H, IW, IH, x.u, r, f));
  }
  const css = (p: { tx: number; ty: number; s: number }) => `translate3d(${p.tx.toFixed(2)}px, ${p.ty.toFixed(2)}px, 0) scale(${p.s.toFixed(6)})`;
  /** Translation et échelle de `transformation` (image de `IW` × `IH` px, zone utile `u`). */
  function parametres(W: number, H: number, IW: number, IH: number, u: Rect, r: Rect, f = 1) {
    // Tout le calcul se fait dans la zone utile de l'image (`x.u`, sans bordure ni légende), qui
    // couvre la scène : `r` y est exprimé, et la translation finale tient compte de son décalage.
    const iw = IW * (u[2] - u[0]), ih = IH * (u[3] - u[1]);
    const T = marges.haut, Hs = Math.max(1, H - marges.haut - marges.bas);
    const rx = r[0] * iw, ry = r[1] * ih, rw = Math.max(1, (r[2] - r[0]) * iw), rh = Math.max(1, (r[3] - r[1]) * ih);
    const z = Math.max(1, Math.min(W / rw, Hs / rh));
    let tx = W / 2 - z * (rx + rw / 2);
    let ty = z * rh <= Hs + 0.5 ? T + Hs / 2 - z * (ry + rh / 2) : T - z * ry;
    tx = Math.min(0, Math.max(W - z * iw, tx));
    ty = Math.min(0, Math.max(H - z * ih, ty));
    // Agrandir autour d'un point de la scène garde l'image couvrante (f ≥ 1).
    const px = W / 2, py = T + Hs / 2;
    tx = px + f * (tx - px); ty = py + f * (ty - py);
    tx -= z * f * u[0] * IW; ty -= z * f * u[1] * IH;
    // Sous-pixel et échelle fine (cf. `css`) : un mouvement très lent ne doit pas avancer par crans.
    return { tx, ty, s: z * f };
  }

  /** Partie de l'image réellement montrée pour le cadre `r` (mêmes calculs que
   *  `transformation`) : le cadre porté aux proportions de la zone utile, borné à l'image (la
   *  scène entière, bandeaux compris, reste couverte). La caméra ne travaille que sur ces vues :
   *  toutes de mêmes proportions, elles s'enchaînent par homothétie, et `transformation` n'a
   *  jamais à les rogner en cours de mouvement (un rognage brusque ferait un à-coup). */
  function vue(x: Diapo, r: Rect): Rect {
    const W = scene.clientWidth, H = scene.clientHeight;
    if (!W || !H) return r;
    const s = Math.max(W / x.l, H / x.h), iw = x.l * s, ih = x.h * s;
    const Hs = Math.max(1, H - marges.haut - marges.bas);
    const rw = Math.max(1, (r[2] - r[0]) * iw), rh = Math.max(1, (r[3] - r[1]) * ih);
    const z = Math.max(1, Math.min(W / rw, Hs / rh));
    const w = Math.min(1, W / z / iw), h = Math.min(1, Hs / z / ih);
    // Bandeaux couverts au-dessus et au-dessous de la zone utile, en fraction de l'image.
    const dh = marges.haut / z / ih, db = marges.bas / z / ih;
    // Un cadre trop haut pour la zone est montré depuis son bord supérieur (têtes).
    const x0 = Math.min(Math.max((r[0] + r[2]) / 2 - w / 2, 0), 1 - w);
    const y0 = Math.max(Math.min(z * rh <= Hs + 0.5 ? (r[1] + r[3]) / 2 - h / 2 : r[1], 1 - h - db), Math.min(dh, 1 - h));
    return [x0, y0, x0 + w, y0 + h];
  }

  /** Étapes retenues au rendu (spec 12, « Caméra calme et lente ») et fenêtre de chaque
   *  transition : [de, a] (s de l'audio). Une étape est ignorée si son passage suit le précédent
   *  retenu de moins de 5 s, si sa vue diffère à peine de la précédente, ou si sa transition ne
   *  tient plus avant la fin de la voix. Les données ne changent pas. */
  function plan(x: Diapo) {
    const E = x.camera, finVoix = x.duree || 6;
    // Après un détail d'ouverture, la première vue n'est atteinte qu'à la fin du recul : aucune
    // étape ne commence avant (la tenue minimale court à partir de là).
    // Image après d'un avant / après, ou fin de la plongée d'une mosaïque : la première vue
    // (imposée par `v0`, sinon celle du premier cadre) n'est quittée qu'après `a0`.
    const etapes = [{ v: x.v0 ?? vue(x, E[0].c), c: E[0].c, t: x.t0 ?? 0, de: 0, a: x.ouv ? dureeRecul(x) : x.a0 ?? 0 }];
    for (let k = 1; k < E.length; k++) {
      const p = etapes[etapes.length - 1], v = vue(x, E[k].c);
      if (E[k].t - p.t < ECART_MIN) continue;
      const { zoom: z0, glisse: g0 } = ampleur(p.v, v);
      if (z0 < MICRO && g0 < MICRO) continue;
      // La transition part de la vue zoomée par la tenue (jusqu'à SOUFFLE) : on compte le pire
      // des deux départs pour tenir les plafonds.
      const pz = ampleur(echelle(p.v, Math.exp(-SOUFFLE)), v);
      const zoom = Math.max(z0, pz.zoom), glisse = Math.max(g0, pz.glisse);
      // Durée : celle qui tient les plafonds (au plus fort, la vitesse vaut 1 / (d − rampe)) ;
      // 3 à 6 s d'ordinaire, davantage pour un long glissement le long d'une image très large.
      const u = Math.max(zoom / VISE_ZOOM, glisse / VISE_GLISSE);
      const besoin = Math.max(DUREE_MIN, u <= 2 * MISE_EN_ROUTE ? 1.5 * u : u + MISE_EN_ROUTE);
      const tot = p.a + TENUE_MIN;
      // Arrivée visée peu après le passage ; plus tard si la transition précédente l'impose.
      const a = Math.min(finVoix, Math.max(E[k].t + RETARD, tot + besoin));
      const d = Math.min(besoin, a - tot);
      // Fin de voix trop proche : une transition un peu plus vive (×1,5 au plus) ou aucune.
      if (d < Math.max(DUREE_MIN, besoin / 1.5)) continue;
      etapes.push({ v, c: E[k].c, t: E[k].t, de: a - d, a });
    }
    return etapes;
  }

  /** Durée du recul depuis le détail d'ouverture : 5 s, davantage si l'ampleur l'exige pour
   *  rester sous les plafonds de vitesse au plus fort (vitesse de pointe 1 / (d − rampe)), moins
   *  si la voix est très courte (la moitié de la voix au plus). */
  function dureeRecul(x: Diapo) {
    let d = RECUL_OUVERTURE;
    if (x.ouv) {
      const { zoom, glisse } = ampleur(echelle(vue(x, x.ouv), 1 - POUSSEE), vue(x, x.camera[0].c));
      d = Math.max(d, Math.max(zoom / VISE_ZOOM, glisse / VISE_GLISSE) / (1 - RAMPE_RECUL));
    }
    return Math.min(d, 0.5 * (x.duree || 6));
  }

  /** Cadre (vue) montré à l'instant `t` (secondes dans l'audio) d'une diapositive. Un instant
   *  négatif (−OUVERTURE à 0) est l'ouverture du carton d'acte, avant la voix. */
  function cadreA(x: Diapo, t: number): Rect {
    const E = x.camera;
    if (mouvementReduit.matches) {
      // Premier cadre fixe, puis coupe sèche vers les suivants.
      let k = 0;
      while (k + 1 < E.length && E[k + 1].t <= t) k++;
      return E[k].c;
    }
    // La dernière tenue s'arrête (en douceur) à la fin de la voix : l'horloge s'y arrête.
    const finVoix = x.duree || 6;
    const P = plan(x);
    if (x.ouv) {
      // Détail d'ouverture : légère poussée pendant les volets (départ et arrêt doux), puis
      // recul vers la première vue, doux aux deux bouts ; la respiration prend le relais à
      // vitesse nulle (P[0].a = fin du recul) : position et vitesse continues partout.
      const O = vue(x, x.ouv), Op = echelle(O, 1 - POUSSEE);
      if (t < 0) return trajet(O, Op, profil(t + OUVERTURE, OUVERTURE, OUVERTURE / 2));
      const dr = P[0].a;
      if (t < dr) return trajet(Op, P[0].v, profil(t, dr, RAMPE_RECUL * dr));
    }
    const tenue = (k: number, u: number) => {
      const jusqua = k + 1 < P.length ? P[k + 1].de : finVoix;
      return souffle(P[k].v, u - P[k].a, jusqua - P[k].a, P[k].c);
    };
    for (let k = P.length - 1; k >= 1; k--) {
      if (t >= P[k].a) return tenue(k, t);
      if (t >= P[k].de) {
        const d = P[k].a - P[k].de;
        return trajet(tenue(k - 1, P[k].de), P[k].v, profil(t - P[k].de, d, Math.min(d / 3, MISE_EN_ROUTE)));
      }
    }
    return tenue(0, t);
  }

  /** Cadre montré pendant un intermède qui porte un `cadre` (instant `ts` dans son audio) :
   *  transition calme depuis la fin de la diapositive, puis respiration jusqu'à la fin. */
  function cadreIntermede(x: Diapo, c: SuiteChant & { cadre: Rect }, ts: number): Rect {
    if (mouvementReduit.matches) return c.cadre;
    const A = cadreA(lec.principal(x), x.duree || 6), B = vue(x, c.cadre);
    const { zoom, glisse } = ampleur(A, B);
    const u = Math.max(zoom / VISE_ZOOM, glisse / VISE_GLISSE);
    const d = Math.min(Math.max(DUREE_MIN, u <= 2 * MISE_EN_ROUTE ? 1.5 * u : u + MISE_EN_ROUTE), c.duree / 2);
    if (ts < d) return trajet(A, B, profil(ts, d, Math.min(d / 3, MISE_EN_ROUTE)));
    return souffle(B, ts - d, c.duree - d, c.cadre);
  }
  Object.assign(lec, { css });
}
