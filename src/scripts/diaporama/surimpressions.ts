// Surimpressions d'une diapositive : chargement (contenu des éléments d'`incrustations`) et mise à
// jour à l'instant t (fenêtres [a, b), mots dits, ovales des portraits). Lit `x.lieu`, `x.citation`,
// `x.portraits`, `x.objet`, `x.manuscrit`, `x.chiffre`, `x.dateRep`. Mêmes sections que incrustations.
import { PORTRAIT_ELARGIR, PORTRAIT_FONDU } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerSurimpressions(lec: Lecteur) {
  const { D, elChiffre, elDate, elLieu, elManuscrit, elMots, elObjet, elPlan, elPortraits, lecteur,
    majChiffre, majManuscrit, majPoussee, msHalo, tailleChiffre, tailleLieu, tailleObjet, taillePortraits } = lec;
  Object.assign(lec, { chargerSurimpressions, majSurimpressions });
  /** Copie qui s'efface (transition CSS) pendant que l'original reçoit le contenu suivant. */
  function effacer(el: HTMLElement) {
    if (!el.classList.contains('est-visible')) return;
    const copie = el.cloneNode(true) as HTMLElement;
    el.after(copie);
    void copie.offsetWidth;
    copie.classList.remove('est-visible');
    window.setTimeout(() => copie.remove(), 900);
    el.classList.remove('est-visible');
  }
  function chargerSurimpressions(x: Diapo | null) {
    if (elLieu) effacer(elLieu);
    if (elMots) effacer(elMots);
    if (elPortraits) effacer(elPortraits);
    if (elObjet) effacer(elObjet);
    if (elManuscrit) effacer(elManuscrit);
    if (elChiffre) effacer(elChiffre);
    if (elDate) effacer(elDate);
    lecteur.classList.remove('avec-citation', 'avec-lieu', 'avec-portraits', 'avec-objet', 'avec-manuscrit', 'avec-chiffre', 'avec-date');
    // Chiffre et date : contenu posé d'emblée (invisible).
    const CH = x?.chiffre, DR = x?.dateRep;
    if (elChiffre && CH) {
      elChiffre.querySelector('.chiffre__prefixe')!.textContent = CH.prefixe;
      elChiffre.querySelector('.chiffre__mesure')!.textContent = CH.texte;
      elChiffre.querySelector('.chiffre__unite')!.textContent = CH.unite;
      lec.chiffreTexte = '';
      majChiffre(CH.a);
    }
    if (elDate && DR) {
      elDate.querySelector('.date-rep__rep')!.textContent = DR.republicain;
      elDate.querySelector('.date-rep__greg')!.textContent = DR.gregorien;
    }
    // Objet et manuscrit : contenu posé d'emblée (invisible), si bien que la place réservée ne
    // change pas pendant la diapositive.
    const O = x?.objet, M = x?.manuscrit;
    for (const [el, v] of [[elObjet, O], [elManuscrit, M]] as const) {
      if (!el || !v) continue;
      el.querySelector('img')!.src = v.src;
      el.querySelector('.objet__nom')!.textContent = v.nom;
      el.querySelector('.objet__legende')!.textContent = v.legende;
      el.classList.toggle('est-gauche', v.cote === 'gauche');
    }
    if (M && msHalo) {
      const [x0, y0, x1, y1] = M.halo;
      Object.assign(msHalo.style, { left: `${x0 * 100}%`, top: `${y0 * 100}%`, width: `${(x1 - x0) * 100}%`, height: `${(y1 - y0) * 100}%` });
      lec.msEtat = '';
    }
    tailleObjet();
    const L = x?.lieu;
    if (elLieu && L) {
      elLieu.querySelectorAll<HTMLElement>('.lieu__fond').forEach((f) => f.classList.toggle('est-actif', f.dataset.fond === L.fond));
      if (L.fond === 'paris' && elPlan && L.vue) {
        const [taille, position] = L.vue.split(';');
        if (!elPlan.style.backgroundImage) elPlan.style.backgroundImage = `url("${elPlan.dataset.src}")`;
        elPlan.style.backgroundSize = taille;
        elPlan.style.backgroundPosition = position;
      }
      const pt = elLieu.querySelector<HTMLElement>('.lieu__point')!;
      pt.style.left = `${L.x}%`;
      pt.style.top = `${L.y}%`;
      elLieu.querySelector('.lieu__nom')!.textContent = L.nom;
      elLieu.querySelector('.lieu__credit')!.textContent = L.credit ?? '';
      tailleLieu();
    }
    const C = x?.citation;
    lec.motsEls = [];
    lec.motsDits = -1;
    if (elMots && !C) elMots.querySelector('.mots__texte')!.innerHTML = '';
    if (elMots && C) {
      elMots.classList.remove('est-signe');
      elMots.querySelector('.mots__texte')!.innerHTML = C.html;
      elMots.querySelector('.mots__auteur')!.textContent = C.auteur;
      lec.motsEls = C.mots.map(() => []);
      elMots.querySelectorAll<HTMLElement>('.m').forEach((m) => lec.motsEls[Number(m.dataset.k)]?.push(m));
    }
    // Portraits : tous les ovales sont posés d'emblée (invisibles), si bien que la rangée garde
    // sa taille (place réservée pour la caméra, constante) ; seul son fond s'élargit, et chacun
    // paraît à son nom (majSurimpressions).
    const P = x?.portraits;
    lec.portraitsEls = [];
    lec.portraitsFins = [];
    lec.portraitsEtat = '';
    if (elPortraits) {
      elPortraits.replaceChildren();
      elPortraits.classList.toggle('est-seul', P?.gens.length === 1);
      for (const g of P?.gens ?? []) {
        const fig = document.createElement('figure');
        fig.className = 'portrait';
        const ovale = document.createElement('span');
        ovale.className = 'portrait__ovale';
        const img = document.createElement('img');
        img.src = g.src;
        img.alt = '';
        img.decoding = 'async';
        ovale.append(img);
        const leg = document.createElement('figcaption');
        const nom = document.createElement('span'), sep = document.createElement('span'), dates = document.createElement('span');
        nom.className = 'portrait__nom'; nom.textContent = g.nom;
        sep.className = 'portrait__sep'; sep.textContent = ' · ';
        dates.className = 'portrait__dates'; dates.textContent = g.dates;
        leg.append(nom, sep, dates);
        fig.append(ovale, leg);
        elPortraits.append(fig);
        lec.portraitsEls.push(fig);
      }
      taillePortraits();
    }
    tailleChiffre();
  }
  /** Surimpressions possibles : lecture lancée, ni carton ni segment après la voix. */
  const surimpressionsActives = () => lec.lance && !lec.enCarton && !lec.enSuite && !lec.suiteFini;
  function majSurimpressions(t: number) {
    const x = D.diapos[lec.i], actif = surimpressionsActives();
    const L = x.lieu, C = x.citation, P = x.portraits, O = x.objet, M = x.manuscrit;
    if (elObjet && O) {
      const vu = actif && t >= O.a && t < O.b;
      if (vu !== elObjet.classList.contains('est-visible')) { elObjet.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-objet', vu); }
    }
    if (elManuscrit && M) {
      const vu = actif && t >= M.a && t < M.b;
      if (vu !== elManuscrit.classList.contains('est-visible')) { elManuscrit.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-manuscrit', vu); }
      majManuscrit(t);
    }
    const CH = x.chiffre, DR = x.dateRep;
    if (elChiffre && CH) {
      const vu = actif && t >= CH.a && t < CH.b;
      if (vu !== elChiffre.classList.contains('est-visible')) { elChiffre.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-chiffre', vu); }
      majChiffre(t);
    }
    if (elDate && DR) {
      const vu = actif && t >= DR.a && t < DR.b;
      if (vu !== elDate.classList.contains('est-visible')) { elDate.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-date', vu); }
    }
    // Frise du temps (révision du 2026-10-09) : elle ne cède plus ; elle prend le bas et pousse
    // celles qui la chevauchent en largeur plus haut (--frise-pousse, cf. majPoussee).
    majPoussee();
    if (elLieu && L) {
      const vu = actif && t >= L.a && t < L.b;
      if (vu !== elLieu.classList.contains('est-visible')) { elLieu.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-lieu', vu); }
    }
    if (elPortraits && P) {
      const vu = actif && t >= P.a && t < P.b;
      if (vu !== elPortraits.classList.contains('est-visible')) { elPortraits.classList.toggle('est-visible', vu); lecteur.classList.toggle('avec-portraits', vu); }
      // Chaque ovale paraît quand la voix attaque le nom (le premier dès l'entrée de la rangée) ;
      // les précédents restent. Rangée qui grandit (retour de l'utilisateur du 2026-10-08) : le
      // fond ne couvre que les portraits apparus ; à un nouveau nom, il s'élargit vers la droite
      // (PORTRAIT_ELARGIR s), puis l'ovale paraît en fondu (PORTRAIT_FONDU s). Tout dérive de
      // l'instant lissé : pause, reprise et sauts justes. Mouvement réduit : sans animation.
      let n = 0;
      while (n < P.gens.length && P.gens[n].t <= t + 0.06) n++;
      n = Math.max(1, n);
      const k = n - 1, t0 = P.gens[k].t - 0.06, reduit = mouvementReduit.matches;
      const el = k === 0 || reduit ? 1 : adoucir((t - t0) / PORTRAIT_ELARGIR);
      const ap = k === 0 || reduit ? 1 : adoucir((t - t0 - PORTRAIT_ELARGIR) / PORTRAIT_FONDU);
      if (!lec.portraitsFins.length && lec.portraitsEls.length && elPortraits.offsetWidth > 0) taillePortraits();
      const fins = lec.portraitsFins;
      const l = fins.length > k ? (k === 0 ? fins[0] : fins[k - 1] + (fins[k] - fins[k - 1]) * el) : NaN;
      const etat = `${k}:${el.toFixed(3)}:${ap.toFixed(3)}:${l.toFixed(1)}`;
      if (etat !== lec.portraitsEtat) {
        if (Number.isFinite(l)) elPortraits.style.setProperty('--fond-l', `${l.toFixed(1)}px`);
        lec.portraitsEls.forEach((e, j) => {
          const o = j < k ? 1 : j > k ? 0 : ap;
          e.style.opacity = o.toFixed(3);
          e.style.transform = o > 0 && o < 1 ? `translateY(${(3 * (1 - o)).toFixed(2)}px)` : '';
        });
        lec.portraitsEtat = etat;
      }
    }
    if (!elMots || !C) return;
    const vu = actif && t >= C.a && t < C.b;
    if (vu !== elMots.classList.contains('est-visible')) {
      elMots.classList.toggle('est-visible', vu);
      lecteur.classList.toggle('avec-citation', vu);
    }
    // Mots dits (le mot paraît quand la voix l'attaque) ; mouvement réduit : la citation entière.
    let n = 0;
    if (mouvementReduit.matches) n = t >= C.a ? C.mots.length : 0;
    else while (n < C.mots.length && C.mots[n] <= t + 0.06) n++;
    if (n !== lec.motsDits) {
      lec.motsEls.forEach((els, k) => els.forEach((m) => m.classList.toggle('est-dit', k < n)));
      lec.motsDits = n;
    }
    elMots.classList.toggle('est-signe', t >= C.fin || (mouvementReduit.matches && n > 0));
  }
}
