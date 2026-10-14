// Données de la leçon « L'antisémitisme en France au XIXe siècle » (spec 22) : échelle et
// bandes de la frise, repères datés, glossaire et personnages. Les ancres (`lien`, `id`) sont
// celles de la page src/content/lecons/xixe/antisemitisme.mdx : stables et lisibles, pour que de
// futures sous-pages (src/content/lecons/xixe/antisemitisme/<sous>.mdx) puissent s'y rattacher.
import type { BandeFrise, JourneeFrise, TrancheFrise } from '../types';

/** Échelle par segments : le début du siècle est comprimé, les années 1879-1906 sont détaillées. */
export const tranches: TrancheFrise[] = [
  { debut: 1789, fin: 1879, pxParAn: 10, pas: 10, libelle: 'De 1789 à 1879 : échelle comprimée (une décennie entre deux graduations)' },
  { debut: 1879, fin: 1907, pxParAn: 40, pas: 1, libelle: 'De 1879 à 1906 : une année par graduation' },
];

/** Régimes (bandes du haut). `motif` : 0 uni clair, 1 hachures, 2 points, 3 uni moyen. */
export const regimes: BandeFrise[] = [
  { debut: '1789-05-05', fin: '1799-11-10', libelle: 'Révolution', court: 'Rév.', motif: 1, dates: '1789-1799' },
  { debut: '1799-11-10', fin: '1815-06-22', libelle: 'Consulat et Empire', court: 'Empire', motif: 3, dates: '1799-1815' },
  { debut: '1815-06-22', fin: '1830-08-09', libelle: 'Restauration', court: 'Restaur.', motif: 0, dates: '1814-1830' },
  { debut: '1830-08-09', fin: '1848-02-24', libelle: 'Monarchie de Juillet', court: 'Juillet', motif: 2, dates: '1830-1848' },
  { debut: '1848-02-24', fin: '1852-12-02', libelle: 'IIe République', court: 'IIe', motif: 1, dates: '1848-1852' },
  { debut: '1852-12-02', fin: '1870-09-04', libelle: 'Second Empire', court: 'IId Empire', motif: 3, dates: '1852-1870' },
  { debut: '1870-09-04', fin: '1907-01-01', libelle: 'IIIe République', court: 'IIIe Rép.', motif: 0, dates: 'à partir de 1870' },
];

/** Parties du récit (seconde rangée). Les quatre familles (parties 2 à 5) traversent tout le
 *  siècle : elles ne forment pas de bande, la frise donne le cadre et la convergence finale. */
export const parties: BandeFrise[] = [
  { debut: '1789-05-05', fin: '1880-01-01', libelle: 'Émancipation, intégration ; les quatre familles se forment', court: 'Émancipation et familles', motif: 0, lien: '#emancipation', dates: '1789-1880' },
  { debut: '1880-01-01', fin: '1894-10-15', libelle: 'La convergence', court: 'Convergence', motif: 3, lien: '#convergence', dates: '1880-1894' },
  { debut: '1894-10-15', fin: '1899-09-20', libelle: 'L’affaire Dreyfus', court: 'L’Affaire', motif: 1, lien: '#affaire-dreyfus', dates: '1894-1899' },
  { debut: '1899-09-20', fin: '1907-01-01', libelle: 'Épilogue', court: 'Épil.', motif: 2, lien: '#epilogue', dates: '1899-1906' },
];

