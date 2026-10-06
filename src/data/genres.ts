// Genres des extraits de la section « Le siècle raconté par ses écrivains ».
// Chaque extrait affiche son genre en petites capitales grises (site monochrome).

export interface Genre {
  id: string;
  libelle: string;
}

export const genres = {
  temoignage: { id: 'temoignage', libelle: 'Témoignage' },
  roman: { id: 'roman', libelle: 'Roman (fiction)' },
  theatre: { id: 'theatre', libelle: 'Théâtre' },
  poesie: { id: 'poesie', libelle: 'Poésie' },
  presse: { id: 'presse', libelle: 'Presse / discours' },
  // Deux genres ajoutés à la liste de la spec pour ne pas classer à tort
  // un historien parmi les témoins, ni un essai parmi les discours.
  histoire: { id: 'histoire', libelle: 'Récit historique' },
  essai: { id: 'essai', libelle: 'Essai' },
} as const satisfies Record<string, Genre>;

export type IdGenre = keyof typeof genres;
