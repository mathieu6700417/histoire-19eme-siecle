// Données centralisées des auteurs cités dans la section
// « Le siècle raconté par ses écrivains ». Une entrée par auteur,
// réutilisée par les fiches (première apparition dans un chapitre)
// et par l'index des auteurs. Pour un nouveau chapitre : ajouter les
// nouveaux auteurs ici, et compléter `oeuvres` pour les auteurs déjà présents.
import { courants } from './courants-politiques';

export interface Auteur {
  id: string;
  /** Nom complet, tel qu'affiché en titre de fiche. */
  nom: string;
  /** Nom court utilisé dans les références (« Chateaubriand »). */
  court: string;
  /** Clé de tri alphabétique (nom de famille). */
  tri: string;
  naissance: { annee: number; lieu: string };
  mort: { annee: number; lieu: string };
  /** Position politique, en quelques mots. */
  position: string;
  /** Couleur d'accent, reprise de la famille politique la plus proche. */
  couleur: string;
  /** Œuvres citées dans la section, avec leur date de publication. */
  oeuvres: string[];
  /** Mini-portrait : 2-3 phrases. */
  portrait: string;
  /**
   * Mention affichée sur la fiche quand l'auteur relève d'une exception à la règle
   * « écrivains ayant vécu au XIXe siècle » (prologue : auteurs morts avant 1800).
   */
  exception?: string;
}

const c = courants;

