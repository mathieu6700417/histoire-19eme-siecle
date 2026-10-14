// Données de la leçon « Les courants politiques en France, 1789-1900 » :
// couleurs des courants, frise chronologique et arbre généalogique.
// Les noms de la frise et les cases de l'arbre mènent aux pages des courants.
import type { AreteArbre, LigneFrise, NoeudArbre, Periode, Repere } from '../types';
import { urlLecon } from '../../utils/adresses';

export interface Courant {
  id: string;
  /** Nom court (frise, arbre). */
  nom: string;
  /** Nom complet (titre de la fiche). */
  titre: string;
  couleur: string;
  /** Période d'existence (bandeau de la fiche, carte du portail). */
  periode: string;
  /** Ce que veut le courant, « en une phrase ». */
  phrase: string;
  /** Adresse de la page du courant. */
  lien: string;
}

/** Adresse de la page d'un courant (sous-page de la leçon). */
const pageCourant = (slug: string) => urlLecon('xixe', `courants-politiques/${slug}`);

// Site strictement monochrome : chaque courant reçoit une nuance de gris, distinguée
// surtout par son libellé (frise, arbre) et par le style des traits. Toutes ces nuances
// donnent un contraste ≥ 4,5:1 avec du texte blanc comme sur le fond du site (#fbfaf7) :
// de 5,3:1 (#6b6b6b) à 18:1 (#111111), vérifié par calcul.
export const courants = {
  legitimistes: {
    id: 'legitimistes',
    nom: 'Légitimistes',
    titre: 'Contre-révolutionnaires, ultras, légitimistes',
    couleur: '#1f1f1f',
    periode: '1789-1900',
    phrase: "Restaurer la monarchie traditionnelle, héréditaire et catholique, en effaçant autant que possible l'héritage de la Révolution.",
    lien: pageCourant('legitimistes'),
  },
  orleanistes: {
    id: 'orleanistes',
    nom: 'Orléanistes',
    titre: 'Monarchistes constitutionnels : doctrinaires et orléanistes',
    couleur: '#4a4a4a',
    periode: '1789-1900',
    phrase: 'Une monarchie constitutionnelle et libérale, où les élites instruites et possédantes gouvernent à travers un Parlement, dans le respect des libertés issues de 1789.',
    lien: pageCourant('orleanistes'),
  },
  bonapartistes: {
    id: 'bonapartistes',
    nom: 'Bonapartistes',
    titre: 'Bonapartistes',
    couleur: '#333333',
    periode: '1799-1900',
    phrase: "Un pouvoir fort, incarné par un chef de la famille Bonaparte, qui garantit l'ordre et les acquis de la Révolution et tient sa légitimité directement du peuple.",
    lien: pageCourant('bonapartistes'),
  },
  republicains: {
    id: 'republicains',
    nom: 'Républicains',
    titre: 'Républicains (des jacobins aux opportunistes)',
    couleur: '#5e5e5e',
    periode: '1789-1900',
    phrase: "La République : un régime sans roi, fondé sur la souveraineté du peuple, le suffrage universel et les libertés, qui forme des citoyens par l'école.",
    lien: pageCourant('republicains'),
  },
  radicaux: {
    id: 'radicaux',
    nom: 'Radicaux',
    titre: 'Radicaux',
    couleur: '#6b6b6b',
    periode: '1835-1900',
    phrase: "Appliquer jusqu'au bout le programme républicain : démocratie complète, laïcité intégrale et réformes sociales par la loi.",
    lien: pageCourant('radicaux'),
  },
  socialistes: {
    id: 'socialistes',
    nom: 'Socialistes',
    titre: 'Socialistes',
    couleur: '#404040',
    periode: '1796-1900',
    phrase: "Mettre fin à l'exploitation des travailleurs en remplaçant la concurrence et la propriété privée des moyens de production par l'association, la propriété collective ou la socialisation.",
    lien: pageCourant('socialistes'),
  },
  anarchistes: {
    id: 'anarchistes',
    nom: 'Anarchistes',
    titre: 'Anarchistes',
    couleur: '#111111',
    periode: '1840-1900',
    phrase: "Abolir l'État, et avec lui toute autorité imposée (patron, Église, armée), pour laisser place à une société de producteurs libres et associés.",
    lien: pageCourant('anarchistes'),
  },
  catholiques: {
    id: 'catholiques',
    nom: 'Catholiques',
    titre: 'Catholiques en politique',
    couleur: '#555555',
    periode: '1830-1900',
    phrase: "Défendre la place de l'Église dans la société, en particulier à l'école, en hésitant entre le refus du monde moderne et la recherche d'un accord avec la liberté, la démocratie et la question sociale.",
    lien: pageCourant('catholiques'),
  },
  nationalistes: {
    id: 'nationalistes',
    nom: 'Nationalistes',
    titre: 'Nationalistes de la fin du siècle',
    couleur: '#2a2a2a',
    periode: '1871-1900',
    phrase: "Placer la nation, son unité, son armée et sa revanche sur l'Allemagne au-dessus de tout, quitte à combattre la République parlementaire et à désigner des ennemis intérieurs.",
    lien: pageCourant('nationalistes'),
  },
} satisfies Record<string, Courant>;