/** Repères datés (cliquables). `court` : libellé sur la frise ; `libelle` : détail. */
export const journees: JourneeFrise[] = [
  { date: '1790-01-28', court: '1790', libelle: '28 janvier 1790 : les Juifs « portugais, espagnols et avignonnais » deviennent citoyens actifs', lien: '#decret-1790' },
  { date: '1791-09-27', court: 'Émancipation', libelle: '27 septembre 1791 : émancipation de tous les Juifs de France', lien: '#emancipation-1791' },
  { date: '1807-02-09', court: 'Sanhédrin', libelle: 'Février-mars 1807 : le Grand Sanhédrin réuni par Napoléon', lien: '#sanhedrin' },
  { date: '1808-03-17', court: 'Consistoires', libelle: '17 mars 1808 : décrets créant les consistoires ; « décret infâme »', lien: '#consistoires' },
  { date: '1840-02-05', court: 'Damas', libelle: 'Février-août 1840 : affaire de Damas (accusation de meurtre rituel)', lien: '#affaire-de-damas' },
  { date: '1845-06-01', court: 'Toussenel', libelle: '1845 : Toussenel, Les Juifs, rois de l’époque', lien: '#toussenel' },
  { date: '1846-03-03', court: 'More judaico', libelle: '3 mars 1846 : fin du serment more judaico', lien: '#more-judaico' },
  { date: '1870-10-24', court: 'Décret Crémieux', libelle: '24 octobre 1870 : décret Crémieux, les Juifs d’Algérie deviennent citoyens français', lien: '#decret-cremieux' },
  { date: '1879-09-01', court: 'Marr', libelle: '1879 : le mot « antisémitisme » se répand en Allemagne (Wilhelm Marr)', lien: '#mot-antisemitisme' },
  { date: '1882-01-19', court: 'Union générale', libelle: 'Janvier 1882 : krach de l’Union générale', lien: '#union-generale' },
  { date: '1886-04-14', court: 'France juive', libelle: '14 avril 1886 : Drumont, La France juive', lien: '#la-france-juive' },
  { date: '1889-09-01', court: 'Ligue', libelle: '1889 : Ligue antisémitique de France (Drumont, Morès, Guérin)', lien: '#ligue-antisemitique' },
  { date: '1892-04-20', court: 'Libre Parole', libelle: '20 avril 1892 : premier numéro de La Libre Parole', lien: '#la-libre-parole' },
  { date: '1892-11-20', court: 'Panama', libelle: 'Automne 1892 : scandale de Panama', lien: '#panama' },
  { date: '1894-12-22', court: 'Condamnation', libelle: '22 décembre 1894 : Dreyfus condamné par le conseil de guerre', lien: '#condamnation-1894' },
  { date: '1895-01-05', court: 'Dégradation', libelle: '5 janvier 1895 : dégradation de Dreyfus', lien: '#degradation' },
  { date: '1898-01-13', court: 'J’accuse', libelle: '13 janvier 1898 : Zola, « J’accuse… ! » ; émeutes antisémites en France et en Algérie', lien: '#j-accuse' },
  { date: '1899-09-09', court: 'Rennes', libelle: '9 septembre 1899 : nouvelle condamnation à Rennes ; grâce le 19 septembre', lien: '#rennes' },
  { date: '1906-07-12', court: 'Réhabilitation', libelle: '12 juillet 1906 : la Cour de cassation réhabilite Dreyfus', lien: '#rehabilitation' },
];

export interface Terme { id: string; terme: string; definition: string }

