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
    oeuvres: ["Mémoires d'outre-tombe (écrits de 1809 à 1841, publiés en 1848-1850)"],
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
    oeuvres: ['Histoire des Girondins (1847)'],
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
    oeuvres: ['Les Châtiments (1853)', 'Quatrevingt-treize (1874)'],
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
    oeuvres: ['Considérations sur les principaux événements de la Révolution française (1818, posthume)'],
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
    oeuvres: ['Stello (1832)'],
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
    oeuvres: ['La Chartreuse de Parme (1839)'],
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
    oeuvres: ['Le Collier de la reine (1849-1850)'],
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
    oeuvres: ['Les Chouans (1829)'],
    portrait:
      "Après des débuts difficiles, il publie en 1829 Les Chouans, premier roman signé de son nom, puis bâtit La Comédie humaine, vaste ensemble de romans qui peint la société française de la Révolution à la monarchie de Juillet. Dans l'avant-propos de 1842, il se dit au service de la religion et de la monarchie.",
  },
];

export const auteurs: Record<string, Auteur> = Object.fromEntries(liste.map((a) => [a.id, a]));

export const auteursTries = [...liste].sort((a, b) => a.tri.localeCompare(b.tri, 'fr'));

export function auteur(id: string): Auteur {
  const a = auteurs[id];
  if (!a) throw new Error(`Auteur inconnu : « ${id} » (ajoutez-le dans src/data/auteurs.ts)`);
  return a;
}