/** Les neuf courants, dans l'ordre du portail et des pages. */
export const listeCourants: Courant[] = Object.values(courants);

const c = courants;

/* ------------------------------------------------------------------ */
/* Frise chronologique                                                 */
/* ------------------------------------------------------------------ */

export const reperesFrise: Repere[] = [
  { annee: 1789, libelle: 'Début de la Révolution' },
  { annee: 1792, libelle: 'Première République' },
  { annee: 1799, libelle: 'Coup d’État de Brumaire : le Consulat' },
  { annee: 1804, libelle: 'Premier Empire' },
  { annee: 1814, libelle: 'Première Restauration' },
  { annee: 1815, libelle: 'Cent-Jours, puis seconde Restauration' },
  { annee: 1830, libelle: 'Trois Glorieuses : Monarchie de Juillet' },
  { annee: 1848, libelle: 'Révolution de février : IIe République' },
  { annee: 1852, libelle: 'Second Empire' },
  { annee: 1870, libelle: 'Sedan, 4 septembre : IIIe République' },
  { annee: 1875, libelle: 'Lois constitutionnelles' },
  { annee: 1900, libelle: 'Fin de la période étudiée' },
];

export const periodesFrise: Periode[] = [
  { debut: 1789, fin: 1799, libelle: 'Révolution' },
  { debut: 1799, fin: 1814, libelle: 'Consulat et Empire', court: 'Consulat, Empire' },
  { debut: 1814, fin: 1830, libelle: 'Restauration' },
  { debut: 1830, fin: 1848, libelle: 'Monarchie de Juillet' },
  { debut: 1848, fin: 1852, libelle: 'IIe République', court: 'IIe' },
  { debut: 1852, fin: 1870, libelle: 'Second Empire' },
  { debut: 1870, fin: 1900, libelle: 'IIIe République' },
];

