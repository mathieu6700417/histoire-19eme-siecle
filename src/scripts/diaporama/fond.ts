// Fonds prolongés des images entières (spec 17, « Fonds prolongés : verdict et intégration ») : une
// image montrée en entier (`x.en`) laissait du noir autour d'elle. Son fond (`x.fond`, ou `p.fond`
// pour un plan) est le prolongement de la scène généré autour de l'image (fond.py) ; il est posé
// SOUS l'image, flouté et un peu assombri, et suit sa transformation : rapprochement lent, entrée en
// scène, recul d'ouverture d'un acte. L'image d'époque reste le fichier servi, intact, par-dessus ;
// seul son tout dernier bord est fondu dans le fond (raccord).
// Le fond d'une image de diapositive est un élément du calque (il suit donc son fondu croisé) ;
// celui d'un plan est dans le fond noir du plan (`.lecteur__noir`, même opacité que le plan).
// Géométrie : `fond.b` est la boîte de l'image dans le fichier de fond (fractions). L'élément a la
// taille qu'il occupe à l'écran quand l'image tient entière dans la scène (échelle de référence) ;
// il reçoit ensuite une translation et une échelle relative. Le flou CSS d'un élément transformé
// grossit avec lui : son rayon est divisé par cette échelle, il reste donc constant à l'écran
// (`FOND_FLOU_*`, part de la largeur de la scène). Rien n'est animé par CSS : tout dérive de la
// transformation de l'image, posée à chaque rendu. Préférence « réduire les animations » : le fond
// reste (il est fixe, comme l'image). Sans `fond`, l'image entière garde son fond noir.
// README : « Fonds prolongés (spec 17) ».
import { FOND_FLOU_FAIBLE, FOND_FLOU_FORT, FOND_LUMIERE, FOND_RACCORD } from './constantes';
import type { Diapo, Fond, Rect } from './types';
import type { Lecteur } from './contexte';

