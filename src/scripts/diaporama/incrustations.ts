// Éléments des surimpressions et leur taille : médaillon de lieu, citation, portraits, objet,
// manuscrit (halo), chiffre clé (défilement), date républicaine. État partagé : portraits*, mots*.
// Spec 12, « Cartes de lieu et citations », « Portraits », « Enrichissements visuels » ;
// README : sections du même nom.
import { mouvementReduit } from './outils';
import type { Lecteur } from './contexte';

export function installerIncrustations(lec: Lecteur) {
  const { D, elLegende, racine, scene } = lec;
  Object.assign(lec, { majChiffre, majManuscrit, tailleChiffre, tailleLieu, tailleManuscrit, tailleObjet,
    taillePortraits });
  // --- Cartes de lieu et citations en surimpression (spec 12, 2026-10-07) ---------------------
  // Contenu posé à l'entrée de l'image ; affichage dérivé de l'instant de l'audio (rendre) : pause,
  // reprise et sauts restent justes. Médaillon ~5 s quand la voix dit le lieu (zone couverte pour
  // la caméra) ; citation mot à mot (sous-titre masqué), qui l'emporte sur le médaillon (fenêtres
  // déjà arbitrées au build). Au changement d'image, l'ancien contenu s'efface en fondu (copie).
  const elLieu = racine.querySelector<HTMLElement>('.lieu');
  const elPlan = elLieu?.querySelector<HTMLElement>('.lieu__plan') ?? null;
  const elMots = racine.querySelector<HTMLElement>('.mots');
  const elPortraits = racine.querySelector<HTMLElement>('.portraits');
  lec.portraitsEls = [];
  // Bord droit du fond de la rangée (px, depuis son bord gauche) quand il couvre les portraits
  // 1, 2… (mesuré par taillePortraits) ; dernier état écrit (évite les écritures inutiles).
  lec.portraitsFins = [];
  lec.portraitsEtat = '';
  lec.motsEls = [];
  lec.motsDits = -1;
  /** Taille du médaillon : ~un quart de la hauteur de la scène (plancher lisible), selon le fond.
   *  À plusieurs lieux (spec 12, « Sans bordures, et médaillon plus grand ») : une fois et demie
   *  plus grand (~240 × 180 px au lieu de 160 × 120 sur ordinateur), dans la limite de la place
   *  (40 % de la hauteur, la moitié de la largeur), téléphone compris. */
  function tailleLieu() {
    const L = D.diapos[lec.i].lieu, c = elLieu?.querySelector<HTMLElement>('.lieu__carte');
    if (!L || !c) return;
    const H = scene.clientHeight, W = scene.clientWidth;
    let h = Math.max(W < 700 ? 92 : 120, Math.min(230, H * 0.24));
    const multiple = Boolean(L.points?.length);
    if (multiple) h = Math.min(1.5 * h, 300, H * 0.4);
    let w = h * L.ratio;
    const lmax = W * (multiple ? 0.5 : 0.46);
    if (w > lmax) { w = lmax; h = w / L.ratio; }
    c.style.width = `${Math.round(w)}px`;
    c.style.height = `${Math.round(h)}px`;
    elLieu!.style.maxWidth = `${Math.round(w) + 12}px`;
  }
  /** Rangée de portraits (spec 12, « Portraits des personnes nommées ») : ovales d'environ 17 %
   *  de la hauteur de la scène (78 à 118 px de haut sur ordinateur, 50 sur téléphone), réduits si
   *  la rangée ne tient pas à côté du médaillon de lieu (coin opposé). Puis la citation : si elle
   *  touche la rangée, elle monte au-dessus d'elle, pour toute la diapositive (rien ne bouge
   *  pendant qu'elle est lue). */
  function taillePortraits() {
    const P = D.diapos[lec.i].portraits;
    if (!elPortraits || !P) return;
    const H = scene.clientHeight, W = scene.clientWidth;
    const gauche = parseFloat(getComputedStyle(elPortraits).left) || 8;
    // ~1,5 fois la taille d'origine (retour de l'utilisateur du 2026-10-08).
    let h = Math.max(W < 700 ? 70 : 110, Math.min(180, H * 0.25));
    elPortraits.style.setProperty('--ovale-h', `${Math.round(h)}px`);
    const lieu = D.diapos[lec.i].lieu && elLieu ? elLieu.offsetWidth + gauche : 0;
    const place = W - 2 * gauche - lieu;
    if (elPortraits.offsetWidth > place && place > 0) {
      h = Math.max(34, h * (place / elPortraits.offsetWidth));
      elPortraits.style.setProperty('--ovale-h', `${Math.round(h)}px`);
    }
    if (elMots) elMots.style.bottom = '';
    if (elMots && D.diapos[lec.i].citation) {
      const libre = (W - elMots.offsetWidth) / 2;
      if (libre < gauche + elPortraits.offsetWidth + 8) elMots.style.bottom = `calc(var(--surimp-bas, var(--frise-bas, 0px)) + var(--frise-pousse, 0px) + ${Math.round(elPortraits.offsetHeight + (parseFloat(getComputedStyle(elLegende).top) || 8) + 8)}px)`;
    }
    // Largeurs du fond (bord extérieur compris) : jusqu'au bord droit du portrait k, plus la
    // marge intérieure et le filet ; le dernier couvre la rangée entière.
    const cs = getComputedStyle(elPortraits);
    const bg = parseFloat(cs.borderLeftWidth) || 0, fin = (parseFloat(cs.paddingRight) || 0) + (parseFloat(cs.borderRightWidth) || 0);
    // Scène non mise en page (offsetWidth nul) : mesure reprise à la prochaine image.
    lec.portraitsFins = elPortraits.offsetWidth > 0 ? lec.portraitsEls.map((f, k) => k === lec.portraitsEls.length - 1
      ? elPortraits.offsetWidth : Math.min(elPortraits.offsetWidth, bg + f.offsetLeft + f.offsetWidth + fin)) : [];
    lec.portraitsEtat = '';
  }
  // --- Objets de musée et manuscrits (spec 12, « Enrichissements visuels », 2026-10-08) -----
  const elObjet = racine.querySelector<HTMLElement>('.objet');
  const elManuscrit = racine.querySelector<HTMLElement>('.manuscrit');
  const msDoc = elManuscrit?.querySelector<HTMLElement>('.manuscrit__doc') ?? null;
  const msHalo = elManuscrit?.querySelector<HTMLElement>('.manuscrit__halo') ?? null;
  lec.msEtat = '';
  /** Objet : image d'environ 22 % de la hauteur de la scène (96 à 200 px sur ordinateur, 56 au
   *  moins sur téléphone ; 1,3 fois plus pour un objet très étroit), 30 % de la largeur au plus
   *  (34 % sur téléphone). */
  function tailleObjet() {
    const O = D.diapos[lec.i].objet;
    if (!elObjet || !O) return;
    const H = scene.clientHeight, W = scene.clientWidth;
    let h = Math.max(W < 700 ? 56 : 96, Math.min(200, H * 0.22));
    // Objet très étroit (sabre) : un peu plus haut, sinon il ne se lit pas.
    if (O.ratio < 0.5) h = Math.min(h * 1.3, H * 0.3);
    let l = h * O.ratio;
    const lmax = W * (W < 700 ? 0.34 : 0.3);
    if (l > lmax) { l = lmax; h = l / O.ratio; }
    elObjet.style.setProperty('--objet-h', `${Math.round(h)}px`);
    elObjet.style.setProperty('--objet-l', `${Math.round(l)}px`);
  }
  /** Manuscrit : la page tient entre le cartouche et le bas occupé de son côté (médaillon de lieu
   *  à droite, portraits à gauche, objet dans son coin), 72 % de la hauteur de la scène au plus,
   *  40 % de sa largeur au plus (46 % sur téléphone), centrée dans cette bande ; la légende est
   *  comptée. Il ne réserve rien pour la caméra (comme la citation, il passe devant l'image). */
  function tailleManuscrit() {
    const M = D.diapos[lec.i].manuscrit;
    if (!elManuscrit || !M) return;
    const H = scene.clientHeight, W = scene.clientWidth, ecart = W < 700 ? 6 : 12;
    // Sous le cartouche en entier (la réduction des marges de la caméra ne vaut pas ici).
    const haut = Math.min(lec.hautBrut, 0.4 * H);
    const libre = H - haut - Math.min(lec.basCotes[M.cote], 0.45 * H) - 2 * ecart;
    let h = Math.min(H * 0.72, libre - 44), l = h * M.ratio;
    const lmax = W * (W < 700 ? 0.46 : 0.4);
    if (l > lmax) { l = lmax; h = l / M.ratio; }
    const poser = () => {
      elManuscrit.style.setProperty('--ms-l', `${Math.round(l)}px`);
      elManuscrit.style.setProperty('--ms-h', `${Math.round(h)}px`);
    };
    poser();
    // La légende compte : si le tout dépasse la bande libre, la page est réduite d'autant.
    const trop = elManuscrit.offsetHeight - libre;
    if (trop > 0) { h = Math.max(60, h - trop); l = h * M.ratio; poser(); }
    elManuscrit.style.setProperty('--ms-haut', `${Math.round(haut + ecart + Math.max(0, (libre - elManuscrit.offsetHeight) / 2))}px`);
  }
  /** Zoom du manuscrit à l'instant `t` : de la page entière (1 s après son entrée) au passage
   *  éclairé (2,5 s de trajet, courbe douce, zoom logarithmique, 2,4 fois au plus, le passage
   *  occupant ~80 % de la page), puis halo en 1,2 s ; mouvement réduit : pas de zoom, halo
   *  d'emblée. Dérivé de l'instant lissé de l'audio : pause, reprise et sauts justes. */
  function majManuscrit(t: number) {
    const M = D.diapos[lec.i].manuscrit;
    if (!msDoc || !msHalo || !M) return;
    const doux = (v: number) => { const u = Math.max(0, Math.min(1, v)); return u * u * (3 - 2 * u); };
    const [x0, y0, x1, y1] = M.halo, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const cible = Math.max(1, Math.min(2.4, 0.8 / (x1 - x0), 0.8 / (y1 - y0)));
    const reduit = mouvementReduit.matches;
    const p = reduit ? 0 : doux((t - M.a - 1) / 2.5);
    const z = Math.pow(cible, p);
    const tx = Math.min(0, Math.max(1 - z, 0.5 - z * cx)), ty = Math.min(0, Math.max(1 - z, 0.5 - z * cy));
    const q = reduit ? (t >= M.a + 0.8 ? 1 : 0) : doux((t - M.a - 3) / 1.2);
    const etat = `translate(${(tx * 100).toFixed(3)}%, ${(ty * 100).toFixed(3)}%) scale(${z.toFixed(5)})|${q.toFixed(3)}`;
    if (etat === lec.msEtat) return;
    lec.msEtat = etat;
    const [tr, op] = etat.split('|');
    msDoc.style.transform = tr;
    msHalo.style.setProperty('--p', op);
  }
  // --- Chiffres clés et dates républicaines (spec 12, « Enrichissements visuels », point 4) --
  const elChiffre = racine.querySelector<HTMLElement>('.chiffre');
  const elChiffreValeur = elChiffre?.querySelector<HTMLElement>('.chiffre__valeur') ?? null;
  const elDate = racine.querySelector<HTMLElement>('.date-rep');
  const DEFILE = 1.4; // s : le chiffre défile jusqu'à sa valeur (courbe qui ralentit)
  const ecrireNombre = (v: number) => String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f');
  /** Chiffre : ~15 % de la hauteur de la scène (54 à 112 px ; 40 px au moins sur téléphone).
   *  Centré dans le tiers inférieur ; s'il se montre en même temps qu'une surimpression de coin
   *  bas qui le toucherait, ou que la date républicaine, il monte au-dessus d'elle pour toute la
   *  diapositive (rien ne bouge pendant qu'il est là). Il ne réserve rien pour la caméra. */
  function tailleChiffre() {
    const x = D.diapos[lec.i], C = x.chiffre;
    if (!elChiffre || !C) return;
    const H = scene.clientHeight, W = scene.clientWidth;
    elChiffre.style.setProperty('--chiffre-t', `${Math.round(Math.max(W < 700 ? 40 : 54, Math.min(112, H * 0.15)))}px`);
    elChiffre.style.removeProperty('--chiffre-bas');
    const ensemble = (f: { a: number; b: number } | null) => !!f && Math.min(f.b, C.b) > Math.max(f.a, C.a);
    const ecart = W < 700 ? 6 : 10;
    let bas = H * (W < 700 ? 0.06 : 0.07);
    const libre = (W - elChiffre.offsetWidth) / 2;
    for (const [el, f] of [[elLieu, x.lieu], [elPortraits, x.portraits], [elObjet, x.objet]] as const) {
      if (!el || !ensemble(f)) continue;
      const cs = getComputedStyle(el);
      const bord = Math.max(...[cs.left, cs.right].map((v) => parseFloat(v)).filter((v) => isFinite(v) && v >= 0 && v < W / 3), 0);
      if (el.offsetWidth + bord + 8 > libre) bas = Math.max(bas, el.offsetHeight + bord + ecart);
    }
    if (elDate && ensemble(x.dateRep)) {
      const bord = W < 700 ? 8 : 12;
      bas = Math.max(bas, elDate.offsetHeight + bord + ecart);
    }
    elChiffre.style.setProperty('--chiffre-bas', `${Math.round(bas)}px`);
  }
  /** Valeur du chiffre à l'instant `t` : de 0 à sa valeur en 1,4 s (par pas ronds : 1, 10 ou
   *  1 000 selon sa grandeur), puis fixe ; sous 20, ou en mouvement réduit, la valeur d'emblée. */
  lec.chiffreTexte = '';
  function majChiffre(t: number) {
    const C = D.diapos[lec.i].chiffre;
    if (!elChiffreValeur || !C) return;
    const p = mouvementReduit.matches || !C.defile ? 1 : Math.max(0, Math.min(1, (t - C.a) / DEFILE));
    const pas = Math.max(1, Math.pow(10, Math.floor(Math.log10(C.valeur)) - 2));
    const v = p >= 1 ? C.valeur : Math.round((C.valeur * (1 - Math.pow(1 - p, 3))) / pas) * pas;
    const texte = ecrireNombre(v);
    if (texte !== lec.chiffreTexte) { elChiffreValeur.textContent = texte; lec.chiffreTexte = texte; }
  }
  Object.assign(lec, { elChiffre, elDate, elLieu, elManuscrit, elMots, elObjet, elPlan, elPortraits, msHalo });
}
