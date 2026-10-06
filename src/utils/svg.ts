// Petits outils de mise en page partagés par les schémas SVG.

/** Largeur estimée (en px) d'un texte serif : volontairement généreuse. */
export function largeurTexte(texte: string, taille: number): number {
  return texte.length * taille * 0.55;
}

/**
 * Répartit des libellés centrés sur des abscisses en plusieurs rangées
 * pour qu'ils ne se chevauchent pas. Renvoie l'indice de rangée de chacun.
 */
export function etagerLibelles(items: { x: number; largeur: number }[], ecart = 6): number[] {
  const finRangees: number[] = [];
  return items.map(({ x, largeur }) => {
    const gauche = x - largeur / 2;
    let rang = finRangees.findIndex((fin) => fin + ecart <= gauche);
    if (rang === -1) {
      rang = finRangees.length;
      finRangees.push(0);
    }
    finRangees[rang] = x + largeur / 2;
    return rang;
  });
}

/** Cible d'un lien : une adresse ou une ancre est gardée telle quelle, un id seul devient « #id ». */
export const cibleLien = (lien: string) => (/^([#/.]|[a-z]+:)/.test(lien) ? lien : `#${lien}`);

/** Identifiant sûr pour un attribut id SVG. */
export const idSur = (s: string) => s.toLowerCase().replace(/[^a-z0-9-]/g, '-');
