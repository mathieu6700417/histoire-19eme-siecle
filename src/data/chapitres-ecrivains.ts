// Plan du parcours « Le siècle raconté par ses écrivains » : 8 chapitres,
// un par régime. Un chapitre est « écrit » dès qu'un fichier de la
// collection `ecrivains` porte son numéro ; les autres s'affichent
// grisés avec la mention « à venir ». Le numéro 0 est le prologue (avant 1789).

export interface ChapitrePrevu {
  numero: number;
  titre: string;
  periode: string;
}

export const chapitresPrevus: ChapitrePrevu[] = [
  { numero: 0, titre: 'La France avant 1789', periode: '1774-1788' },
  { numero: 1, titre: 'La Révolution', periode: '1789-1799' },
  { numero: 2, titre: 'Consulat et Empire', periode: '1799-1815' },
  { numero: 3, titre: 'La Restauration', periode: '1814-1830' },
  { numero: 4, titre: 'La monarchie de Juillet', periode: '1830-1848' },
  { numero: 5, titre: '1848 et la IIe République', periode: '1848-1852' },
  { numero: 6, titre: 'Le Second Empire', periode: '1852-1870' },
  { numero: 7, titre: "L'année terrible : guerre et Commune", periode: '1870-1871' },
  { numero: 8, titre: "La IIIe République jusqu'à 1900", periode: '1871-1900' },
];

/** Libellé court d'un chapitre : « Prologue » pour le numéro 0, « Chapitre N » sinon. */
export const libelleChapitre = (numero: number) => (numero === 0 ? 'Prologue' : `Chapitre ${numero}`);
