// Artistes des œuvres qui illustrent la section « Le siècle raconté par ses écrivains »
// (composant Oeuvre.astro, spec 11). Séparé de `auteurs.ts` : l'index des auteurs ne
// liste pas les peintres. La date de naissance décide du statut « témoin » de l'œuvre
// (artiste né au moins 10 ans avant les faits représentés), comme pour les extraits.
//
// Pour un nouveau chapitre : ajouter les artistes ici (id sans accent, en minuscules).
// Dates incertaines : mettre l'année la plus probable dans `naissance.annee` et la
// forme prudente à afficher dans `dates` (« vers 1745-1818 », « 1738-après 1780 »).

export interface Artiste {
  id: string;
  /** Nom complet, tel qu'affiché dans la notice. */
  nom: string;
  naissance: { annee: number };
  mort?: { annee: number };
  /** Dates affichées si elles diffèrent de « naissance-mort » (dates incertaines). */
  dates?: string;
}

const liste: Artiste[] = [
  // Prologue
  { id: 'hubert-robert', nom: 'Hubert Robert', naissance: { annee: 1733 }, mort: { annee: 1808 } },
  { id: 'chasseriau', nom: 'Théodore Chassériau', naissance: { annee: 1819 }, mort: { annee: 1856 } },
  { id: 'lemonnier', nom: 'Anicet-Charles-Gabriel Lemonnier', naissance: { annee: 1743 }, mort: { annee: 1824 } },
  { id: 'saint-quentin', nom: 'Jacques-Philippe-Joseph de Saint-Quentin', naissance: { annee: 1738 }, dates: '1738-après 1780' },
  { id: 'cochin', nom: 'Charles-Nicolas Cochin', naissance: { annee: 1715 }, mort: { annee: 1790 } },
  { id: 'van-loo', nom: 'Louis-Michel van Loo', naissance: { annee: 1707 }, mort: { annee: 1771 } },
  { id: 'houdon', nom: 'Jean-Antoine Houdon', naissance: { annee: 1741 }, mort: { annee: 1828 } },
  { id: 'vigee-le-brun', nom: 'Élisabeth Vigée Le Brun', naissance: { annee: 1755 }, mort: { annee: 1842 } },
  { id: 'callet', nom: 'Antoine-François Callet', naissance: { annee: 1741 }, mort: { annee: 1823 } },
  // Chapitre 1
  { id: 'houel', nom: 'Jean-Pierre Houël', naissance: { annee: 1735 }, mort: { annee: 1813 } },
  { id: 'bertaux', nom: 'Jacques Bertaux', naissance: { annee: 1741 }, mort: { annee: 1813 } },
  { id: 'horace-vernet', nom: 'Horace Vernet', naissance: { annee: 1789 }, mort: { annee: 1863 } },
  { id: 'swebach', nom: 'Jacques-François Swebach-Desfontaines', naissance: { annee: 1769 }, mort: { annee: 1823 } },
  { id: 'guerin', nom: 'Pierre-Narcisse Guérin', naissance: { annee: 1774 }, mort: { annee: 1833 } },
  { id: 'david', nom: 'Jacques-Louis David', naissance: { annee: 1748 }, mort: { annee: 1825 } },
  { id: 'muller', nom: 'Charles-Louis Müller', naissance: { annee: 1815 }, mort: { annee: 1892 } },
  { id: 'carle-vernet', nom: 'Carle Vernet', naissance: { annee: 1758 }, mort: { annee: 1836 } },
  { id: 'gros', nom: 'Antoine-Jean Gros', naissance: { annee: 1771 }, mort: { annee: 1835 } },
  // Chapitre 2
  { id: 'zix', nom: 'Benjamin Zix', naissance: { annee: 1772 }, mort: { annee: 1811 } },
  { id: 'gillray', nom: 'James Gillray', naissance: { annee: 1756 }, mort: { annee: 1815 } },
  { id: 'meissonier', nom: 'Ernest Meissonier', naissance: { annee: 1815 }, mort: { annee: 1891 } },
  { id: 'boilly', nom: 'Louis-Léopold Boilly', naissance: { annee: 1761 }, mort: { annee: 1845 } },
  { id: 'charlet', nom: 'Nicolas-Toussaint Charlet', naissance: { annee: 1792 }, mort: { annee: 1845 } },
  { id: 'rowlandson', nom: 'Thomas Rowlandson', naissance: { annee: 1757 }, mort: { annee: 1827 } },
  { id: 'georgin', nom: 'François Georgin', naissance: { annee: 1801 }, mort: { annee: 1863 } },
  // Chapitre 3
  { id: 'opiz', nom: 'Georg Emanuel Opiz', naissance: { annee: 1775 }, mort: { annee: 1841 } },
  { id: 'gericault', nom: 'Théodore Géricault', naissance: { annee: 1791 }, mort: { annee: 1824 } },
  { id: 'coeure', nom: 'Sébastien Coeuré', naissance: { annee: 1786 }, mort: { annee: 1867 } },
  { id: 'achille-deveria', nom: 'Achille Devéria', naissance: { annee: 1800 }, mort: { annee: 1857 } },
  { id: 'delacroix', nom: 'Eugène Delacroix', naissance: { annee: 1798 }, mort: { annee: 1863 } },
  { id: 'besnard', nom: 'Albert Besnard', naissance: { annee: 1849 }, mort: { annee: 1934 } },
  { id: 'gerard', nom: 'François Gérard', naissance: { annee: 1770 }, mort: { annee: 1837 } },
  { id: 'lecomte', nom: 'Hippolyte Lecomte', naissance: { annee: 1781 }, mort: { annee: 1857 } },
  // Chapitres 4 et 5
  { id: 'daumier', nom: 'Honoré Daumier', naissance: { annee: 1808 }, mort: { annee: 1879 } },
  { id: 'philipon', nom: 'Charles Philipon', naissance: { annee: 1800 }, mort: { annee: 1862 } },
  { id: 'mouchot', nom: 'Ludovic Mouchot', naissance: { annee: 1846 }, mort: { annee: 1893 } },
  { id: 'louis-auguste-bisson', nom: 'Louis-Auguste Bisson', naissance: { annee: 1814 }, mort: { annee: 1876 } },
  { id: 'jeanron', nom: 'Philippe-Auguste Jeanron', naissance: { annee: 1809 }, mort: { annee: 1877 } },
  { id: 'philippe-benoist', nom: 'Philippe Benoist', naissance: { annee: 1813 }, mort: { annee: 1905 } },
  { id: 'janet-lange', nom: 'Janet-Lange', naissance: { annee: 1815 }, mort: { annee: 1872 } },
  { id: 'philippoteaux', nom: 'Henri Félix Emmanuel Philippoteaux', naissance: { annee: 1815 }, mort: { annee: 1884 } },
  { id: 'sorrieu', nom: 'Frédéric Sorrieu', naissance: { annee: 1807 } },
  { id: 'vogel', nom: 'Hermann Vogel', naissance: { annee: 1856 }, mort: { annee: 1918 } },
  { id: 'vierge', nom: 'Daniel Vierge', naissance: { annee: 1851 }, mort: { annee: 1904 } },
];

export const artistes: Record<string, Artiste> = Object.fromEntries(liste.map((a) => [a.id, a]));

/** Artiste par identifiant ; erreur de build si l'identifiant est inconnu. */
export function artiste(id: string): Artiste {
  const a = artistes[id];
  if (!a) throw new Error(`Artiste inconnu : ${id} (ajouter une entrée dans src/data/artistes.ts)`);
  return a;
}

/** Dates affichées : « 1748-1825 », ou la forme prudente donnée dans `dates`. */
export const datesArtiste = (a: Artiste) => a.dates ?? (a.mort ? `${a.naissance.annee}-${a.mort.annee}` : `né en ${a.naissance.annee}`);