export function installerFond(lec: Lecteur) {
  const { scene } = lec;
  Object.assign(lec, { creerFond, majFond, placerFond, prechargerFond, preparerFond });
  const calque = (c: HTMLElement) => c.querySelector<HTMLElement>(':scope > .lecteur__fond')!;
  const TR = /translate3d\((-?[\d.]+)px, (-?[\d.]+)px, 0(?:px)?\) scale\(([\d.]+)\)/;

  /** Raccord : le tout dernier bord de la zone utile de `img` devient transparent (largeur `r` px
   *  de l'image posée), pour que l'image se fonde dans son fond. `r` ≤ 0 : image entière. */
  function raccorder(img: HTMLElement, u: Rect, r: number) {
    const cle = r > 0 ? `${u.join(',')}|${r.toFixed(2)}` : '';
    if ((img.dataset.raccord ?? '') === cle) return;
    if (!cle) {
      delete img.dataset.raccord;
      for (const p of ['mask-image', '-webkit-mask-image', 'mask-composite', '-webkit-mask-composite']) img.style.removeProperty(p);
      return;
    }
    img.dataset.raccord = cle;
    const pc = (v: number) => `${(v * 100).toFixed(4)}%`, px = `${r.toFixed(2)}px`;
    const bande = (sens: string, a: number, b: number) =>
      `linear-gradient(${sens}, transparent ${pc(a)}, #000 calc(${pc(a)} + ${px}), #000 calc(${pc(b)} - ${px}), transparent ${pc(b)})`;
    const masque = `${bande('to right', u[0], u[2])}, ${bande('to bottom', u[1], u[3])}`;
    img.style.setProperty('-webkit-mask-image', masque);
    img.style.setProperty('-webkit-mask-composite', 'source-in');
    img.style.setProperty('mask-image', masque);
    img.style.setProperty('mask-composite', 'intersect');
  }

  /** Pose le fond `el` sous l'image `base` (zone utile `u`, transformation `tr`) ; `gris` : le
   *  gris de l'entrée de l'image (absent : celui du dernier rendu, calque figé). */
  function placerFond(el: HTMLElement, base: HTMLImageElement, F: Fond, u: Rect, tr: string, gris?: number) {
    const m = TR.exec(tr), IW = parseFloat(base.style.width) || 0, IH = parseFloat(base.style.height) || 0;
    const W = scene.clientWidth, H = scene.clientHeight;
    if (!m || !IW || !IH || !W || !H) return;
    const tx = +m[1], ty = +m[2], s = +m[3];
    const iw = IW * (u[2] - u[0]), ih = IH * (u[3] - u[1]);
    // Échelle de référence : l'image entière dans la scène (sans les bandeaux du plein écran).
    const sr = Math.min(W / iw, H / ih), k = s / sr;
    const w0 = (iw * sr) / (F.b[2] - F.b[0]), h0 = (ih * sr) / (F.b[3] - F.b[1]);
    const taille = `${w0.toFixed(2)}x${h0.toFixed(2)}`;
    if (el.dataset.taille !== taille) {
      el.dataset.taille = taille;
      el.style.width = `${w0.toFixed(2)}px`;
      el.style.height = `${h0.toFixed(2)}px`;
    }
    const X = tx + s * IW * u[0] - k * w0 * F.b[0], Y = ty + s * IH * u[1] - k * h0 * F.b[1];
    el.style.transform = `translate3d(${X.toFixed(2)}px, ${Y.toFixed(2)}px, 0) scale(${k.toFixed(6)})`;
    if (gris != null) el.dataset.gris = gris > 0.002 ? gris.toFixed(3) : '';
    // Rayon au vingtième de pixel : pendant le rapprochement, le filtre ne change que de loin en loin.
    const flou = Math.round(((F.fort ? FOND_FLOU_FORT : FOND_FLOU_FAIBLE) * W) / k * 20) / 20;
    const filtre = `blur(${flou}px) brightness(${FOND_LUMIERE})${el.dataset.gris ? ` grayscale(${el.dataset.gris})` : ''}`;
    if (el.style.filter !== filtre) el.style.filter = filtre;
    raccorder(base, u, (FOND_RACCORD * W) / sr);
    // La version colorisée (spec 16) recouvre l'image : même raccord, sur sa propre boîte.
    const co = base.nextElementSibling;
    if (co instanceof HTMLElement && co.classList.contains('lecteur__couleur') && !co.hidden) raccorder(co, [0, 0, 1, 1], (FOND_RACCORD * W) / sr);
  }

  const image = (el: HTMLElement, F: Fond) => { const v = `url("${F.src}")`; if (el.dataset.src !== F.src) { el.dataset.src = F.src; el.style.backgroundImage = v; } };

  /** Élément de fond d'une image de série (plan, galerie), à glisser dans son fond noir. */
  function creerFond(F: Fond) {
    const el = document.createElement('i');
    el.className = 'lecteur__fond';
    image(el, F);
    return el;
  }

  /** Pose le fond de l'image de la diapositive dans le calque (ou le retire, avec le raccord). */
  function preparerFond(c: HTMLElement, x: Diapo) {
    const el = calque(c), img = c.querySelector('img')!;
    if (!x.fond || !x.en) {
      if (!el.hidden) { el.hidden = true; el.style.backgroundImage = ''; delete el.dataset.src; }
      raccorder(img, x.u, 0);
      const co = img.nextElementSibling;
      if (co instanceof HTMLElement && co.classList.contains('lecteur__couleur')) raccorder(co, [0, 0, 1, 1], 0);
      return;
    }
    image(el, x.fond);
    el.hidden = false;
  }

  /** À chaque rendu (et pour un calque figé) : le fond suit la transformation `tr` de l'image. */
  function majFond(c: HTMLElement, x: Diapo, tr: string, gris?: number) {
    if (!x.fond || !x.en) return;
    placerFond(calque(c), c.querySelector('img')!, x.fond, x.u, tr, gris);
  }

  // Fonds des diapositives à venir, chargés d'avance : jamais de noir en attendant le fichier.
  function prechargerFond(x: Diapo) {
    for (const i of [x, ...(x.plans ?? []), ...(lec.galerieDe(x) ?? [])]) if (i.fond) new Image().src = i.fond.src;
  }
}