export const lignesFrise: LigneFrise[] = [
  {
    ...c.legitimistes,
    segments: [
      { debut: 1789, fin: 1814, statut: 'existe', libelle: 'Contre-révolution : émigrés, Vendée (1793), chouannerie' },
      { debut: 1814, fin: 1815, statut: 'existe', libelle: 'Première Restauration (1814)' },
      { debut: 1815, fin: 1816, statut: 'pouvoir', libelle: 'Terreur blanche et Chambre introuvable (1815-1816)' },
      { debut: 1816, fin: 1820, statut: 'existe', libelle: 'Ultras dans l’opposition aux ministères modérés (Richelieu, Decazes)' },
      { debut: 1820, fin: 1830, statut: 'pouvoir', libelle: 'Retour des ultras : Villèle (1821-1828), Charles X (1824), Polignac (1829-1830)' },
      { debut: 1830, fin: 1871, statut: 'existe', libelle: 'Légitimistes fidèles à la branche aînée des Bourbons ; « émigration intérieure »' },
      { debut: 1871, fin: 1900, statut: 'declin', libelle: 'Échec de la restauration (drapeau blanc, 1873), mort du comte de Chambord (1883)' },
    ],
  },
  {
    ...c.orleanistes,
    segments: [
      { debut: 1789, fin: 1792, statut: 'existe', libelle: 'Monarchiens (1789) puis Feuillants (1791) : une monarchie constitutionnelle' },
      { debut: 1814, fin: 1830, statut: 'existe', libelle: 'Doctrinaires et libéraux sous la Restauration (Royer-Collard, Guizot)' },
      { debut: 1830, fin: 1848, statut: 'pouvoir', libelle: 'Monarchie de Juillet : Louis-Philippe, Casimir Perier, Thiers, Guizot' },
      { debut: 1848, fin: 1852, statut: 'existe', libelle: 'Au sein du parti de l’Ordre (Thiers)' },
      { debut: 1852, fin: 1871, statut: 'existe', libelle: 'Opposition libérale au Second Empire' },
      { debut: 1871, fin: 1879, statut: 'pouvoir', libelle: 'Thiers (1871-1873), puis l’Ordre moral (duc de Broglie, Mac-Mahon)' },
      { debut: 1879, fin: 1900, statut: 'declin', libelle: 'Ralliement d’une partie à la République conservatrice' },
    ],
  },
  {
    ...c.bonapartistes,
    segments: [
      { debut: 1799, fin: 1814, statut: 'pouvoir', libelle: 'Consulat (1799) et Premier Empire (1804-1814)' },
      { debut: 1814, fin: 1848, statut: 'existe', libelle: 'Cent-Jours (1815), légende napoléonienne, tentatives de Louis-Napoléon (1836, 1840)' },
      { debut: 1848, fin: 1852, statut: 'pouvoir', libelle: 'Louis-Napoléon Bonaparte président (élu le 10 décembre 1848)' },
      { debut: 1852, fin: 1870, statut: 'pouvoir', libelle: 'Second Empire (1852-1870)' },
      { debut: 1870, fin: 1879, statut: 'existe', libelle: 'Parti de l’Appel au peuple (Rouher)' },
      { debut: 1879, fin: 1900, statut: 'declin', libelle: 'Mort du Prince impérial (1879) ; une partie rejoint le boulangisme' },
    ],
  },
  {
    ...c.republicains,
    segments: [
      { debut: 1789, fin: 1792, statut: 'existe', libelle: 'Patriotes et clubs ; l’idée républicaine progresse après Varennes (1791)' },
      { debut: 1792, fin: 1799, statut: 'pouvoir', libelle: 'Première République : Convention puis Directoire' },
      { debut: 1799, fin: 1830, statut: 'declin', libelle: 'Républicains surveillés et réprimés ; Charbonnerie (1821-1822)' },
      { debut: 1830, fin: 1848, statut: 'existe', libelle: 'Sociétés républicaines, insurrections de 1832 et 1834' },
      { debut: 1848, fin: 1849, statut: 'pouvoir', libelle: 'Gouvernement provisoire, républicains modérés (Lamartine, Cavaignac)' },
      { debut: 1849, fin: 1870, statut: 'existe', libelle: 'Opposition, proscription après 1851, les Cinq (1857), Gambetta' },
      { debut: 1870, fin: 1879, statut: 'existe', libelle: 'Défense nationale (1870-1871), puis conquête de la République (1876-1879)' },
      { debut: 1879, fin: 1900, statut: 'pouvoir', libelle: 'La « République des républicains » : opportunistes puis modérés' },
    ],
  },
  {
    ...c.radicaux,
    segments: [
      { debut: 1835, fin: 1852, statut: 'existe', libelle: 'Ledru-Rollin, La Réforme (1843) ; démocrates-socialistes de 1849' },
      { debut: 1869, fin: 1895, statut: 'existe', libelle: 'Programme de Belleville (1869), Clemenceau « tombeur de ministères »' },
      { debut: 1895, fin: 1896, statut: 'pouvoir', libelle: 'Premier gouvernement radical : Léon Bourgeois (1895-1896)' },
      { debut: 1896, fin: 1900, statut: 'existe', libelle: 'Défense républicaine pendant l’affaire Dreyfus ; vers le parti radical (1901)' },
    ],
  },
  {
    ...c.socialistes,
    segments: [
      { debut: 1796, fin: 1797, statut: 'existe', libelle: 'Babeuf et la conjuration des Égaux (1796)' },
      { debut: 1820, fin: 1848, statut: 'existe', libelle: 'Socialistes « utopiques » (Saint-Simon, Fourier, Cabet), Blanqui, Louis Blanc' },
      { debut: 1848, fin: 1852, statut: 'existe', libelle: 'Louis Blanc au gouvernement provisoire ; journées de Juin (1848)' },
      { debut: 1852, fin: 1864, statut: 'declin', libelle: 'Répression et exil sous l’Empire autoritaire' },
      { debut: 1864, fin: 1871, statut: 'existe', libelle: 'Première Internationale (1864), Varlin ; la Commune (1871)' },
      { debut: 1871, fin: 1879, statut: 'declin', libelle: 'Répression après la Commune' },
      { debut: 1879, fin: 1900, statut: 'existe', libelle: 'Renaissance : Guesde, possibilistes, blanquistes, allemanistes, Jaurès' },
    ],
  },
  {
    ...c.anarchistes,
    segments: [
      { debut: 1840, fin: 1865, statut: 'existe', libelle: 'Proudhon : « La propriété, c’est le vol » (1840), fédéralisme' },
      { debut: 1865, fin: 1880, statut: 'existe', libelle: 'Bakounine ; rupture avec Marx dans l’Internationale (1872)' },
      { debut: 1880, fin: 1894, statut: 'existe', libelle: 'Propagande par le fait ; attentats (1892-1894)' },
      { debut: 1894, fin: 1900, statut: 'existe', libelle: 'Lois « scélérates » ; repli vers les syndicats (Pelloutier, CGT 1895)' },
    ],
  },
  {
    ...c.catholiques,
    segments: [
      { debut: 1830, fin: 1850, statut: 'existe', libelle: 'Catholiques libéraux : Lamennais, L’Avenir (1830), Montalembert' },
      { debut: 1850, fin: 1871, statut: 'existe', libelle: 'Loi Falloux (1850) ; intransigeants (Veuillot), Syllabus (1864)' },
      { debut: 1871, fin: 1890, statut: 'existe', libelle: 'Catholicisme social (Albert de Mun, 1871) ; lutte contre les lois laïques' },
      { debut: 1890, fin: 1900, statut: 'existe', libelle: 'Rerum novarum (1891) et Ralliement (1890-1892)' },
    ],
  },
  {
    ...c.nationalistes,
    segments: [
      { debut: 1871, fin: 1882, statut: 'existe', libelle: 'Esprit de revanche après la perte de l’Alsace-Moselle (1871)' },
      { debut: 1882, fin: 1886, statut: 'existe', libelle: 'Ligue des patriotes (1882), Déroulède' },
      { debut: 1886, fin: 1889, statut: 'existe', libelle: 'Boulangisme (1886-1889) : le mouvement frôle le pouvoir sans le prendre' },
      { debut: 1889, fin: 1900, statut: 'existe', libelle: 'Drumont, Barrès ; affaire Dreyfus, Action française (1899)' },
    ],
  },
];