/** Glossaire (ancre : #glossaire-<id>). Ordre alphabétique. */
export const glossaire: Terme[] = [
  { id: 'antidreyfusard', terme: 'Antidreyfusard', definition: 'Partisan de la culpabilité de Dreyfus ou, plus largement, adversaire de la révision de son procès au nom de l’honneur de l’armée et de l’ordre. Tous les antidreyfusards ne sont pas antisémites, mais les antisémites sont presque tous antidreyfusards.' },
  { id: 'antijudaisme', terme: 'Antijudaïsme', definition: 'Hostilité envers les Juifs fondée sur la religion : on leur reproche leur foi et la mort du Christ, et l’on attend leur conversion. Forme ancienne, surtout chrétienne, de l’hostilité aux Juifs.' },
  { id: 'antisemitisme', terme: 'Antisémitisme', definition: 'Mot apparu en Allemagne vers 1879 et vite adopté en France. Il désigne l’hostilité envers les Juifs considérés comme un groupe à part, par nature et non plus par leur foi : un juif converti reste, pour l’antisémite, un juif. Le mot est trompeur, car il n’existe pas de « Sémites » au sens racial.' },
  { id: 'aryen-semite', terme: '« Aryen » et « Sémite »', definition: 'À l’origine, termes de linguistes : il existe des langues indo-européennes (dites alors « aryennes ») et des langues sémitiques (hébreu, araméen, arabe). Au XIXe siècle, on en fait à tort des races humaines opposées. Ces « races » n’existent pas : une langue ne dit rien de l’origine biologique de ceux qui la parlent.' },
  { id: 'ashkenaze', terme: 'Ashkénaze', definition: 'Juif dont les ancêtres vivaient en Europe centrale et orientale (de l’hébreu *Ashkenaz*, « Allemagne »). En 1789, les Juifs d’Alsace et de Lorraine, de langue yiddish ou allemande, sont ashkénazes.' },
  { id: 'assimilation', terme: 'Assimilation, intégration', definition: 'Processus par lequel les Juifs, devenus citoyens, adoptent la langue, la culture et les carrières de la société française tout en gardant, pour la plupart, leur religion. Les historiens préfèrent souvent parler d’intégration.' },
  { id: 'bordereau', terme: 'Bordereau', definition: 'Lettre non signée, trouvée en septembre 1894 dans une corbeille de l’ambassade d’Allemagne, qui annonce l’envoi de documents militaires. Attribuée à tort à Dreyfus, elle était de la main d’Esterhazy.' },
  { id: 'consistoire', terme: 'Consistoire', definition: 'Organisation officielle du culte israélite créée par Napoléon (décrets du 17 mars 1808) : un consistoire central à Paris, des consistoires départementaux, composés de rabbins et de laïcs notables. Il encadre le culte et doit favoriser l’intégration.' },
  { id: 'decret-cremieux', terme: 'Décret Crémieux', definition: 'Décret du 24 octobre 1870 qui fait citoyens français, collectivement, les Juifs d’Algérie (environ 35 000 selon les estimations). Les musulmans d’Algérie, eux, restent des « sujets ». Les antisémites d’Algérie en réclameront l’abrogation.' },
  { id: 'decret-infame', terme: '« Décret infâme »', definition: 'Nom donné par les Juifs au décret du 17 mars 1808 qui, pour dix ans, restreint leur droit de commercer, de prêter et de s’installer, surtout en Alsace. Il n’est pas renouvelé en 1818.' },
  { id: 'deicide', terme: '« Peuple déicide »', definition: 'Accusation chrétienne ancienne selon laquelle le peuple juif tout entier, et ses descendants, porteraient la responsabilité de la mort du Christ. L’Église catholique ne la rejettera officiellement qu’au XXe siècle.' },
  { id: 'dreyfusard', terme: 'Dreyfusard', definition: 'Partisan de l’innocence de Dreyfus et de la révision de son procès, au nom de la justice et des droits de l’individu. Beaucoup de dreyfusards deviennent aussi des adversaires déclarés de l’antisémitisme.' },
  { id: 'emancipation', terme: 'Émancipation', definition: 'Octroi aux Juifs des mêmes droits civils et politiques qu’aux autres habitants. La France est le premier grand État d’Europe à le faire (décrets de 1790 et 1791).' },
  { id: 'franco-judaisme', terme: 'Franco-judaïsme', definition: 'Terme d’historiens pour désigner l’attachement des israélites français du XIXe siècle à la fois à leur religion et à la France de 1789, qui les a émancipés : patriotisme, foi en l’école et en la République.' },
  { id: 'grand-sanhedrin', terme: 'Grand Sanhédrin', definition: 'Assemblée de rabbins et de laïcs réunie à Paris par Napoléon en février-mars 1807, du nom de l’ancien tribunal suprême d’Israël. Elle donne une valeur religieuse aux réponses de l’Assemblée des notables : la loi de l’État prime en matière civile.' },
  { id: 'israelite', terme: 'Israélite', definition: 'Terme employé de préférence à « juif » par les Juifs français eux-mêmes et par l’administration au XIXe siècle, pour désigner une appartenance religieuse et non une nation à part.' },
  { id: 'judeophobie', terme: 'Judéophobie', definition: 'Terme général, employé par certains historiens, qui englobe toutes les formes d’hostilité envers les Juifs, religieuses ou modernes, sans préjuger de leurs différences.' },
  { id: 'ligue', terme: 'Ligue', definition: 'Association politique qui mobilise des militants hors des partis et du Parlement, souvent dans la rue : Ligue des patriotes (1882), Ligue antisémitique (1889, refondée en 1897), Ligue de la patrie française et Ligue des droits de l’homme (1898).' },
  { id: 'meurtre-rituel', terme: 'Meurtre rituel', definition: 'Accusation mensongère, née dans l’Angleterre du XIIe siècle, selon laquelle les Juifs tueraient des chrétiens, surtout des enfants, pour utiliser leur sang dans des rites. Plusieurs papes l’ont condamnée ; elle a pourtant causé de nombreux massacres.' },
  { id: 'more-judaico', terme: 'Serment *more judaico*', definition: 'Serment « à la manière juive » imposé aux Juifs devant les tribunaux, dans une synagogue et avec des formules humiliantes. La Cour de cassation le déclare contraire à l’égalité le 3 mars 1846, après un long combat d’Adolphe Crémieux.' },
  { id: 'nationalisme', terme: 'Nationalisme', definition: 'À la fin du XIXe siècle, doctrine qui place la nation au-dessus de tout et la définit par la terre, les morts et l’hérédité ; elle cherche des ennemis intérieurs (Juifs, protestants, francs-maçons, étrangers).' },
  { id: 'revision', terme: 'Révision', definition: 'Réexamen d’un procès par la Cour de cassation quand un fait nouveau fait douter de la culpabilité d’un condamné. Le procès de Dreyfus est révisé en 1899, et le jugement de Rennes cassé en 1906.' },
  { id: 'sefarade', terme: 'Séfarade', definition: 'Juif dont les ancêtres vivaient dans la péninsule Ibérique (de l’hébreu *Sefarad*, « Espagne ») avant les expulsions de la fin du XVe siècle. En 1789, ce sont les Juifs « portugais » de Bordeaux et de Bayonne.' },
  { id: 'theorie-du-complot', terme: 'Théorie du complot', definition: 'Explication des malheurs d’une société par l’action cachée d’un petit groupe tout-puissant. Elle est invérifiable par construction : chaque démenti devient une preuve de plus de la ruse des « comploteurs ».' },
];

