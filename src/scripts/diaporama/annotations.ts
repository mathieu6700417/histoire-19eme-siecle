// Annotations de visionnage (spec 15) : outil LOCAL, chargé seulement par le build de
// `npm run annoter` (import dynamique conditionné par `__ANNOTATIONS__`, lecteur.ts) ; rien de ce
// module ni de ses styles n'existe dans le site déployé. A : pause, panneau de saisie, Entrée
// enregistre (serveur scripts/diaporamas/annoter.py) et reprend ; L : liste ; repères sur la barre.
// README : « Annotations de visionnage (spec 15) ».
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

const CATEGORIES = ['image', 'cadrage', 'texte', 'voix', 'musique', 'surimpression', 'autre'] as const;
type Categorie = typeof CATEGORIES[number];
type TypeLieu = 'diapositive' | 'plan' | 'chant' | 'galerie' | 'lecture' | 'episode' | 'carton' | 'generique' | 'recapitulatif';
interface Lieu { type: TypeLieu; n: number | null; acte: string | null; segment: string | null; plan: string | null;
  image_galerie: number | null; instant: number; temps_global: number }
interface Ecran { image: { fichier: string; commons?: string | null; titre_court?: string | null } | null; phrase: string | null;
  sous_titre: string | null; surimpressions: string[]; camera: { etape: number; vue: number[] } | null;
  musique: string | null; fenetre: [number, number]; plein_ecran: boolean }
interface Annotation { id: string; cree: string; modifie: string | null; slug: string; categorie: Categorie; texte: string;
  etat: 'a-faire' | 'traite'; traitement: string | null; lieu: Lieu; ecran: Ecran; capture: string | null }
type Charge = Pick<Annotation, 'id' | 'cree' | 'categorie' | 'texte' | 'lieu' | 'ecran'>;

const STYLES = `
.annot-panneau, .annot-liste, .annot-message { position: absolute; z-index: 60; box-sizing: border-box; font-family: var(--f-texte); color: var(--c-texte); background: rgba(251, 250, 247, 0.96); }
.annot-panneau[hidden], .annot-liste[hidden], .annot-message[hidden] { display: none; }
.annot-panneau { border-top: 1px solid var(--c-texte); padding: 0.5rem 1rem 0.55rem; }
.annot-contexte { margin: 0 0 0.3rem; font-variant: small-caps; letter-spacing: 0.08em; color: var(--c-texte-doux); font-size: 0.95rem; font-variant-numeric: lining-nums; }
.annot-categories { display: flex; flex-wrap: wrap; gap: 0 1.1rem; margin: 0 0 0.35rem; }
.annot-categories button { font: inherit; font-size: 0.95rem; padding: 0 0 1px; color: var(--c-texte-doux); background: none; border: 0; border-bottom: 1px solid transparent; cursor: pointer; }
.annot-categories button span { font-size: 0.8rem; font-variant-numeric: lining-nums; margin-right: 0.3em; }
.annot-categories button[aria-checked="true"] { color: var(--c-texte); border-bottom-color: var(--c-texte); }
.annot-texte { display: block; width: 100%; box-sizing: border-box; resize: none; font: inherit; font-size: 1.05rem; line-height: 1.4; color: var(--c-texte); background: var(--c-fond); border: 1px solid var(--c-ocre-clair); border-radius: 0; padding: 0.3rem 0.5rem; }
.annot-texte:focus { outline: none; border-color: var(--c-texte); }
.annot-aide { margin: 0.3rem 0 0; font-size: 0.82rem; color: var(--c-texte-doux); font-variant-numeric: lining-nums; }
.annot-erreur { margin: 0.35rem 0 0; font-size: 0.95rem; color: var(--c-texte); border-left: 2px solid var(--c-texte); padding-left: 0.6rem; }
.annot-erreur[hidden] { display: none; }
.annot-message { padding: 0.3rem 0.8rem; border: 1px solid var(--c-texte-doux); font-size: 0.95rem; font-variant-numeric: lining-nums; pointer-events: none; }
.annot-liste { background: var(--c-fond); display: flex; flex-direction: column; padding: 0.8rem 1.2rem 0.6rem; border: 1px solid var(--c-filet); }
.annot-liste-titre { margin: 0 0 0.5rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--c-texte); font-variant: small-caps; letter-spacing: 0.08em; display: flex; justify-content: space-between; gap: 1rem; }
.annot-liste-titre span { color: var(--c-texte-doux); font-variant-numeric: lining-nums; }
.annot-lignes { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1 1 auto; min-height: 0; }
.annot-lignes li { display: grid; grid-template-columns: 2.2rem minmax(9rem, 19rem) 6.5rem 1fr 4.2rem; gap: 0 0.8rem; align-items: baseline; padding: 0.22rem 0.4rem; border-bottom: 1px solid var(--c-filet); border-left: 2px solid transparent; font-size: 0.98rem; line-height: 1.35; cursor: pointer; font-variant-numeric: lining-nums; }
.annot-lignes li.est-choisie { border-left-color: var(--c-texte); background: #f1efea; }
.annot-lignes li.est-traitee { color: #8a8a8a; }
.annot-lignes .annot-num { text-align: right; color: var(--c-texte-doux); }
.annot-lignes .annot-lieu, .annot-lignes .annot-cat, .annot-lignes .annot-etat { font-variant: small-caps; letter-spacing: 0.05em; color: var(--c-texte-doux); }
.annot-lignes li.est-traitee span { color: inherit; }
.annot-lignes .annot-debut { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.annot-lignes .annot-suite { grid-column: 4 / -1; font-style: italic; font-size: 0.9rem; }
.annot-vide { margin: 1rem 0; color: var(--c-texte-doux); font-style: italic; }
.annot-repere { position: absolute; top: 3px; width: 2px; height: 15px; margin-left: -1px; background: #6e6e6e; pointer-events: none; }
.annot-repere.est-traite { background: #c4c1b9; }
.annot-compteur { font: inherit; font-size: 0.95rem; margin: 0; padding: 0; min-height: 44px; color: var(--c-texte-doux); background: none; border: 0; cursor: pointer; text-decoration: underline; text-decoration-color: var(--c-filet); text-underline-offset: 3px; font-variant-numeric: lining-nums; }
`;

