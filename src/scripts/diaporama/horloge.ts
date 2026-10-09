// Horloges : `maintenant`, chronomètre figeable (carton, entrée d'image) et horloge lissée qui
// suit `audio.currentTime` sans à-coups. Les captures (scripts/diaporamas/captures.py) remplacent
// performance.now et l'audio par une horloge factice. Spec 12, « Sans bordures… » (2026-10-08).
export const maintenant = () => performance.now() / 1000;

/** Chronomètre qu'on peut figer et relancer (carton d'acte ; entrée d'une image). */
export class Chrono {
  ecoule = 0; depuis = 0; // `depuis` : instant de la dernière relance (0 = figé)
  get t() { return this.ecoule + (this.depuis ? maintenant() - this.depuis : 0); }
  get tourne() { return this.depuis > 0; }
  zero() { this.ecoule = 0; this.depuis = 0; }
  relancer() { if (!this.depuis) this.depuis = maintenant(); }
  figer() { if (this.depuis) { this.ecoule += maintenant() - this.depuis; this.depuis = 0; } }
}

/** Horloge lissée (spec 12, « Sans bordures… », 2026-10-08) : `audio.currentTime` avance par
 *  crans irréguliers (mises à jour du moteur audio, ~10 à 250 ms), d'où une caméra saccadée. Entre
 *  deux mises à jour, l'instant avance avec l'horloge de l'écran (`performance.now()` ×
 *  `playbackRate`) ; l'écart à l'audio est rattrapé en douceur en modulant la vitesse (±5 % au
 *  plus), sans jamais reculer ni sauter. En pause, à l'arrêt ou après un saut (écart de plus de
 *  0,3 s), l'instant est celui de l'audio, exactement. */
export class HorlogeLissee {
  t = 0; brut = -1; p = 0; src = ''; ecart = 0; v = 1; jouait = false; parti = false;
  /** Instant de l'image en cours (horodatage de requestAnimationFrame, s) : la caméra avance
   *  alors d'exactement une image par image affichée, quel que soit le moment du calcul. */
  image = 0;
  lire(a: HTMLAudioElement) {
    const perf = performance.now() / 1000;
    const brut = a.currentTime || 0, r = a.playbackRate || 1;
    const now = this.image && Math.abs(perf - this.image) < 0.1 ? this.image : perf;
    const joue = !a.paused && !a.ended && !a.seeking;
    if (!joue || !this.jouait || a.src !== this.src || now - this.p > 0.25 || Math.abs(brut - this.t) > 0.3) {
      this.t = brut; this.ecart = 0; this.v = r; this.parti = false;
    } else if (!this.parti) {
      // L'audio n'a pas encore avancé depuis le départ (latence de démarrage) : on l'attend.
      this.t = brut;
      this.parti = brut !== this.brut;
    } else {
      this.t += Math.min(0.1, Math.max(0, now - this.p)) * this.v;
      if (brut !== this.brut) {
        // Nouvelle valeur de l'audio : écart filtré (la valeur lue a quelques ms de retard,
        // variables), puis vitesse corrigée pour le résorber en ~1 s.
        this.ecart += 0.25 * (brut - this.t - this.ecart);
        this.v = r * (1 + Math.max(-0.05, Math.min(0.05, this.ecart)));
      }
    }
    this.brut = brut; this.p = now; this.src = a.src; this.jouait = joue;
    return this.t;
  }
}