/* ------------------------------------------------------------------ */
/* Arbre généalogique                                                  */
/* ------------------------------------------------------------------ */

// Rangées, de haut en bas : droites, puis gauches.
// 0 légitimistes (+ intransigeants) · 1 catholiques · 2 orléanistes
// 3 bonapartistes, boulangisme, Action française · 4-5 nationalistes
// 6 républicains · 7 radicaux · 8-10 socialistes · 11 anarchistes
export const noeudsArbre: NoeudArbre[] = [
  { id: 'contre-revolution', libelle: 'Contre-révolution', annee: 1789, rangee: 0, couleur: c.legitimistes.couleur, lien: c.legitimistes.lien, detail: 'Émigrés, insurgés de Vendée et chouans ; penseurs : Maistre, Bonald.' },
  { id: 'ultras', libelle: 'Ultras', annee: 1815, rangee: 0, couleur: c.legitimistes.couleur, lien: c.legitimistes.lien, detail: 'Royalistes « plus royalistes que le roi » sous la Restauration.' },
  { id: 'legitimistes', libelle: 'Légitimistes', annee: 1830, rangee: 0, couleur: c.legitimistes.couleur, lien: c.legitimistes.lien, detail: 'Fidèles à la branche aînée des Bourbons après 1830 (comte de Chambord).' },

  { id: 'catholiques-liberaux', libelle: 'Catholiques libéraux', annee: 1830, rangee: 1, couleur: c.catholiques.couleur, lien: c.catholiques.lien, detail: 'Lamennais et L’Avenir (1830), puis Montalembert.' },
  { id: 'intransigeants', libelle: 'Intransigeants', annee: 1850, rangee: 0, couleur: c.catholiques.couleur, lien: c.catholiques.lien, detail: 'Catholiques ultramontains hostiles au libéralisme (Louis Veuillot).' },
  { id: 'catholicisme-social', libelle: 'Catholicisme social', annee: 1871, rangee: 1, couleur: c.catholiques.couleur, lien: c.catholiques.lien, detail: 'Albert de Mun et les Cercles catholiques d’ouvriers (1871).' },
  { id: 'rallies', libelle: 'Ralliés', annee: 1892, rangee: 1, couleur: c.catholiques.couleur, lien: c.catholiques.lien, detail: 'Catholiques acceptant la République à l’appel de Léon XIII (1892).' },

  { id: 'monarchiens', libelle: 'Monarchiens', annee: 1789, rangee: 2, couleur: c.orleanistes.couleur, lien: c.orleanistes.lien, detail: 'Partisans d’une monarchie à l’anglaise en 1789 (Mounier, Malouet).' },
  { id: 'doctrinaires', libelle: 'Doctrinaires', annee: 1816, rangee: 2, couleur: c.orleanistes.couleur, lien: c.orleanistes.lien, detail: 'Libéraux attachés à la Charte : Royer-Collard, Guizot, duc de Broglie.' },
  { id: 'orleanistes', libelle: 'Orléanistes', annee: 1830, rangee: 2, couleur: c.orleanistes.couleur, lien: c.orleanistes.lien, detail: 'Soutiens de Louis-Philippe et de la monarchie parlementaire.' },

  { id: 'empire', libelle: 'Napoléon Ier', annee: 1799, rangee: 3, couleur: c.bonapartistes.couleur, lien: c.bonapartistes.lien, detail: 'Consulat (1799) et Premier Empire (1804-1814).' },
  { id: 'bonapartistes', libelle: 'Bonapartistes', annee: 1815, rangee: 3, couleur: c.bonapartistes.couleur, lien: c.bonapartistes.lien, detail: 'Fidèles de la dynastie et de la légende napoléonienne ; Second Empire (1852-1870).' },
  { id: 'boulangisme', libelle: 'Boulangisme', annee: 1886, rangee: 3, couleur: c.nationalistes.couleur, lien: c.nationalistes.lien, detail: 'Mouvement autour du général Boulanger (1886-1889).' },

  { id: 'ligue-patriotes', libelle: 'Ligue des patriotes', annee: 1882, rangee: 5, couleur: c.nationalistes.couleur, lien: c.nationalistes.lien, detail: 'Ligue républicaine et revancharde fondée en 1882 (Déroulède).' },
  { id: 'action-francaise', libelle: 'Action française', annee: 1899, rangee: 3, couleur: c.nationalistes.couleur, lien: c.nationalistes.lien, detail: 'Fondée en 1899 ; Maurras la convertit au royalisme.' },
  { id: 'nationalistes', libelle: 'Nationalistes', annee: 1889, rangee: 4, couleur: c.nationalistes.couleur, lien: c.nationalistes.lien, detail: 'Nationalisme de droite : Barrès, Drumont, antidreyfusards.' },

  { id: 'jacobins', libelle: 'Jacobins', annee: 1789, rangee: 6, couleur: c.republicains.couleur, lien: c.republicains.lien, detail: 'Club des Jacobins ; Montagnards de la Convention (Robespierre).' },
  { id: 'republicains', libelle: 'Républicains', annee: 1830, rangee: 6, couleur: c.republicains.couleur, lien: c.republicains.lien, detail: 'Sociétés républicaines, 1848, opposition au Second Empire.' },
  { id: 'opportunistes', libelle: 'Opportunistes', annee: 1877, rangee: 6, couleur: c.republicains.couleur, lien: c.republicains.lien, detail: 'Républicains modérés : Gambetta, Ferry ; réformes « au moment opportun ».' },
  { id: 'radicaux', libelle: 'Radicaux', annee: 1869, rangee: 7, couleur: c.radicaux.couleur, lien: c.radicaux.lien, detail: 'Programme de Belleville (1869), Clemenceau, Pelletan.' },

  { id: 'babouvistes', libelle: 'Babouvistes', annee: 1796, rangee: 8, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Babeuf et la conjuration des Égaux (1796).' },
  { id: 'blanquistes', libelle: 'Blanquistes', annee: 1835, rangee: 8, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Révolutionnaires de complot autour de Blanqui, puis d’Édouard Vaillant.' },
  { id: 'socialistes', libelle: 'Socialistes', annee: 1864, rangee: 8, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Mouvement ouvrier de la Première Internationale (1864) et de la Commune.' },
  { id: 'guesdistes', libelle: 'Guesdistes', annee: 1879, rangee: 8, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Parti ouvrier de Jules Guesde, marxiste.' },
  { id: 'allemanistes', libelle: 'Allemanistes', annee: 1890, rangee: 10, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Scission ouvriériste des possibilistes autour de Jean Allemane (1890).' },
  { id: 'utopistes', libelle: 'Socialistes utopiques', annee: 1820, rangee: 9, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Saint-Simon, Fourier, Cabet ; puis Louis Blanc.' },
  { id: 'possibilistes', libelle: 'Possibilistes', annee: 1882, rangee: 9, couleur: c.socialistes.couleur, lien: c.socialistes.lien, detail: 'Réformistes de Paul Brousse (1882).' },

  { id: 'proudhoniens', libelle: 'Proudhoniens', annee: 1840, rangee: 11, couleur: c.anarchistes.couleur, lien: c.anarchistes.lien, detail: 'Disciples de Proudhon : mutuellisme, fédéralisme.' },
  { id: 'anarchistes', libelle: 'Anarchistes', annee: 1872, rangee: 11, couleur: c.anarchistes.couleur, lien: c.anarchistes.lien, detail: 'Rupture de Bakounine avec Marx (1872) ; propagande par le fait.' },
  { id: 'anarcho-syndicalistes', libelle: 'Anarcho-syndicalistes', annee: 1895, rangee: 11, couleur: c.anarchistes.couleur, lien: c.anarchistes.lien, detail: 'Les anarchistes investissent les syndicats : Pelloutier, CGT (1895).' },
];

export const aretesArbre: AreteArbre[] = [
  // Droite légitimiste
  { de: 'contre-revolution', vers: 'ultras', type: 'filiation' },
  { de: 'ultras', vers: 'legitimistes', type: 'filiation' },
  // Catholiques
  { de: 'catholiques-liberaux', vers: 'catholicisme-social', type: 'filiation' },
  { de: 'intransigeants', vers: 'catholicisme-social', type: 'filiation' },
  { de: 'catholicisme-social', vers: 'rallies', type: 'filiation' },
  // Monarchie constitutionnelle
  { de: 'monarchiens', vers: 'doctrinaires', type: 'filiation' },
  { de: 'doctrinaires', vers: 'orleanistes', type: 'filiation' },
  // Bonapartisme et nationalisme
  { de: 'empire', vers: 'bonapartistes', type: 'filiation' },
  { de: 'bonapartistes', vers: 'boulangisme', type: 'filiation' },
  { de: 'republicains', vers: 'ligue-patriotes', type: 'filiation' },
  { de: 'ligue-patriotes', vers: 'boulangisme', type: 'filiation' },
  { de: 'boulangisme', vers: 'nationalistes', type: 'filiation' },
  { de: 'nationalistes', vers: 'action-francaise', type: 'filiation' },
  // Républicains
  { de: 'jacobins', vers: 'republicains', type: 'filiation' },
  { de: 'republicains', vers: 'opportunistes', type: 'filiation' },
  { de: 'republicains', vers: 'radicaux', type: 'scission' },
  // Socialistes et anarchistes
  { de: 'jacobins', vers: 'babouvistes', type: 'filiation' },
  { de: 'babouvistes', vers: 'blanquistes', type: 'filiation' },
  { de: 'blanquistes', vers: 'socialistes', type: 'filiation' },
  { de: 'utopistes', vers: 'socialistes', type: 'filiation' },
  { de: 'socialistes', vers: 'guesdistes', type: 'filiation' },
  { de: 'guesdistes', vers: 'possibilistes', type: 'scission' },
  { de: 'possibilistes', vers: 'allemanistes', type: 'scission' },
  { de: 'proudhoniens', vers: 'anarchistes', type: 'filiation' },
  { de: 'socialistes', vers: 'anarchistes', type: 'scission' },
  { de: 'anarchistes', vers: 'anarcho-syndicalistes', type: 'filiation' },
];

/** Ligne(s) de la frise d'un seul courant : mini-frise de sa page. */
export const lignesDe = (id: string): LigneFrise[] => lignesFrise.filter((l) => l.id === id);

export const reperesArbre: Repere[] = reperesFrise;