const liste: Auteur[] = [
  {
    id: 'chateaubriand',
    nom: 'François-René de Chateaubriand',
    court: 'Chateaubriand',
    tri: 'Chateaubriand',
    naissance: { annee: 1768, lieu: 'Saint-Malo' },
    mort: { annee: 1848, lieu: 'Paris' },
    position: 'Royaliste, attaché aux libertés ; fidèle à la branche aînée des Bourbons après 1830',
    couleur: c.legitimistes.couleur,
    oeuvres: ["Mémoires d'outre-tombe (écrits de 1809 à 1841, publiés en 1848-1850)", 'De Buonaparte et des Bourbons (1814)', "De la guerre d'Espagne (1823)", 'Génie du christianisme (1802)'],
    portrait:
      "Cadet d'une famille noble bretonne, il émigre en 1792, combat dans l'armée des princes puis vit en exil à Londres. Célèbre avec le Génie du christianisme (1802), il rompt avec Napoléon en 1804, devient ministre des Affaires étrangères sous la Restauration et refuse de servir Louis-Philippe en 1830. Ses Mémoires d'outre-tombe ne devaient paraître qu'après sa mort.",
  },
  {
    id: 'michelet',
    nom: 'Jules Michelet',
    court: 'Michelet',
    tri: 'Michelet',
    naissance: { annee: 1798, lieu: 'Paris' },
    mort: { annee: 1874, lieu: 'Hyères' },
    position: 'Républicain',
    couleur: c.republicains.couleur,
    oeuvres: ['Histoire de la Révolution française (1847-1853)'],
    portrait:
      "Fils d'un petit imprimeur parisien, il devient professeur au Collège de France et dirige la section historique des Archives nationales. Son Histoire de la Révolution française fait du peuple le véritable héros de la Révolution. Hostile au Second Empire, il perd ses fonctions officielles après le coup d'État de 1851.",
  },
  {
    id: 'lamartine',
    nom: 'Alphonse de Lamartine',
    court: 'Lamartine',
    tri: 'Lamartine',
    naissance: { annee: 1790, lieu: 'Mâcon' },
    mort: { annee: 1869, lieu: 'Paris' },
    position: "Né dans une famille royaliste, devenu républicain modéré",
    couleur: c.republicains.couleur,
    oeuvres: ['Histoire des Girondins (1847)', 'Méditations poétiques (1820)', 'Nouvelles Méditations poétiques (1823)'],
    portrait:
      "Poète romantique révélé par les Méditations poétiques (1820), il devient député sous la monarchie de Juillet et glisse du libéralisme à la république. Son Histoire des Girondins connaît un immense succès à la veille de la révolution de 1848, dont il est l'une des grandes figures au sein du Gouvernement provisoire.",
  },
  {
    id: 'hugo',
    nom: 'Victor Hugo',
    court: 'Hugo',
    tri: 'Hugo',
    naissance: { annee: 1802, lieu: 'Besançon' },
    mort: { annee: 1885, lieu: 'Paris' },
    position: 'Royaliste dans sa jeunesse, républicain à partir de la IIe République',
    couleur: c.republicains.couleur,
    oeuvres: ['Les Châtiments (1853)', 'Quatrevingt-treize (1874)', 'Odes et Ballades (1822-1828)', 'Préface de Cromwell (1827)', 'Les Chants du crépuscule (1835)', 'Les Misérables (1862)'],
    portrait:
      "Chef de file du romantisme, pair de France sous Louis-Philippe, il devient républicain sous la IIe République. Opposant au coup d'État de Louis-Napoléon Bonaparte, il vit en exil de 1851 à 1870, à Jersey puis à Guernesey. À sa mort, la IIIe République lui fait des funérailles nationales.",
  },
  {
    id: 'mercier',
    nom: 'Louis-Sébastien Mercier',
    court: 'Mercier',
    tri: 'Mercier',
    naissance: { annee: 1740, lieu: 'Paris' },
    mort: { annee: 1814, lieu: 'Paris' },
    position: 'Républicain modéré, proche des Girondins',
    couleur: c.republicains.couleur,
    oeuvres: ['Le Nouveau Paris (1798)'],
    portrait:
      "Auteur à succès du Tableau de Paris (1781-1788), il accueille la Révolution avec enthousiasme et devient député à la Convention. Il refuse de voter la mort du roi, est emprisonné pendant la Terreur, puis siège au Conseil des Cinq-Cents sous le Directoire. Mort en 1814, il a vu les quatorze premières années du XIXe siècle.",
  },
  {
    id: 'la-rochejaquelein',
    nom: 'Victoire de Donnissan, marquise de La Rochejaquelein',
    court: 'Mme de La Rochejaquelein',
    tri: 'La Rochejaquelein',
    naissance: { annee: 1772, lieu: 'Versailles' },
    mort: { annee: 1857, lieu: 'Orléans' },
    position: 'Royaliste, dans le camp des insurgés vendéens',
    couleur: c.legitimistes.couleur,
    oeuvres: ['Mémoires (commencés vers 1798-1799, publiés en 1815)'],
    portrait:
      "Issue d'une famille de la cour, elle épouse en 1791 Louis de Lescure, l'un des futurs chefs vendéens, mort de ses blessures en novembre 1793. Elle suit l'armée vendéenne jusqu'à sa déroute, survit cachée, puis épouse en 1802 Louis de La Rochejaquelein, frère du général Henri. Ses Mémoires sont devenus le grand récit royaliste de la guerre de Vendée.",
  },
  {
    id: 'maistre',
    nom: 'Joseph de Maistre',
    court: 'Maistre',
    tri: 'Maistre',
    naissance: { annee: 1753, lieu: 'Chambéry' },
    mort: { annee: 1821, lieu: 'Turin' },
    position: 'Contre-révolutionnaire',
    couleur: c.legitimistes.couleur,
    oeuvres: ['Considérations sur la France (1797)'],
    portrait:
      "Magistrat savoyard, sujet du roi de Sardaigne et non du roi de France, il fuit l'invasion française de la Savoie en 1792 et s'installe à Lausanne. Ses Considérations sur la France font de lui le maître à penser de la contre-révolution. Il représente ensuite le roi de Sardaigne à Saint-Pétersbourg (1803-1817).",
  },
  {
    id: 'stael',
    nom: 'Germaine de Staël',
    court: 'Mme de Staël',
    tri: 'Staël',
    naissance: { annee: 1766, lieu: 'Paris' },
    mort: { annee: 1817, lieu: 'Paris' },
    position: "Libérale : monarchie constitutionnelle, puis république modérée",
    couleur: c.orleanistes.couleur,
    oeuvres: ['Considérations sur les principaux événements de la Révolution française (1818, posthume)', 'De l\'Allemagne (imprimé en 1810, publié en 1813)'],
    portrait:
      "Fille de Jacques Necker, ministre des Finances de Louis XVI, elle tient à Paris l'un des salons politiques les plus influents. Opposante à Napoléon, qui l'éloigne de Paris à partir de 1803, elle vit souvent à Coppet, en Suisse, et publie Corinne (1807) et De l'Allemagne (1813). Ses Considérations paraissent un an après sa mort.",
  },
  {
    id: 'sieyes',
    nom: 'Emmanuel-Joseph Sieyès',
    court: 'Sieyès',
    tri: 'Sieyès',
    naissance: { annee: 1748, lieu: 'Fréjus' },
    mort: { annee: 1836, lieu: 'Paris' },
    position: 'Patriote de 1789, républicain modéré, puis rallié à Bonaparte',
    couleur: c.republicains.couleur,
    oeuvres: ["Qu'est-ce que le tiers état ? (janvier 1789)"],
    portrait:
      "Prêtre, vicaire général de l'évêque de Chartres, il devient célèbre en quelques semaines avec son pamphlet de 1789, puis siège comme député du tiers état aux états généraux et à la Constituante. Membre de la Convention, il vote la mort du roi ; directeur en 1799, il prépare avec Bonaparte le coup d'État de Brumaire. Exilé comme régicide sous la Restauration, il rentre en France en 1830.",
  },
  {
    id: 'vigny',
    nom: 'Alfred de Vigny',
    court: 'Vigny',
    tri: 'Vigny',
    naissance: { annee: 1797, lieu: 'Loches' },
    mort: { annee: 1863, lieu: 'Paris' },
    position: 'Aristocrate libéral et désabusé, méfiant envers tous les pouvoirs',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Stello (1832)', 'Servitude et grandeur militaires (1835)'],
    portrait:
      "Fils d'une famille noble éprouvée par la Révolution, officier sous la Restauration, il devient l'un des grands poètes romantiques (Poèmes antiques et modernes, Les Destinées). Dans Stello, un médecin, le « Docteur Noir », raconte la fin tragique de trois poètes, dont André Chénier, pour montrer que tout pouvoir, monarchie ou république, sacrifie les poètes.",
  },
  {
    id: 'stendhal',
    nom: 'Stendhal (Henri Beyle)',
    court: 'Stendhal',
    tri: 'Stendhal',
    naissance: { annee: 1783, lieu: 'Grenoble' },
    mort: { annee: 1842, lieu: 'Paris' },
    position: 'Libéral, admirateur du jeune Bonaparte, hostile à la Restauration',
    couleur: c.orleanistes.couleur,
    oeuvres: ['La Chartreuse de Parme (1839)', 'Le Rouge et le Noir (1830)'],
    portrait:
      "Il suit l'armée de Bonaparte en Italie en 1800 et sert l'administration impériale jusqu'en 1814. Amoureux de l'Italie, il vit longtemps à Milan, puis devient consul à Civitavecchia sous Louis-Philippe. Le Rouge et le Noir (1830) et La Chartreuse de Parme (1839) font de lui l'un des maîtres du roman.",
  },
  {
    id: 'tocqueville',
    nom: 'Alexis de Tocqueville',
    court: 'Tocqueville',
    tri: 'Tocqueville',
    naissance: { annee: 1805, lieu: 'Paris' },
    mort: { annee: 1859, lieu: 'Cannes' },
    position: 'Libéral, attaché aux libertés politiques et méfiant envers la centralisation',
    couleur: c.orleanistes.couleur,
    oeuvres: ["L'Ancien Régime et la Révolution (1856)"],
    portrait:
      "Issu d'une famille noble dont plusieurs membres furent guillotinés sous la Terreur, il devient célèbre avec De la démocratie en Amérique (1835-1840). Député sous la monarchie de Juillet, ministre des Affaires étrangères en 1849, il se retire de la vie politique après le coup d'État de 1851. L'Ancien Régime et la Révolution, fondé sur un long travail d'archives, montre ce que la Révolution doit à la monarchie qu'elle a renversée.",
  },
  {
    id: 'campan',
    nom: 'Henriette Campan',
    court: 'Mme Campan',
    tri: 'Campan',
    naissance: { annee: 1752, lieu: 'Paris' },
    mort: { annee: 1822, lieu: 'Mantes' },
    position: 'Royaliste, fidèle à Marie-Antoinette, puis ralliée à l’Empire',
    couleur: c.legitimistes.couleur,
    oeuvres: ['Mémoires sur la vie privée de Marie-Antoinette (publication posthume, 1823)'],
    portrait:
      "Lectrice des filles de Louis XV, puis femme de chambre de Marie-Antoinette, elle vit vingt ans dans l'intimité de la reine. Ruinée par la Révolution, elle ouvre un pensionnat de jeunes filles, puis dirige pour Napoléon la maison d'éducation de la Légion d'honneur à Écouen. Ses Mémoires, publiés après sa mort, défendent la mémoire de la reine.",
  },
  {
    id: 'dumas',
    nom: 'Alexandre Dumas',
    court: 'Dumas',
    tri: 'Dumas',
    naissance: { annee: 1802, lieu: 'Villers-Cotterêts' },
    mort: { annee: 1870, lieu: 'Puys, près de Dieppe' },
    position: 'Libéral puis républicain, combattant des journées de juillet 1830',
    couleur: c.republicains.couleur,
    oeuvres: ['Le Collier de la reine (1849-1850)', 'Mes Mémoires (1852-1856)'],
    portrait:
      "Fils d'un général de la Révolution né à Saint-Domingue, il triomphe au théâtre puis dans le roman-feuilleton : Les Trois Mousquetaires, Le Comte de Monte-Cristo. Dans un cycle de romans consacré à la fin de la monarchie, dont Le Collier de la reine, il mêle personnages historiques et intrigues inventées pour un très large public.",
  },
  {
    id: 'beaumarchais',
    nom: 'Pierre-Augustin Caron de Beaumarchais',
    court: 'Beaumarchais',
    tri: 'Beaumarchais',
    naissance: { annee: 1732, lieu: 'Paris' },
    mort: { annee: 1799, lieu: 'Paris' },
    position: 'Homme des Lumières, critique des privilèges, sans être révolutionnaire',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Le Mariage de Figaro (écrit vers 1778, joué en 1784)'],
    portrait:
      "Fils d'un horloger, il devient homme d'affaires, agent secret du roi et fournisseur d'armes des insurgés américains. Ses comédies, Le Barbier de Séville (1775) et Le Mariage de Figaro, joué en 1784 après des années de censure, font rire la cour d'un valet plus habile que son maître. Emprisonné en 1792, il doit ensuite quitter la France pendant plusieurs années.",
    exception: "Mort en 1799 : admis dans le prologue, à titre d'exception, pour un texte écrit avant la Révolution.",
  },
  {
    id: 'chamfort',
    nom: 'Nicolas de Chamfort',
    court: 'Chamfort',
    tri: 'Chamfort',
    naissance: { annee: 1741, lieu: 'Auvergne' },
    mort: { annee: 1794, lieu: 'Paris' },
    position: "Homme de lettres de la cour, devenu républicain en 1789",
    couleur: c.republicains.couleur,
    oeuvres: ['Maximes, pensées, caractères et anecdotes (notes rédigées jusqu’en 1794, publiées en 1795)'],
    portrait:
      "Enfant naturel, sans fortune, il réussit dans les salons et au théâtre, entre à l'Académie française en 1781 et vit au service de grands seigneurs, qu'il observe sans indulgence. Ami de Mirabeau, il embrasse la Révolution, puis, menacé d'arrestation sous la Terreur, tente de se suicider et meurt de ses blessures en 1794.",
    exception: "Mort en 1794 : admis dans le prologue, à titre d'exception, pour des notes écrites en grande partie sous l'Ancien Régime.",
  },
  {
    id: 'rivarol',
    nom: 'Antoine de Rivarol',
    court: 'Rivarol',
    tri: 'Rivarol',
    naissance: { annee: 1753, lieu: 'Bagnols-sur-Cèze' },
    mort: { annee: 1801, lieu: 'Berlin' },
    position: 'Royaliste, polémiste contre-révolutionnaire',
    couleur: c.legitimistes.couleur,
    oeuvres: ["De l'universalité de la langue française (1784)"],
    portrait:
      "Causeur célèbre des salons parisiens, il remporte en 1784 le prix de l'Académie de Berlin avec un discours sur la langue française. Hostile à la Révolution, il écrit dans les journaux royalistes, puis émigre en 1792 et meurt en exil à Berlin.",
  },
  {
    id: 'laclos',
    nom: 'Pierre Choderlos de Laclos',
    court: 'Laclos',
    tri: 'Laclos',
    naissance: { annee: 1741, lieu: 'Amiens' },
    mort: { annee: 1803, lieu: 'Tarente' },
    position: "Proche du duc d'Orléans, jacobin en 1791, puis rallié à Bonaparte",
    couleur: c.republicains.couleur,
    oeuvres: ['Les Liaisons dangereuses (1782)'],
    portrait:
      "Officier d'artillerie sans fortune, il publie en 1782 Les Liaisons dangereuses, roman par lettres qui fait scandale. Secrétaire du duc d'Orléans au début de la Révolution, il est emprisonné sous la Terreur, puis devient général sous Bonaparte et meurt en Italie.",
  },
  {
    id: 'gouges',
    nom: 'Olympe de Gouges',
    court: 'Olympe de Gouges',
    tri: 'Gouges',
    naissance: { annee: 1748, lieu: 'Montauban' },
    mort: { annee: 1793, lieu: 'Paris' },
    position: 'Monarchiste constitutionnelle, puis proche des Girondins ; militante des droits des femmes',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Déclaration des droits de la femme et de la citoyenne (1791)'],
    portrait:
      "Fille d'un boucher de Montauban, veuve jeune, elle s'installe à Paris et écrit pour le théâtre, notamment contre l'esclavage des Noirs. Pendant la Révolution, elle multiplie les brochures politiques et réclame pour les femmes les mêmes droits que les hommes. Hostile aux Montagnards, elle est guillotinée le 3 novembre 1793.",
    exception: "Mort en 1793 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'saint-just',
    nom: 'Louis-Antoine de Saint-Just',
    court: 'Saint-Just',
    tri: 'Saint-Just',
    naissance: { annee: 1767, lieu: 'Decize' },
    mort: { annee: 1794, lieu: 'Paris' },
    position: 'Montagnard, proche de Robespierre',
    couleur: c.republicains.couleur,
    oeuvres: ['Discours concernant le jugement de Louis XVI (13 novembre 1792)'],
    portrait:
      "Élu à la Convention à vingt-cinq ans, il s'y fait connaître par son premier discours, sur le procès du roi. Membre du Comité de salut public, il est envoyé en mission aux armées et inspire les lois les plus dures de la Terreur. Il est guillotiné avec Robespierre le 10 thermidor an II.",
    exception: "Mort en 1794 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'desmoulins',
    nom: 'Camille Desmoulins',
    court: 'Desmoulins',
    tri: 'Desmoulins',
    naissance: { annee: 1760, lieu: 'Guise' },
    mort: { annee: 1794, lieu: 'Paris' },
    position: 'Révolutionnaire, Montagnard, proche de Danton, puis « indulgent »',
    couleur: c.republicains.couleur,
    oeuvres: ['Le Vieux Cordelier (décembre 1793 - janvier 1794)'],
    portrait:
      "Avocat sans causes, il harangue la foule au Palais-Royal le 12 juillet 1789 et devient l'un des journalistes les plus lus de la Révolution. Député montagnard, ami de Danton, il réclame à la fin de 1793, dans Le Vieux Cordelier, un « comité de clémence ». Il est guillotiné avec Danton en avril 1794.",
    exception: "Mort en 1794 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'robespierre',
    nom: 'Maximilien de Robespierre',
    court: 'Robespierre',
    tri: 'Robespierre',
    naissance: { annee: 1758, lieu: 'Arras' },
    mort: { annee: 1794, lieu: 'Paris' },
    position: 'Jacobin, Montagnard',
    couleur: c.republicains.couleur,
    oeuvres: ['Sur les principes de morale politique (discours du 5 février 1794)'],
    portrait:
      "Avocat à Arras, député du tiers état en 1789, il se fait remarquer par la défense intransigeante des droits et du suffrage de tous. Figure du club des Jacobins, élu à la Convention, il entre au Comité de salut public en juillet 1793 et devient la principale voix du gouvernement révolutionnaire. Renversé le 9 thermidor, il est guillotiné le lendemain.",
    exception: "Mort en 1794 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'condorcet',
    nom: 'Nicolas de Condorcet',
    court: 'Condorcet',
    tri: 'Condorcet',
    naissance: { annee: 1743, lieu: 'Ribemont' },
    mort: { annee: 1794, lieu: 'Bourg-la-Reine' },
    position: 'Républicain proche des Girondins, philosophe des Lumières',
    couleur: c.republicains.couleur,
    oeuvres: ["Esquisse d'un tableau historique des progrès de l'esprit humain (écrite en 1793-1794, publiée en 1795)"],
    portrait:
      "Mathématicien, secrétaire de l'Académie des sciences, ami de Voltaire et de Turgot, il défend l'instruction publique, l'abolition de l'esclavage et les droits des femmes. Député à la Convention, proscrit avec les Girondins en 1793, il se cache pendant des mois et rédige l'Esquisse. Arrêté en mars 1794, il meurt en prison, peut-être empoisonné.",
    exception: "Mort en 1794 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'chenier',
    nom: 'André Chénier',
    court: 'André Chénier',
    tri: 'Chénier',
    naissance: { annee: 1762, lieu: 'Constantinople' },
    mort: { annee: 1794, lieu: 'Paris' },
    position: 'Monarchiste constitutionnel, adversaire des Jacobins',
    couleur: c.orleanistes.couleur,
    oeuvres: ['La Jeune Captive (écrite en prison en 1794, publiée en 1795)'],
    portrait:
      "Poète presque inconnu de son vivant, il accueille la Révolution avec enthousiasme puis attaque les Jacobins dans les journaux. Arrêté en mars 1794, enfermé à Saint-Lazare, il y écrit ses derniers poèmes et est guillotiné le 7 thermidor an II, deux jours avant la chute de Robespierre. Ses vers, publiés au XIXe siècle, en feront une figure des romantiques.",
    exception: "Mort en 1794 : admis dans le chapitre 1, à titre d'exception, pour un texte écrit pendant la Révolution.",
  },
  {
    id: 'moreau',
    nom: 'Jacob-Nicolas Moreau',
    court: 'Moreau',
    tri: 'Moreau',
    naissance: { annee: 1717, lieu: 'Saint-Florentin' },
    mort: { annee: 1803, lieu: 'Chambourcy' },
    position: 'Défenseur de la monarchie absolue, adversaire des philosophes',
    couleur: c.legitimistes.couleur,
    oeuvres: ["Nouveau mémoire pour servir à l'histoire des Cacouacs (1757)"],
    portrait:
      "Avocat devenu publiciste au service de la cour, il attaque les encyclopédistes dans une satire célèbre, les « Cacouacs ». Nommé historiographe de France en 1774, il consacre sa carrière à justifier, par l'histoire et le droit, l'autorité du roi. Il traverse la Révolution sans émigrer et meurt sous le Consulat.",
  },
  {
    id: 'montesquieu',
    nom: 'Montesquieu (Charles-Louis de Secondat)',
    court: 'Montesquieu',
    tri: 'Montesquieu',
    naissance: { annee: 1689, lieu: 'La Brède' },
    mort: { annee: 1755, lieu: 'Paris' },
    position: 'Partisan d\'une monarchie tempérée par les corps intermédiaires',
    couleur: c.orleanistes.couleur,
    oeuvres: ["De l'esprit des lois (1748)"],
    portrait:
      "Président au parlement de Bordeaux, célèbre dès 1721 avec les Lettres persanes, il publie en 1748 De l'esprit des lois, comparaison des gouvernements de tous les temps. Il y défend la séparation des pouvoirs et le rôle des « pouvoirs intermédiaires » (noblesse, clergé, parlements), seuls capables d'empêcher la monarchie de tourner au despotisme.",
    exception: "Mort en 1755 : admis dans le prologue, à titre d'exception, pour un texte fondateur que lisent les hommes de 1789.",
  },
  {
    id: 'diderot',
    nom: 'Denis Diderot',
    court: 'Diderot',
    tri: 'Diderot',
    naissance: { annee: 1713, lieu: 'Langres' },
    mort: { annee: 1784, lieu: 'Paris' },
    position: 'Philosophe des Lumières, critique de l\'absolutisme et de l\'Église',
    couleur: c.republicains.couleur,
    oeuvres: ["Article « Autorité politique » de l'Encyclopédie (1751)"],
    portrait:
      "Fils d'un coutelier de Langres, il dirige avec d'Alembert l'Encyclopédie (1751-1772), vaste dictionnaire des sciences, des arts et des métiers, plusieurs fois interdit. Romancier, critique d'art et dramaturge, il écrit aussi, souvent sans signer, des pages très hardies contre le despotisme et la religion.",
    exception: "Mort en 1784 : admis dans le prologue, à titre d'exception, pour un texte fondateur que lisent les hommes de 1789.",
  },
  {
    id: 'voltaire',
    nom: 'Voltaire (François-Marie Arouet)',
    court: 'Voltaire',
    tri: 'Voltaire',
    naissance: { annee: 1694, lieu: 'Paris' },
    mort: { annee: 1778, lieu: 'Paris' },
    position: 'Partisan d\'un roi éclairé, adversaire acharné de l\'intolérance religieuse',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Dictionnaire philosophique (1764 ; édition de 1769)'],
    portrait:
      "Poète, dramaturge et conteur adulé, embastillé puis exilé dans sa jeunesse, il s'installe à Ferney, près de Genève, d'où il mène campagne contre « l'infâme », le fanatisme religieux, et défend les victimes de l'intolérance, comme Calas (1762). Il n'est pas démocrate : il espère des réformes venues d'un souverain éclairé.",
    exception: "Mort en 1778 : admis dans le prologue, à titre d'exception, pour un texte fondateur que lisent les hommes de 1789.",
  },
  {
    id: 'rousseau',
    nom: 'Jean-Jacques Rousseau',
    court: 'Rousseau',
    tri: 'Rousseau',
    naissance: { annee: 1712, lieu: 'Genève' },
    mort: { annee: 1778, lieu: 'Ermenonville' },
    position: 'Théoricien de la souveraineté du peuple et de l\'égalité',
    couleur: c.republicains.couleur,
    oeuvres: ['Du contrat social (1762)'],
    portrait:
      "Citoyen de Genève, autodidacte, il se brouille avec les philosophes de Paris et critique la civilisation qui a corrompu l'homme. Du contrat social et Émile, publiés en 1762, sont condamnés et brûlés ; il vit ensuite errant et persécuté. Les révolutionnaires en feront leur penseur de référence et transféreront ses cendres au Panthéon en 1794.",
    exception: "Mort en 1778 : admis dans le prologue, à titre d'exception, pour un texte fondateur que lisent les hommes de 1789.",
  },
  {
    id: 'turgot',
    nom: 'Anne Robert Jacques Turgot',
    court: 'Turgot',
    tri: 'Turgot',
    naissance: { annee: 1727, lieu: 'Paris' },
    mort: { annee: 1781, lieu: 'Paris' },
    position: 'Réformateur éclairé, proche des physiocrates',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Lettre au roi (24 août 1774)'],
    portrait:
      "Intendant du Limousin pendant treize ans, ami des philosophes et des économistes « physiocrates », il devient contrôleur général des Finances en août 1774. Il libère le commerce des grains, supprime la corvée royale et les corporations, mais se heurte aux privilégiés et à la cour ; Louis XVI le renvoie en mai 1776.",
    exception: "Mort en 1781 : admis dans le prologue, à titre d'exception, pour un texte écrit sous Louis XVI.",
  },
  {
    id: 'balzac',
    nom: 'Honoré de Balzac',
    court: 'Balzac',
    tri: 'Balzac',
    naissance: { annee: 1799, lieu: 'Tours' },
    mort: { annee: 1850, lieu: 'Paris' },
    position: 'Légitimiste et catholique à partir des années 1830',
    couleur: c.legitimistes.couleur,
    oeuvres: ['Les Chouans (1829)', 'Le Bal de Sceaux (1830)', 'Le Colonel Chabert (1832)'],
    portrait:
      "Après des débuts difficiles, il publie en 1829 Les Chouans, premier roman signé de son nom, puis bâtit La Comédie humaine, vaste ensemble de romans qui peint la société française de la Révolution à la monarchie de Juillet. Dans l'avant-propos de 1842, il se dit au service de la religion et de la monarchie.",
  },
  {
    id: 'courier',
    nom: 'Paul-Louis Courier',
    court: 'Courier',
    tri: 'Courier',
    naissance: { annee: 1772, lieu: 'Paris' },
    mort: { annee: 1825, lieu: 'Véretz (Indre-et-Loire)' },
    position: 'Libéral, adversaire des Bourbons et du « parti prêtre »',
    couleur: c.orleanistes.couleur,
    oeuvres: ['Pétition aux deux Chambres (1816)', 'Pétition pour des villageois que l\'on empêche de danser (1822)'],
    portrait:
      "Officier d'artillerie sous la Révolution et l'Empire, passionné de grec ancien, il quitte l'armée en 1809 et s'installe en Touraine comme propriétaire de vignes. Sous la Restauration, ses courtes brochures, signées « Paul-Louis, vigneron », attaquent avec une ironie redoutable les nobles, le clergé et l'administration ; elles lui valent la prison en 1821. Il est assassiné en 1825 près de chez lui.",
  },
  {
    id: 'beranger',
    nom: 'Pierre-Jean de Béranger',
    court: 'Béranger',
    tri: 'Béranger',
    naissance: { annee: 1780, lieu: 'Paris' },
    mort: { annee: 1857, lieu: 'Paris' },
    position: 'Libéral et patriote, chantre de la légende napoléonienne ; républicain sous la monarchie de Juillet',
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Chansons, dont « Le Vieux Drapeau » (1820)', '« Les Gaulois et les Francs » (1814)'],
    portrait:
      "D'origine modeste, malgré la particule qu'il s'est donnée, il devient le chansonnier le plus populaire du siècle. Ses chansons, qui se chantent sur des airs connus, raillent les nobles, les prêtres et les rois, et célèbrent le peuple et la gloire de l'Empire. Elles lui valent deux procès et deux séjours en prison sous la Restauration (1821 et 1828).",
  },
  {
    id: 'saint-simon',
    nom: 'Claude-Henri de Rouvroy, comte de Saint-Simon',
    court: 'Saint-Simon',
    tri: 'Saint-Simon',
    naissance: { annee: 1760, lieu: 'Paris' },
    mort: { annee: 1825, lieu: 'Paris' },
    position: 'Penseur de la société industrielle, précurseur du socialisme',
    couleur: c.socialistes.couleur,
    oeuvres: ["L'Organisateur (1819-1820)"],
    portrait:
      "Noble d'une grande famille, il combat en Amérique pour l'indépendance des États-Unis, renonce à son titre sous la Révolution et s'enrichit puis se ruine en spéculant sur les biens nationaux. Il consacre la fin de sa vie à imaginer une société organisée par les savants et les « industriels », c'est-à-dire tous les producteurs. Ses disciples, les saint-simoniens, influenceront les banquiers, les ingénieurs et les socialistes du siècle.",
  },
  {
    id: 'musset',
    nom: 'Alfred de Musset',
    court: 'Musset',
    tri: 'Musset',
    naissance: { annee: 1810, lieu: 'Paris' },
    mort: { annee: 1857, lieu: 'Paris' },
    position: 'Peu engagé ; libéral modéré, fidèle à la monarchie de Juillet',
    couleur: c.orleanistes.couleur,
    oeuvres: ["La Confession d'un enfant du siècle (1836)"],
    portrait:
      "Fils d'un fonctionnaire du ministère de la Guerre, il entre à dix-huit ans dans le cercle des romantiques et publie ses premiers vers en 1829. Poète des Nuits, auteur de comédies et de drames (Lorenzaccio), il a donné, avec La Confession d'un enfant du siècle, le portrait le plus célèbre du « mal du siècle » de sa génération.",
  },
  {
    id: 'gautier',
    nom: 'Théophile Gautier',
    court: 'Gautier',
    tri: 'Gautier',
    naissance: { annee: 1811, lieu: 'Tarbes' },
    mort: { annee: 1872, lieu: 'Neuilly-sur-Seine' },
    position: "Indifférent à la politique, défenseur de « l'art pour l'art » ; proche de la cour sous le Second Empire",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Histoire du romantisme (1874, posthume)'],
    portrait:
      "Élève peintre, il se lie très jeune avec Victor Hugo et combat pour Hernani en 1830, avec son célèbre gilet rouge. Poète, romancier (Le Capitaine Fracasse) et critique de théâtre et d'art, il défend une poésie qui ne sert aucune cause. Il écrit à la fin de sa vie les souvenirs de sa jeunesse romantique.",
  },
  {
    id: 'blanc',
    nom: 'Louis Blanc',
    court: 'Louis Blanc',
    tri: 'Blanc',
    naissance: { annee: 1811, lieu: 'Madrid' },
    mort: { annee: 1882, lieu: 'Cannes' },
    position: 'Républicain et socialiste',
    couleur: c.socialistes.couleur,
    oeuvres: ['Histoire de dix ans, 1830-1840 (1841-1844)'],
    portrait:
      "Journaliste républicain, il publie en 1839 L'Organisation du travail, qui réclame des ateliers sociaux pour garantir un emploi aux ouvriers, puis une histoire très critique des débuts de la monarchie de Juillet. Membre du gouvernement provisoire en 1848, il doit s'exiler après les journées de Juin et ne revient en France qu'en 1870.",
  },
  {
    id: 'napoleon',
    nom: 'Napoléon Bonaparte',
    court: 'Napoléon',
    tri: 'Napoléon',
    naissance: { annee: 1769, lieu: 'Ajaccio' },
    mort: { annee: 1821, lieu: 'Sainte-Hélène' },
    position: "Premier consul (1799-1804), puis empereur des Français (1804-1814 et 1815)",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Lettres à Joséphine (1796-1812, publiées au XIXe siècle)'],
    portrait:
      "Officier d'artillerie d'une famille de petite noblesse corse, général à vingt-quatre ans, il conquiert l'Italie (1796-1797), part pour l'Égypte, puis prend le pouvoir par le coup d'État de Brumaire (1799). Premier consul, puis empereur, il réorganise la France et domine l'Europe jusqu'aux désastres de 1812-1813. Exilé à l'île d'Elbe en 1814, revenu pour les Cent-Jours, vaincu à Waterloo, il meurt captif des Anglais à Sainte-Hélène.",
    exception: "Homme d'État plutôt qu'écrivain : admis dans le chapitre « Consulat et Empire », à titre d'exception, pour ses lettres.",
  },
  {
    id: 'coignet',
    nom: 'Jean-Roch Coignet',
    court: 'Coignet',
    tri: 'Coignet',
    naissance: { annee: 1776, lieu: 'Druyes-les-Belles-Fontaines (Yonne)' },
    mort: { annee: 1865, lieu: 'Auxerre' },
    position: "Soldat de la Garde impériale, fidèle à Napoléon toute sa vie",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Les Cahiers du capitaine Coignet (1851-1853)'],
    portrait:
      "Fils de paysans, maltraité dans son enfance, il devient soldat en 1799, entre dans la Garde des consuls puis dans les grenadiers à pied de la Garde impériale, et fait toutes les campagnes de l'Empire jusqu'à Waterloo, où il est officier. Il n'apprend à lire et à écrire qu'une fois soldat. Retiré à Auxerre, il rédige vers 1850 ses souvenirs, publiés sous le titre de Cahiers.",
  },
  {
    id: 'fontanes',
    nom: 'Louis de Fontanes',
    court: 'Fontanes',
    tri: 'Fontanes',
    naissance: { annee: 1757, lieu: 'Niort' },
    mort: { annee: 1821, lieu: 'Paris' },
    position: "Royaliste modéré rallié à Bonaparte, orateur officiel de l'Empire, pair de France sous la Restauration",
    couleur: c.legitimistes.couleur,
    oeuvres: ['Discours (1804-1806)', "Odes sur la mort du duc d'Enghien (1804) et sur l'enlèvement du pape (1809), publiées en 1839"],
    portrait:
      "Poète et critique, ami et protecteur de Chateaubriand, il se rallie au Premier consul. Président du Corps législatif de 1804 à 1810, puis grand maître de l'Université, chargé de tout l'enseignement de l'Empire, il prononce les grands éloges officiels du régime. En privé, il écrit des odes hostiles à Napoléon, publiées seulement après sa mort. Il se rallie aux Bourbons en 1814.",
  },
  {
    id: 'las-cases',
    nom: 'Emmanuel de Las Cases',
    court: 'Las Cases',
    tri: 'Las Cases',
    naissance: { annee: 1766, lieu: 'château de Las Cases (Tarn)' },
    mort: { annee: 1842, lieu: 'Passy' },
    position: "Ancien émigré rallié à l'Empire, compagnon d'exil de Napoléon",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Mémorial de Sainte-Hélène (1823)'],
    portrait:
      "Officier de marine noble, il émigre sous la Révolution, rentre en France sous le Consulat et devient chambellan de l'empereur. En 1815, il suit Napoléon à Sainte-Hélène et note leurs conversations, jusqu'à son expulsion de l'île par les Anglais en novembre 1816. Le Mémorial, publié en 1823, est l'un des livres les plus lus du siècle et l'une des sources de la légende napoléonienne.",
  },
  {
    id: 'marbot',
    nom: 'Marcellin de Marbot',
    court: 'Marbot',
    tri: 'Marbot',
    naissance: { annee: 1782, lieu: 'Altillac (Corrèze)' },
    mort: { annee: 1854, lieu: 'Paris' },
    position: "Officier de l'Empire, rallié ensuite à la monarchie de Juillet",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Mémoires du général baron de Marbot (publiés en 1891)'],
    portrait:
      "Fils d'un général de la Révolution, il s'engage à dix-sept ans et fait presque toutes les campagnes de l'Empire comme officier de cavalerie et aide de camp de plusieurs maréchaux. Général sous la monarchie de Juillet, il écrit à la fin de sa vie des Mémoires pleins de verve, publiés par sa famille en 1891.",
  },
  {
    id: 'constant',
    nom: 'Benjamin Constant',
    court: 'Constant',
    tri: 'Constant',
    naissance: { annee: 1767, lieu: 'Lausanne' },
    mort: { annee: 1830, lieu: 'Paris' },
    position: "Libéral ; opposant à Napoléon, rallié pendant les Cent-Jours, député libéral sous la Restauration",
    couleur: c.orleanistes.couleur,
    oeuvres: ["De l'esprit de conquête et de l'usurpation (1814)"],
    portrait:
      "Né à Lausanne dans une famille protestante d'origine française, compagnon de Mme de Staël, il siège au Tribunat jusqu'à ce que Bonaparte l'en exclue en 1802. Il combat l'Empire par la plume, puis se rallie à Napoléon pendant les Cent-Jours pour rédiger une constitution libérale. Député sous la Restauration, il est l'un des maîtres du libéralisme ; il est aussi l'auteur du roman Adolphe (1816).",
  },
  {
    id: 'bourgogne',
    nom: 'Adrien Bourgogne',
    court: 'Bourgogne',
    tri: 'Bourgogne',
    naissance: { annee: 1785, lieu: 'Condé-sur-l\'Escaut (Nord)' },
    mort: { annee: 1867, lieu: 'Valenciennes' },
    position: "Sous-officier de la Garde impériale, fidèle à l'empereur",
    couleur: c.bonapartistes.couleur,
    oeuvres: ['Mémoires du sergent Bourgogne (publiés en 1898)'],
    portrait:
      "Fils d'un marchand de toile, il entre en 1806 dans les vélites de la Garde impériale et fait les campagnes de Prusse, de Pologne, d'Espagne et de Russie, où il survit à la retraite. Prisonnier en 1813, il prend des notes qui lui serviront à rédiger ses Mémoires. Après 1830, il est officier de place à Valenciennes. Ses souvenirs ne sont publiés qu'en 1898.",
  },
];

export const auteurs: Record<string, Auteur> = Object.fromEntries(liste.map((a) => [a.id, a]));

export const auteursTries = [...liste].sort((a, b) => a.tri.localeCompare(b.tri, 'fr'));

export function auteur(id: string): Auteur {
  const a = auteurs[id];
  if (!a) throw new Error(`Auteur inconnu : « ${id} » (ajoutez-le dans src/data/auteurs.ts)`);
  return a;
}