export interface Personnage { id: string; nom: string; dates: string; role: string }

/** Personnages, dans l'ordre de leur entrée en scène. */
export const personnages: Personnage[] = [
  { id: 'gregoire', nom: 'L’abbé Grégoire', dates: '1750-1831', role: 'Curé lorrain, député du clergé aux états généraux. Son *Essai sur la régénération physique, morale et politique des Juifs* (1789) plaide pour leur égalité, tout en espérant leur « régénération » et, à terme, leur conversion. Il défend aussi l’abolition de l’esclavage.' },
  { id: 'clermont-tonnerre', nom: 'Stanislas de Clermont-Tonnerre', dates: '1757-1792', role: 'Noble libéral, député de la noblesse de Paris. Le 23 décembre 1789, il défend les droits des non-catholiques, des comédiens et des Juifs. Monarchien, il est tué par la foule le 10 août 1792.' },
  { id: 'cremieux', nom: 'Adolphe Crémieux', dates: '1796-1880', role: 'Avocat né à Nîmes, figure du franco-judaïsme. Il obtient la fin du serment *more judaico* (1846), intervient dans l’affaire de Damas (1840), est ministre de la Justice en 1848 et en 1870 (décret Crémieux), président de l’Alliance israélite universelle.' },
  { id: 'rothschild', nom: 'James de Rothschild', dates: '1792-1868', role: 'Banquier né à Francfort, installé à Paris en 1812. Prêteur des gouvernements de la Restauration et de la monarchie de Juillet, financier des chemins de fer, il devient pour ses ennemis le symbole de la « féodalité financière ».' },
  { id: 'toussenel', nom: 'Alphonse Toussenel', dates: '1803-1885', role: 'Disciple de Fourier, journaliste à *La Démocratie pacifique*, auteur de livres sur les animaux. *Les Juifs, rois de l’époque* (1845) confond le Juif et le financier et fait de l’hostilité aux Juifs une arme contre le capitalisme.' },
  { id: 'gobineau', nom: 'Arthur de Gobineau', dates: '1816-1882', role: 'Diplomate et écrivain. Son *Essai sur l’inégalité des races humaines* (1853-1855) explique le déclin des civilisations par le mélange des races. Il n’est pas d’abord antisémite, mais son vocabulaire racial sera repris par les antisémites.' },
  { id: 'renan', nom: 'Ernest Renan', dates: '1823-1892', role: 'Philologue et historien des religions, auteur de la *Vie de Jésus* (1863). Il oppose les « Sémites » et les « Indo-Européens » en 1855, puis récuse en 1883, dans une conférence, l’idée d’une « race juive ».' },
  { id: 'drumont', nom: 'Édouard Drumont', dates: '1844-1917', role: 'Journaliste catholique, auteur de *La France juive* (1886), immense succès, fondateur de la Ligue antisémitique (1889) et du quotidien *La Libre Parole* (1892). Député d’Alger de 1898 à 1902.' },
  { id: 'mores', nom: 'Le marquis de Morès', dates: '1858-1896', role: 'Aventurier, ancien officier, éleveur au Dakota. Cofondateur de la Ligue antisémitique, il mène des bandes de bouchers de La Villette ; il tue en duel le capitaine juif Armand Mayer (1892). Il est assassiné en 1896 dans le Sud tunisien.' },
  { id: 'guerin', nom: 'Jules Guérin', dates: '1860-1910', role: 'Militant antisémite, refondateur de la Ligue antisémitique en 1897, financé en partie par des royalistes. En 1899, il s’enferme plusieurs semaines rue de Chabrol à Paris pour échapper à l’arrestation (« Fort Chabrol »).' },
  { id: 'regis', nom: 'Max Régis', dates: '1873-1950', role: 'Étudiant puis agitateur antisémite à Alger, meneur des émeutes de janvier 1898, élu maire d’Alger la même année. Il fait venir Drumont, élu député d’Alger en mai 1898.' },
  { id: 'barres', nom: 'Maurice Barrès', dates: '1862-1923', role: 'Écrivain lorrain, élu député boulangiste de Nancy en 1889, théoricien du nationalisme (« la terre et les morts »). Antidreyfusard, il fait de la « race » l’explication de la trahison supposée de Dreyfus.' },
  { id: 'dreyfus', nom: 'Alfred Dreyfus', dates: '1859-1935', role: 'Officier d’artillerie né à Mulhouse dans une famille juive alsacienne qui a choisi la France en 1871. Condamné à tort pour trahison (1894, 1899), déporté à l’île du Diable, gracié en 1899, réhabilité en 1906. Il sert pendant la Grande Guerre.' },
  { id: 'lazare', nom: 'Bernard Lazare', dates: '1865-1903', role: 'Écrivain et journaliste né à Nîmes. Après un livre ambigu sur *L’Antisémitisme* (1894), il est le premier à publier la défense de Dreyfus (*Une erreur judiciaire*, novembre 1896) et devient un adversaire résolu de l’antisémitisme.' },
  { id: 'picquart', nom: 'Georges Picquart', dates: '1854-1914', role: 'Chef du service de renseignements de l’armée en 1895-1896. Il découvre qu’Esterhazy est l’auteur du bordereau ; on l’écarte, puis on l’emprisonne. Peu suspect de sympathie pour les Juifs, il choisit la vérité. Ministre de la Guerre en 1906.' },
  { id: 'esterhazy', nom: 'Ferdinand Walsin Esterhazy', dates: '1847-1923', role: 'Officier criblé de dettes, véritable auteur du bordereau. Acquitté par un conseil de guerre le 11 janvier 1898, il s’enfuit en Angleterre en septembre 1898 et reconnaît ensuite avoir écrit le document.' },
  { id: 'zola', nom: 'Émile Zola', dates: '1840-1902', role: 'Romancier des *Rougon-Macquart*. Il dénonce l’antisémitisme dès 1896 (« Pour les Juifs ») et publie « J’accuse… ! » le 13 janvier 1898 ; condamné pour diffamation, il s’exile en Angleterre (1898-1899).' },
  { id: 'jaures', nom: 'Jean Jaurès', dates: '1859-1914', role: 'Professeur de philosophie, député socialiste de Carmaux. D’abord réticent, il s’engage pour Dreyfus en 1898 et publie *Les Preuves* dans *La Petite République* ; il entraîne une partie des socialistes dans le camp dreyfusard.' },
  { id: 'leroy-beaulieu', nom: 'Anatole Leroy-Beaulieu', dates: '1842-1912', role: 'Historien et catholique libéral, professeur à l’École libre des sciences politiques. Dans *Israël chez les nations* (1893) et des conférences sur *L’Antisémitisme* (1897), il réfute les thèses antisémites au nom du christianisme et des principes de 1789.' },
];
