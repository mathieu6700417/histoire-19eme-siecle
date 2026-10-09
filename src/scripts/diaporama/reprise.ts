// Reprise mémorisée (localStorage) et premier rendu, avant tout clic. Installé en dernier.
// Spec 12, « Lecteur (`Diaporama.astro`) ».
import { ecrire, lire } from './outils';
import type { Lecteur } from './contexte';

export function installerReprise(lec: Lecteur) {
  const { CLE_POS, D, btnReprendre, cadre, calques, majTemps, mesurerMarges, precharger, rendre } = lec;
  // Reprise : « Reprendre à la diapositive 37 ». La position est mémorisée par la clé stable
  // de la diapositive (son fichier Commons) ; un ancien numéro (format d'avant, chiffres
  // seuls) est accepté une fois, puis réécrit sous forme de clé.
  const memo = lire(CLE_POS);
  let k = memo ? D.diapos.findIndex((x) => x.cle === memo) : -1;
  if (k < 0 && memo && /^\d+$/.test(memo)) {
    k = D.diapos.findIndex((x) => x.n === Number(memo));
    ecrire(CLE_POS, k >= 0 ? D.diapos[k].cle : null);
  }
  if (k > 0) {
    btnReprendre.hidden = false;
    btnReprendre.dataset.index = String(k);
    btnReprendre.textContent = `Reprendre à la diapositive ${D.diapos[k].n}`;
  }

  cadre(calques[0], D.diapos[0]);
  mesurerMarges();
  rendre(0);
  majTemps();
  precharger(0);
}