const base = (src: string | null | undefined) => (src ? decodeURIComponent(src.split('/').pop()!.split('?')[0]).replace(/\.[a-z0-9]+$/i, '') : null);
const secondes = (t: number) => `${t.toFixed(1).replace('.', ',')} s`;
const deux = (n: number) => String(n).padStart(2, '0');
const el = <K extends keyof HTMLElementTagNameMap>(nom: K, classe: string, texte = '') => {
  const e = document.createElement(nom);
  e.className = classe;
  if (texte) e.textContent = texte;
  return e;
};

export function installerAnnotations(lec: Lecteur) {
  if ((window as any).__sansAnnotations) return; // captures prises par le serveur : lecteur nu
  const { D, audio, lecteur, racine, sa, scene, segments, bornes } = lec;
  const API = `/__annotations/${D.slug}`;
  const CLE_SECOURS = `annotations-secours:${D.slug}`;
  if (!document.getElementById('annot-styles')) {
    const s = document.createElement('style');
    s.id = 'annot-styles';
    s.textContent = STYLES;
    document.head.append(s);
  }

  let liste: Annotation[] = [];
  let ouvert: null | 'panneau' | 'liste' = null;
  let jouait = false;                 // la lecture était en cours avant l'ouverture
  let contexte: { lieu: Lieu; ecran: Ecran } | null = null;
  let categorie: Categorie = 'autre';
  let edition: Annotation | null = null;  // annotation modifiée depuis la liste
  let brouillon: Charge | null = null;    // annotation dont l'envoi a échoué (panneau resté ouvert)
  let choisie = 0, aConfirmer = false, occupe = false;

  // --- Éléments ------------------------------------------------------------------------------
  const panneau = el('div', 'annot-panneau');
  panneau.hidden = true;
  panneau.setAttribute('role', 'dialog');
  panneau.setAttribute('aria-label', 'Annotation');
  const elContexte = el('p', 'annot-contexte');
  const elCategories = el('div', 'annot-categories');
  elCategories.setAttribute('role', 'radiogroup');
  elCategories.setAttribute('aria-label', 'Catégorie');
  const boutons = CATEGORIES.map((c, k) => {
    const b = el('button', '');
    b.type = 'button';
    b.dataset.c = c;
    b.setAttribute('role', 'radio');
    b.append(el('span', '', String(k + 1)), c);
    b.addEventListener('click', () => { choisir(c); champ.focus({ preventScroll: true }); });
    return b;
  });
  elCategories.append(...boutons);
  const champ = el('textarea', 'annot-texte');
  champ.rows = 2;
  champ.placeholder = 'Correction à faire…';
  champ.setAttribute('aria-label', 'Texte de l’annotation');
  champ.spellcheck = false;
  const elAide = el('p', 'annot-aide', 'Entrée : enregistrer et reprendre · Maj+Entrée : saut de ligne · Tab ou Alt+1…7 : catégorie (chiffre seul tant que le champ est vide) · Échap ou Ctrl+. : annuler');
  const elErreur = el('p', 'annot-erreur');
  elErreur.hidden = true;
  elErreur.setAttribute('role', 'alert');
  panneau.append(elContexte, elCategories, champ, elAide, elErreur);

  const elListe = el('div', 'annot-liste');
  elListe.hidden = true;
  elListe.setAttribute('role', 'dialog');
  elListe.setAttribute('aria-label', 'Annotations de la période');
  const elListeTitre = el('p', 'annot-liste-titre');
  const elLignes = el('ol', 'annot-lignes');
  const AIDE_LISTE = '↑ ↓ : choisir · Entrée : aller à l’instant annoté (en pause) · E : modifier · Suppr : supprimer · Échap : fermer';
  const elListeAide = el('p', 'annot-aide', AIDE_LISTE);
  elListe.append(elListeTitre, elLignes, elListeAide);

  const elMessage = el('p', 'annot-message');
  elMessage.hidden = true;
  elMessage.setAttribute('role', 'status');
  lecteur.append(panneau, elListe, elMessage);

  const compteur = el('button', 'annot-compteur');
  compteur.type = 'button';
  compteur.title = 'Liste des annotations (L) · annoter : A';
  compteur.addEventListener('click', () => { if (!ouvert) ouvrirListe(); });
  racine.querySelector('.lecteur__temps')?.after(compteur);

  /** Panneau en bas de l'image, liste sur toute l'image (au-dessus des commandes en plein écran). */
  function placer() {
    const L = lecteur.getBoundingClientRect(), S = scene.getBoundingClientRect();
    let bas = S.bottom;
    if (document.fullscreenElement === lecteur) {
      for (const e of [lec.elSt, racine.querySelector<HTMLElement>('.lecteur__progression')]) {
        const r = e?.getBoundingClientRect();
        if (r && r.height && r.top < bas) bas = r.top;
      }
    }
    for (const e of [panneau, elListe]) {
      e.style.left = `${S.left - L.left}px`;
      e.style.width = `${S.width}px`;
      e.style.bottom = `${L.bottom - bas}px`;
    }
    elListe.style.top = `${S.top - L.top}px`;
    elMessage.style.top = `${S.top - L.top + 12}px`;
    elMessage.style.right = `${L.right - S.right + 12}px`;
  }
  window.addEventListener('resize', () => { if (ouvert) placer(); });
  // Échap en plein écran : le navigateur sort du plein écran avant que la page ne voie la touche.
  // Chrome et Edge savent la laisser à la page (Keyboard Lock) : Échap annule alors la saisie ou
  // ferme la liste sans quitter le plein écran, et le quitte quand rien n'est ouvert (ci-dessous).
  // Ailleurs (Safari, Firefox), Ctrl+. ou Cmd+. annule sans toucher au plein écran.
  const verrou = (navigator as any).keyboard as { lock?: (t: string[]) => Promise<void>; unlock?: () => void } | undefined;
  document.addEventListener('fullscreenchange', () => {
    if (document.fullscreenElement) verrou?.lock?.(['Escape']).catch(() => {});
    else verrou?.unlock?.();
    if (ouvert) placer();
  });

  let minuterieMessage = 0;
  function message(texte: string, duree = 2600) {
    placer();
    elMessage.textContent = texte;
    elMessage.hidden = false;
    clearTimeout(minuterieMessage);
    minuterieMessage = window.setTimeout(() => (elMessage.hidden = true), duree);
  }

  // --- Contexte au moment de la pause -----------------------------------------------------------
  function releverContexte(): { lieu: Lieu; ecran: Ecran } {
    const x = D.diapos[lec.i], s = x.suite;
    const tg = lec.tempsCourant();
    const lieu: Lieu = { type: 'diapositive', n: x.n, acte: D.actes[lec.acteDe[lec.i]]?.titre ?? null, segment: null,
      plan: null, image_galerie: null, instant: 0, temps_global: tg };
    const ecran: Ecran = { image: null, phrase: null, sous_titre: null, surimpressions: [], camera: null, musique: null,
      fenetre: [window.innerWidth, window.innerHeight], plein_ecran: Boolean(document.fullscreenElement) };
    let img: string | null = x.img;
    const m = (racine as any).__musique?.();
    ecran.musique = m && m.musiqueOn && m.courant >= 0 ? base(m.fonds[m.courant]?.src) : null;
    const st = lecteur.classList.contains('avec-st') ? lec.elSt.querySelector('.st:not(.st--sortant)')?.textContent?.trim() || null : null;
    if (lec.enGenerique) {
      lieu.type = lec.enGenerique === 'ouverture' ? 'generique' : 'recapitulatif';
      lieu.n = null; lieu.acte = null;
      lieu.instant = lec.enGenerique === 'ouverture' ? tg : tg - (lec.total - lec.genFin);
      ecran.musique = base(D.generique?.[lec.enGenerique === 'ouverture' ? 'ouverture' : 'fin'].src);
      img = null;
    } else if (lec.enCarton) {
      lieu.type = 'carton';
      lieu.instant = Math.min(lec.chronoCarton.t, lec.prelude[lec.i]);
      img = null;
    } else if (s && (lec.enSuite || lec.suiteFini)) {
      const ts = lec.suiteFini ? s.duree : sa.currentTime || 0;
      const G = lec.galerieDe(x);
      // Intermède : « chant » s'il a des paroles, « galerie » pour une série d'images sur un extrait instrumental.
      lieu.type = s.type === 'chant' ? (s.galerie && (s.instrumental || !s.paroles.length) ? 'galerie' : 'chant') : s.type;
      lieu.segment = s.type === 'chant' ? base(s.src) : s.id;
      lieu.instant = ts;
      if (G) {
        let k = 0;
        G.forEach((p, j) => { if (ts >= p.t) k = j; });
        lieu.image_galerie = k + 1;
        img = G[k].img;
      } else if (s.type === 'episode') img = null; // panneau : pas d'image de diapositive à l'écran
      if (s.type === 'chant') {
        ecran.musique = base(s.src);
        let vers: string | null = null;
        for (const p of s.paroles) if (p[0] <= ts) vers = p[1];
        ecran.phrase = vers;
        ecran.sous_titre = lecteur.classList.contains('en-clip') ? lec.elClipTexte.textContent?.trim() || null : null;
      } else if (s.type === 'episode') {
        ecran.phrase = s.phrases.find((p) => p[0] <= ts && ts < p[1])?.[2] ?? null;
        ecran.sous_titre = ecran.phrase;
      } else {
        // Lecture : phrase en cours, relue dans les mots de la carte.
        try {
          const mots = lec.ov ? lec.etats.get(lec.ov)?.mots : null;
          let p: [number, number, number] | null = null;
          for (const q of s.phrases) if (q[0] <= ts) p = q;
          if (mots && p) ecran.phrase = mots.slice(p[1], p[2]).map((e) => e[0]?.textContent ?? '').join(' ').replace(/\s+/g, ' ').trim() || null;
        } catch { /* carte pas encore préparée */ }
      }
    } else {
      const t = lec.instant();
      lieu.instant = t;
      ecran.sous_titre = st;
      // Vue rendue : image principale (ou image après), ou plan en cours.
      let xp: Diapo = lec.principal(x);
      if (x.ap && t >= x.ap.t) { xp = lec.apresDe(x); img = x.ap.img; }
      const P = x.plans ?? [];
      let k = -1;
      P.forEach((p, j) => { if (t >= p.t) k = j; });
      if (k >= 0) {
        lieu.type = 'plan';
        lieu.plan = 'bcdefgh'[k];
        img = P[k].img;
        xp = lec.planDe(x, P[k], k + 1 < P.length ? P[k + 1].t + 0.8 : x.duree || 6);
      }
      try {
        const etapes = lec.plan(xp);
        ecran.camera = { etape: Math.max(1, etapes.filter((e) => e.t <= t).length), vue: lec.vue(xp, lec.cadreA(xp, t)).map((v) => Math.round(v * 1000) / 1000) };
      } catch { ecran.camera = null; }
      const S = ecran.surimpressions, dans = (f: { a: number; b: number } | null) => Boolean(f && f.a <= t && t < f.b);
      if (dans(x.lieu)) S.push(`lieu:${x.lieu!.nom}`);
      if (dans(x.citation)) S.push(`citation:${x.citation!.auteur}`);
      if (dans(x.portraits)) for (const g of x.portraits!.gens) if (g.t <= t) S.push(`portrait:${g.id}`);
      if (dans(x.objet)) S.push(`objet:${x.objet!.nom}`);
      if (dans(x.manuscrit)) S.push(`manuscrit:${x.manuscrit!.nom}`);
      if (dans(x.chiffre)) S.push(`chiffre:${x.chiffre!.texte}`);
      if (dans(x.dateRep)) S.push(`date:${x.dateRep!.republicain}`);
      if (x.mos) S.push('mosaique');
      if (x.ap && t >= x.ap.t) S.push('avant-apres');
    }
    if (img) {
      const chemin = decodeURIComponent(new URL(img, location.href).pathname);
      const prefixe = `/diaporamas/${D.slug}/`;
      ecran.image = { fichier: chemin.includes(prefixe) ? chemin.slice(chemin.indexOf(prefixe) + prefixe.length) : chemin };
    }
    return { lieu, ecran };
  }

  /** « diapositive 37 · 8,4 s · plan b ». */
  function ligneLieu(l: Lieu) {
    if (l.type === 'generique') return `générique d’ouverture · ${secondes(l.instant)}`;
    if (l.type === 'recapitulatif') return `récapitulatif de fin · ${secondes(l.instant)}`;
    const quoi = l.type === 'plan' ? `plan ${l.plan}` : l.type === 'diapositive' ? '' : l.type === 'episode' ? 'épisode' : l.type;
    const image = l.image_galerie && l.type !== 'plan' ? `image ${l.image_galerie}` : '';
    return [`diapositive ${l.n}`, l.type === 'diapositive' || l.type === 'plan' ? '' : quoi, secondes(l.instant), l.type === 'plan' ? quoi : image].filter(Boolean).join(' · ');
  }

  // --- Serveur ----------------------------------------------------------------------------------
  async function appeler(methode: string, chemin = '', corps?: unknown): Promise<{ annotations: Annotation[]; annotation?: Annotation }> {
    const r = await fetch(API + chemin, { method: methode, cache: 'no-store',
      headers: corps ? { 'Content-Type': 'application/json' } : undefined, body: corps ? JSON.stringify(corps) : undefined });
    const j = await r.json().catch(() => null);
    if (!r.ok || !j) throw Object.assign(new Error(j?.erreur ?? `réponse ${r.status}`), { code: r.status });
    return j;
  }
  // Copies de secours : annotations dont l'envoi a échoué, renvoyées à la tentative suivante.
  function secours(): Charge[] {
    try { const v = JSON.parse(localStorage.getItem(CLE_SECOURS) || '[]'); return Array.isArray(v) ? v : []; } catch { return []; }
  }
  function garderSecours(l: Charge[]) {
    try { l.length ? localStorage.setItem(CLE_SECOURS, JSON.stringify(l)) : localStorage.removeItem(CLE_SECOURS); } catch { /* stockage refusé */ }
  }
  /** Renvoie les copies de secours (sauf `sauf`, en cours de saisie) ; s'arrête à la première panne. */
  async function renvoyerSecours(sauf?: string) {
    for (const c of secours()) {
      if (c.id === sauf) continue;
      try { liste = (await appeler('POST', '', c)).annotations; }
      catch (e) { if (!((e as any).code >= 400 && (e as any).code < 500)) throw e; } // refusée : inutile de la garder
      garderSecours(secours().filter((y) => y.id !== c.id));
    }
  }
  async function charger() {
    try { await renvoyerSecours(brouillon?.id); liste = (await appeler('GET')).annotations; }
    catch { /* serveur arrêté : on garde la dernière liste connue */ }
    majReperes();
  }

  // --- Repères et compteur ------------------------------------------------------------------------
  const numero = (a: Annotation) => liste.findIndex((y) => y.id === a.id) + 1;
  const triees = () => [...liste].sort((a, b) => a.lieu.temps_global - b.lieu.temps_global || a.id.localeCompare(b.id));
  function texteCompteur() {
    const n = liste.length, f = liste.filter((a) => a.etat === 'traite').length, s = secours().length;
    return `${n} annotation${n > 1 ? 's' : ''}, ${f} traitée${f > 1 ? 's' : ''}${s ? ` · ${s} en attente d’envoi` : ''}`;
  }
  function majReperes() {
    racine.querySelectorAll('.annot-repere').forEach((e) => e.remove());
    for (const a of liste) {
      const t = a.lieu.temps_global;
      let k = bornes.findIndex((b) => t >= b.t0 && t < b.t1);
      if (k < 0) k = t >= lec.total ? bornes.length - 1 : 0;
      const b = bornes[k];
      const r = el('span', `annot-repere${a.etat === 'traite' ? ' est-traite' : ''}`);
      r.style.left = `${(Math.max(0, Math.min(1, (t - b.t0) / (b.t1 - b.t0))) * 100).toFixed(3)}%`;
      r.dataset.id = a.id;
      segments[k].append(r);
    }
    compteur.textContent = texteCompteur();
  }

  // --- Panneau de saisie --------------------------------------------------------------------------
  function choisir(c: Categorie) {
    categorie = c;
    boutons.forEach((b) => b.setAttribute('aria-checked', String(b.dataset.c === c)));
  }
  function montrerPanneau(titre: string, texte: string, c: Categorie) {
    ouvert = 'panneau';
    elListe.hidden = true;
    elContexte.textContent = titre;
    champ.value = texte;
    choisir(c);
    elErreur.hidden = true;
    placer();
    panneau.hidden = false;
    champ.focus({ preventScroll: true });
    champ.setSelectionRange(texte.length, texte.length);
  }
  /** Touche A : pause immédiate, contexte relevé à l'instant de la pause, panneau. */
  function ouvrirPanneau() {
    jouait = lec.joue;
    if (jouait) lec.pause();
    contexte = releverContexte();
    edition = null; brouillon = null;
    montrerPanneau(ligneLieu(contexte.lieu), '', 'autre');
  }
  /** Ferme le panneau ; reprend la lecture à l'instant de la pause si elle était en cours. */
  function fermerPanneau() {
    panneau.hidden = true;
    ouvert = null;
    brouillon = null;
    if (edition) { edition = null; return ouvrirListe(false); }
    reprendre();
  }
  function reprendre() {
    lec.btnLecture.focus({ preventScroll: true });
    if (jouait && !lec.joue) lec.demarrer();
    jouait = false;
  }
  async function enregistrer() {
    const texte = champ.value.trim();
    if (occupe) return;
    if (!texte) return fermerPanneau(); // un texte vide n'enregistre rien
    occupe = true;
    try {
      if (edition) {
        liste = (await appeler('PUT', `/${edition.id}`, { texte, categorie })).annotations;
        message(`Annotation ${numero(edition)} modifiée`);
      } else {
        if (!brouillon) {
          const d = new Date(), dec = -d.getTimezoneOffset();
          const jour = `${d.getFullYear()}${deux(d.getMonth() + 1)}${deux(d.getDate())}`, heure = `${deux(d.getHours())}${deux(d.getMinutes())}${deux(d.getSeconds())}`;
          brouillon = { ...contexte!, texte, categorie, id: `${jour}-${heure}-${String((contexte!.lieu.n ?? 0) % 1000).padStart(3, '0')}`,
            cree: `${d.getFullYear()}-${deux(d.getMonth() + 1)}-${deux(d.getDate())}T${deux(d.getHours())}:${deux(d.getMinutes())}:${deux(d.getSeconds())}${dec < 0 ? '-' : '+'}${deux(Math.floor(Math.abs(dec) / 60))}:${deux(Math.abs(dec) % 60)}` };
        }
        brouillon.texte = texte; brouillon.categorie = categorie;
        const envoi = brouillon;
        // Copie de secours d'abord : le texte survit à une panne du serveur ou à un rechargement.
        garderSecours([...secours().filter((y) => y.id !== envoi.id), envoi]);
        await renvoyerSecours(envoi.id).catch(() => {});
        const r = await appeler('POST', '', envoi);
        liste = r.annotations;
        garderSecours(secours().filter((y) => y.id !== envoi.id));
        message(`Annotation ${r.annotation ? numero(r.annotation) : liste.length} enregistrée`);
      }
      majReperes();
      fermerPanneau();
    } catch (e) {
      const refus = (e as any).code >= 400 && (e as any).code < 500;
      elErreur.textContent = refus
        ? `Annotation refusée par le serveur (${(e as Error).message}).`
        : 'Écriture impossible : le serveur d’annotation ne répond pas (relancer « npm run annoter »). Le texte est conservé dans ce navigateur ; Entrée pour réessayer, Échap pour fermer : il sera renvoyé à la prochaine annotation ou au rechargement de la page.';
      elErreur.hidden = false;
      placer();
      compteur.textContent = texteCompteur();
    } finally { occupe = false; }
  }

  // --- Liste ------------------------------------------------------------------------------------
  function rendreListe() {
    const T = triees();
    choisie = Math.max(0, Math.min(T.length - 1, choisie));
    elListeTitre.replaceChildren(`Annotations · ${(lecteur.getAttribute('aria-label') ?? D.slug).replace(/^Diaporama\s*:\s*/, '')}`, el('span', '', texteCompteur()));
    elLignes.replaceChildren(...T.map((a, k) => {
      const li = el('li', `${k === choisie ? 'est-choisie' : ''}${a.etat === 'traite' ? ' est-traitee' : ''}`);
      li.dataset.id = a.id;
      li.title = a.texte + (a.traitement ? `\n→ ${a.traitement}` : '');
      li.append(el('span', 'annot-num', String(numero(a))), el('span', 'annot-lieu', ligneLieu(a.lieu)), el('span', 'annot-cat', a.categorie),
        el('span', 'annot-debut', a.texte.replace(/\s+/g, ' ')), el('span', 'annot-etat', a.etat === 'traite' ? 'traitée' : 'à faire'));
      if (a.etat === 'traite' && a.traitement) li.append(el('span', 'annot-suite', `→ ${a.traitement}`));
      li.addEventListener('click', () => { choisie = k; allerA(a); });
      return li;
    }));
    if (!T.length) elLignes.append(el('p', 'annot-vide', 'Aucune annotation pour cette période. Touche A pendant la lecture pour en écrire une.'));
    elListeAide.textContent = aConfirmer && T[choisie]
      ? `Supprimer l’annotation ${numero(T[choisie])} ? Entrée ou O : oui · Échap ou N : non`
      : AIDE_LISTE;
    elLignes.querySelector('.est-choisie')?.scrollIntoView({ block: 'nearest' });
  }
  function ouvrirListe(neuf = true) {
    if (neuf) { jouait = lec.joue; if (jouait) lec.pause(); }
    ouvert = 'liste';
    aConfirmer = false;
    placer();
    rendreListe();
    elListe.hidden = false;
    if (neuf) charger().then(() => { if (ouvert === 'liste') rendreListe(); });
  }
  function fermerListe(reprise = true) {
    elListe.hidden = true;
    ouvert = null;
    if (reprise) reprendre(); else { jouait = false; lec.btnLecture.focus({ preventScroll: true }); }
  }
  /** Pose un lecteur audio à l'instant voulu (tout de suite, et dès que sa durée est connue). */
  function caler(a: HTMLAudioElement, t: number, puis: () => void) {
    const poser = () => { try { a.currentTime = t; } catch { /* pas encore chargé */ } puis(); };
    if (a.readyState < 1) a.addEventListener('loadedmetadata', poser, { once: true });
    poser();
  }
  /** Saute à l'instant annoté, en pause. Carton, générique et récapitulatif : à leur début. */
  function allerA(a: Annotation) {
    fermerListe(false);
    lec.deverrouillerAudio();
    if (lec.joue) lec.pause();
    const l = a.lieu, k = D.diapos.findIndex((x) => x.n === l.n);
    if (l.type === 'generique') return lec.aller(0);
    if (l.type === 'recapitulatif') return lec.aller(lec.N - 1);
    if (k < 0) return;
    if (l.type === 'carton') return lec.aller(k);
    if (l.type !== 'diapositive' && l.type !== 'plan' && D.diapos[k].suite) {
      lec.allerSuite(k);
      return caler(sa, l.instant, () => { lec.majSuite(); lec.rendre(); lec.majTemps(); });
    }
    lec.aller(k);
    if (lec.enCarton) {
      // Comme `allerSuite` : la diapositive sans son carton.
      lec.arreterMinuterie();
      lec.enCarton = false; lec.ouvre = false;
      lec.finirVolets();
      lec.chronoCarton.zero();
      lecteur.classList.remove('en-carton');
      lec.elCarton.setAttribute('aria-hidden', 'true');
      lec.entrerImage(false);
    }
    caler(audio, l.instant, () => { lec.rendre(); lec.majTemps(); });
  }
  async function supprimerChoisie() {
    const a = triees()[choisie];
    aConfirmer = false;
    if (!a || occupe) return rendreListe();
    occupe = true;
    try {
      const n = numero(a);
      liste = (await appeler('DELETE', `/${a.id}`)).annotations;
      message(`Annotation ${n} supprimée`);
    } catch { message('Suppression impossible : le serveur d’annotation ne répond pas.', 5000); }
    occupe = false;
    majReperes();
    rendreListe();
  }

  // --- Clavier ----------------------------------------------------------------------------------
  // Phase de capture sur la fenêtre : tant que le panneau ou la liste est ouvert, aucune touche
  // n'atteint les raccourcis du lecteur (espace, flèches, F, S, M, Entrée).
  window.addEventListener('keydown', (e) => {
    if (!ouvert) {
      // Échap verrouillée (voir plus haut) : hors saisie, elle quitte le plein écran comme d'habitude.
      if (e.key === 'Escape' && document.fullscreenElement && !e.repeat) { document.exitFullscreen().catch(() => {}); return; }
      if (e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
      const cible = e.target instanceof Element ? e.target : document.body;
      if (cible.closest('input:not([type="range"]), textarea, select, [contenteditable]')) return;
      if ((e.key === 'a' || e.key === 'A') && lec.lance) { e.preventDefault(); e.stopPropagation(); ouvrirPanneau(); }
      else if (e.key === 'l' || e.key === 'L') { e.preventDefault(); e.stopPropagation(); ouvrirListe(); }
      return;
    }
    e.stopPropagation();
    if (ouvert === 'panneau') {
      if (e.key === 'Escape' || ((e.ctrlKey || e.metaKey) && e.key === '.')) { e.preventDefault(); fermerPanneau(); }
      else if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); enregistrer(); }
      else if (e.key === 'Tab') {
        e.preventDefault();
        choisir(CATEGORIES[(CATEGORIES.indexOf(categorie) + (e.shiftKey ? CATEGORIES.length - 1 : 1)) % CATEGORIES.length]);
      } else if (e.altKey && /^Digit[1-7]$/.test(e.code)) { e.preventDefault(); choisir(CATEGORIES[Number(e.code.slice(5)) - 1]); }
      else if (!e.ctrlKey && !e.metaKey && !e.altKey && champ.value === '' && /^[1-7]$/.test(e.key)) { e.preventDefault(); choisir(CATEGORIES[Number(e.key) - 1]); }
      else if (document.activeElement !== champ && e.key.length === 1 && !e.ctrlKey && !e.metaKey) champ.focus({ preventScroll: true });
      return;
    }
    // Liste.
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault();
    const T = triees();
    if (aConfirmer) {
      if (e.key === 'Enter' || e.key === 'o' || e.key === 'O') supprimerChoisie();
      else if (e.key === 'Escape' || e.key === 'n' || e.key === 'N') { aConfirmer = false; rendreListe(); }
      return;
    }
    if (e.key === 'Escape' || e.key === 'l' || e.key === 'L') fermerListe();
    else if (e.key === 'ArrowDown') { choisie++; rendreListe(); }
    else if (e.key === 'ArrowUp') { choisie--; rendreListe(); }
    else if (e.key === 'Home') { choisie = 0; rendreListe(); }
    else if (e.key === 'End') { choisie = T.length - 1; rendreListe(); }
    else if (e.key === 'Enter' && T[choisie]) allerA(T[choisie]);
    else if ((e.key === 'e' || e.key === 'E') && T[choisie]) {
      edition = T[choisie];
      montrerPanneau(`Modifier l’annotation ${numero(edition)} · ${ligneLieu(edition.lieu)}`, edition.texte, edition.categorie);
    } else if ((e.key === 'Delete' || e.key === 'Backspace') && T[choisie]) { aConfirmer = true; rendreListe(); }
  }, true);

  compteur.textContent = texteCompteur();
  charger();
}
