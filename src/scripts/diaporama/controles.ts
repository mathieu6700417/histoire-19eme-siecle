// Contrôles : clics (data-action), barre des actes, sous-titres, plein écran, recadrage au
// redimensionnement, masquage des contrôles, clavier, balayage. Spec 12, « Lecteur ».
import { CLE_ST } from './constantes';
import { ecrire, lire } from './outils';
import type { Lecteur } from './contexte';

export function installerControles(lec: Lecteur) {
  const { D, ajusterFrises, aller, allerSuite, basculer, basculerMusique, bornes, btnLecture, btnMusique,
    btnPe, btnSt, cadre, calques, couches, debuts, lancer, lecteur, majBasSurimpressions, majSuite,
    mesurerMarges, passerCarton, poser, prelude, racine, rendre, revelerCartouches, scene, segments,
    suivant, tailleChiffre, tailleLieu, tailleObjet, taillePortraits, voixEtPause } = lec;
  Object.assign(lec, { montrerControles });
  // --- Contrôles ---------------------------------------------------------------------------
  racine.addEventListener('click', (e) => {
    const b = (e.target as Element).closest<HTMLElement>('[data-action]');
    if (!b || !racine.contains(b)) return;
    const action = b.dataset.action;
    if (action === 'lancer') lancer(0);
    else if (action === 'reprendre') lancer(Number(b.dataset.index));
    else if (action === 'basculer') basculer();
    else if (action === 'precedent') aller(lec.i - 1);
    else if (action === 'suivant') suivant();
    else if (action === 'passer') passerCarton();
    else if (action === 'sous-titres') sousTitres(!lecteur.classList.contains('avec-st'));
    else if (action === 'plein-ecran') pleinEcran();
    else if (action === 'musique') basculerMusique();
  });
  segments.forEach((s) => s.addEventListener('click', (e) => {
    // Clic dans un segment : on saute à l'endroit visé ; clavier : au début de l'acte.
    const ev = e as MouseEvent;
    if (ev.detail === 0) return aller(D.diapos.findIndex((x) => x.n >= Number(s.dataset.debut)));
    const r = s.getBoundingClientRect();
    const k = segments.indexOf(s);
    const t = bornes[k].t0 + ((ev.clientX - r.left) / r.width) * (bornes[k].t1 - bornes[k].t0);
    let j = bornes[k].de;
    while (j + 1 < bornes[k].fin && debuts[j + 1] <= t) j++;
    // Dans la part d'un segment (chant, lecture, épisode) : directement au segment.
    if (D.diapos[j].suite && t >= debuts[j] + prelude[j] + voixEtPause[j]) return allerSuite(j);
    aller(j);
  }));

  function sousTitres(oui: boolean) {
    lecteur.classList.toggle('avec-st', oui);
    btnSt.setAttribute('aria-pressed', String(oui));
    mesurerMarges();
    rendre();
    ecrire(CLE_ST, oui ? 'oui' : 'non');
  }
  sousTitres(lire(CLE_ST) !== 'non');

  // Plein écran (API Fullscreen ; caché si le navigateur ne la permet pas, ex. iPhone).
  const peDispo = document.fullscreenEnabled || (document as any).webkitFullscreenEnabled;
  if (!peDispo) btnPe.hidden = true;
  function pleinEcran() {
    const el = document.fullscreenElement ?? (document as any).webkitFullscreenElement;
    if (el) (document.exitFullscreen ?? (document as any).webkitExitFullscreen).call(document);
    else (lecteur.requestFullscreen ?? (lecteur as any).webkitRequestFullscreen).call(lecteur);
  }
  // Après un changement de taille, la caméra est recalculée pour l'instant courant ; les
  // calques figés (sortant d'un fondu, image sous un carton) sont reposés sur leur cadre.
  function recadrer() {
    couches.forEach((c, k) => { if (c.x) cadre(calques[k], c.x); });
    tailleLieu();
    taillePortraits();
    tailleObjet();
    mesurerMarges();
    tailleChiffre();
    couches.forEach((c, k) => { if (c.x && (k !== lec.visible || c.x !== D.diapos[lec.i])) poser(k); });
    rendre();
    ajusterFrises();
    majSuite();
  }
  const auRedimensionnement = () => {
    recadrer();
    btnPe.setAttribute('aria-pressed', String(Boolean(document.fullscreenElement)));
    montrerControles();
  };
  document.addEventListener('fullscreenchange', auRedimensionnement);
  new ResizeObserver(recadrer).observe(scene);

  // En plein écran, légende et contrôles s'effacent après 3 s d'inactivité.
  let inactivite = 0;
  function montrerControles() {
    lecteur.classList.remove('inactif');
    majBasSurimpressions();
    clearTimeout(inactivite);
    inactivite = window.setTimeout(() => {
      if (lec.joue && document.fullscreenElement === lecteur) { lecteur.classList.add('inactif'); majBasSurimpressions(); }
    }, 3000);
  }
  for (const ev of ['mousemove', 'touchstart', 'keydown']) lecteur.addEventListener(ev, montrerControles, { passive: true });

  // Clavier : espace, ← →, F, S, Entrée (passer le carton) — sauf dans un champ de saisie.
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const cible = e.target instanceof Element ? e.target : document.body;
    if (cible.closest('input, textarea, select, [contenteditable]')) return;
    if (e.key === ' ' || e.key === 'Spacebar') {
      if (cible.closest('button, a')) return; // le bouton s'active de lui-même
      e.preventDefault(); basculer();
    } else if (e.key === 'ArrowLeft') { e.preventDefault(); aller(lec.i - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); suivant(); }
    else if (e.key === 'Enter') {
      // Pendant un carton, Entrée le passe (même si le focus est sur le bouton de lecture).
      const bouton = cible.closest('button, a');
      if (!lec.enCarton || (bouton && bouton !== btnLecture)) return;
      e.preventDefault(); passerCarton();
    }
    else if (e.key === 'f' || e.key === 'F') { if (peDispo) pleinEcran(); }
    else if (e.key === 's' || e.key === 'S') sousTitres(!lecteur.classList.contains('avec-st'));
    else if ((e.key === 'm' || e.key === 'M') && btnMusique) basculerMusique();
  });

  // Balayage gauche/droite sur l'image.
  let x0 = 0, y0 = 0;
  scene.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
  scene.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) dx < 0 ? suivant() : aller(lec.i - 1);
    else if (Math.abs(dx) < 12 && Math.abs(dy) < 12) revelerCartouches();
  }, { passive: true });
}
