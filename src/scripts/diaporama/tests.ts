// Points d'entrée des tests et des captures (scripts/diaporamas/captures.py) : `__aller(n, segment)`,
// `__instant()`, `__camera(n, t)` ; `__clip()` est dans chant.ts, `__musique()` dans musique.ts.
// README : « Caméra : format et pièges », « Lecteur : carte des modules ».
import { ampleur } from './geometrie';
import { mouvementReduit } from './outils';
import type { Lecteur } from './contexte';

export function installerTests(lec: Lecteur) {
  const { D, aller, allerSuite, apresDe, audio, cadreA, deverrouillerAudio, horloge, plan, plongee,
    principal, racine, vue } = lec;
  // Pour les tests : saut vers une diapositive (par son numéro) ou vers son segment.
  (racine as any).__aller = (n: number, segment = false) => {
    const k = D.diapos.findIndex((x) => x.n === n);
    if (k < 0) return;
    deverrouillerAudio();
    return segment ? allerSuite(k) : aller(k);
  };
  // Horloge (tests) : dernier instant lissé rendu et valeur brute de l'audio.
  (racine as any).__instant = () => ({ lisse: horloge.t, brut: audio.currentTime });
  // Contrôle de la caméra (tests) : cadre montré à l'instant `t` de la diapositive `n`.
  (racine as any).__camera = (n: number, t: number) => {
    const x = D.diapos.find((d) => d.n === n);
    if (!x) return null;
    const xp = principal(x);
    const r = cadreA(xp, t);
    const ap = x.ap && t >= x.ap.t ? (() => { const xa = apresDe(x); return { cadre: cadreA(xa, t), plan: plan(xa).map((e) => ({ t: e.t, de: e.de, a: e.a })) }; })() : null;
    const mos = x.mos && !x.ouv ? (() => { const g = plongee(x); return { debut: g.t0, duree: g.d, fin: g.a0, sigma: g.sigma }; })() : null;
    const plans = (x.plans ?? []).map((p, k, P) => { const xq = lec.planDe(x, p, k + 1 < P.length ? P[k + 1].t + 0.8 : x.duree || 6); return { t: p.t, visible: t >= p.t, cadre: cadreA(xq, t), plan: plan(xq).map((e) => ({ t: e.t, de: e.de, a: e.a })) }; });
    return { ap, mos, plans, cadre: r, vue: vue(x, r), utile: x.u, etapes: x.camera, duree: x.duree, effectives: mouvementReduit.matches ? x.camera.length : plan(xp).length,
      plan: plan(xp).map((e, k, P) => ({ t: e.t, de: e.de, a: e.a, ...(k ? ampleur(P[k - 1].v, e.v) : {}) })) };
  };
}
