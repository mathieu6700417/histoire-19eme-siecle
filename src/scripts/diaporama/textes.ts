// Textes : estompe des cartouches, changement du cartouche (fondu croisé) et du sous-titre.
// Spec 12, « Cartouches lisibles et cartons plus longs », « Lecteur ».
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerTextes(lec: Lecteur) {
  const { elLegende, elMusique, elSt, legendeVoulue, racine } = lec;
  Object.assign(lec, { changerCartouche, changerLegende, changerSousTitre, estomperPlusTard,
    revelerCartouches });
  // --- Textes et compteurs ---------------------------------------------------------------
  /** Cartouche : l'ancien s'efface, le nouveau entre ~0,6 s après l'image (CSS). */
  /** Bandeaux (cartouches de l'image et de la musique) : bien visibles quelques secondes à
   *  chaque changement (~12 s), puis cachés en fondu lent ; le survol ou la pause les ramène (CSS). */
  const ESTOMPE = 12000;   // ms
  const REAPPARITION = 4000; // ms : après un toucher sur l'image (téléphone)
  const minuteriesEstompe = new Map<HTMLElement, number>();
  function estomperPlusTard(el: HTMLElement, delai = ESTOMPE) {
    el.classList.remove('est-discret');
    clearTimeout(minuteriesEstompe.get(el));
    minuteriesEstompe.set(el, window.setTimeout(() => el.classList.add('est-discret'), delai));
  }
  /** Toucher sur l'image : les cartouches cachés reviennent quelques secondes. */
  function revelerCartouches() {
    for (const el of [elLegende, elMusique]) if (el.classList.contains('est-discret')) estomperPlusTard(el, REAPPARITION);
  }
  function changerCartouche(x: Diapo) { changerLegende(legendeVoulue(x, 0)); }
  function changerLegende(html: string) {
    lec.legendeMontree = html;
    racine.querySelectorAll('.lecteur__legende--sortant').forEach((e) => e.remove());
    if (elLegende.classList.contains('est-visible')) {
      const copie = elLegende.cloneNode(true) as HTMLElement;
      copie.setAttribute('aria-hidden', 'true');
      elLegende.after(copie);
      void copie.offsetWidth;
      copie.classList.add('lecteur__legende--sortant');
      window.setTimeout(() => copie.remove(), 500);
    }
    elLegende.innerHTML = html;
    elLegende.classList.remove('est-visible');
    void elLegende.offsetWidth;
    elLegende.classList.add('est-visible');
    estomperPlusTard(elLegende);
  }
  /** Sous-titre en fondu croisé ; l'ancien texte, sorti du flux, ne change pas la hauteur. */
  function changerSousTitre(texte: string) {
    elSt.querySelectorAll('.st--sortant').forEach((e) => e.remove());
    const ancien = elSt.querySelector<HTMLElement>('.st');
    if (ancien && ancien.textContent === texte) return;
    if (ancien) {
      ancien.classList.add('st--sortant');
      ancien.setAttribute('aria-hidden', 'true');
      window.setTimeout(() => ancien.remove(), 700);
    }
    const s = document.createElement('span');
    s.className = 'st st--entrant';
    s.textContent = texte;
    elSt.append(s);
    void s.offsetWidth;
    s.classList.remove('st--entrant');
  }
}
