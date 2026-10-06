// Libellés des thèmes, dans l'ordre d'affichage sur la page d'accueil.
export const themes = [
  { id: 'politique', libelle: 'Vie politique' },
  { id: 'societe', libelle: 'Société' },
  { id: 'economie', libelle: 'Économie' },
  { id: 'culture', libelle: 'Culture et idées' },
  { id: 'international', libelle: 'La France et le monde' },
  { id: 'sciences', libelle: 'Sciences et techniques' },
] as const;

export const libelleTheme = (id: string) => themes.find((t) => t.id === id)?.libelle ?? id;
