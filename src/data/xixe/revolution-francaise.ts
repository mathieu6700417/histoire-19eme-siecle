// Données de la leçon « La Révolution française » (spec 20) : frise des régimes, des parties du
// récit et des grandes journées, glossaire et personnages. Les ancres (`lien`, `id`) sont celles
// de la page src/content/lecons/xixe/revolution-francaise.mdx : stables, pour que de futures
// sous-pages puissent s'y rattacher.
import type { BandeFrise, JourneeFrise } from '../types';

/** Régimes (bandes du haut). `motif` : 0 uni clair, 1 hachures, 2 points, 3 uni moyen. */
export const regimes: BandeFrise[] = [
  { debut: '1787-01-01', fin: '1789-06-17', libelle: 'Monarchie absolue', court: 'Monarchie absolue', motif: 1, lien: '#la-crise-de-la-monarchie' },
  { debut: '1789-06-17', fin: '1792-08-10', libelle: 'Monarchie constitutionnelle', court: 'Monarchie const.', motif: 0, lien: '#monarchie-constitutionnelle' },
  { debut: '1792-09-21', fin: '1795-10-26', libelle: 'République : la Convention', court: 'Convention', motif: 3, lien: '#la-convention' },
  { debut: '1795-10-26', fin: '1799-11-10', libelle: 'République : le Directoire', court: 'Directoire', motif: 2, lien: '#le-directoire' },
  { debut: '1799-11-10', fin: '1800-01-01', libelle: 'Consulat', court: 'Cons.', motif: 1, lien: '#18-brumaire' },
];

/** Parties du récit (seconde rangée de bandes). */
export const parties: BandeFrise[] = [
  { debut: '1787-01-01', fin: '1789-05-05', libelle: '1. La crise de la monarchie', court: '1. La crise', motif: 0, lien: '#la-crise-de-la-monarchie' },
  { debut: '1789-05-05', fin: '1789-10-06', libelle: '2. 1789', court: '2', motif: 3, lien: '#annee-1789' },
  { debut: '1789-10-06', fin: '1791-10-01', libelle: '3. Une monarchie constitutionnelle', court: '3. Monarchie constitutionnelle', motif: 0, lien: '#monarchie-constitutionnelle' },
  { debut: '1791-10-01', fin: '1792-09-21', libelle: '4. La guerre et la chute du roi', court: '4. Chute du roi', motif: 3, lien: '#la-guerre-et-la-chute-du-roi' },
  { debut: '1792-09-21', fin: '1794-07-27', libelle: '5. La Convention et la Terreur', court: '5. Convention', motif: 0, lien: '#la-convention' },
  { debut: '1794-07-27', fin: '1800-01-01', libelle: '6. Thermidor et Directoire', court: '6. Directoire', motif: 3, lien: '#thermidor-et-directoire' },
];

/** Grandes journées (repères cliquables). `court` : libellé sur la frise ; `libelle` : détail. */
export const journees: JourneeFrise[] = [
  { date: '1787-02-22', court: 'Notables', libelle: '22 février 1787 : ouverture de l’assemblée des notables', lien: '#assemblee-des-notables' },
  { date: '1788-06-07', court: 'Tuiles', libelle: '7 juin 1788 : journée des Tuiles à Grenoble', lien: '#journee-des-tuiles' },
  { date: '1788-08-08', court: 'Convocation', libelle: '8 août 1788 : le roi convoque les états généraux', lien: '#convocation-des-etats-generaux' },
  { date: '1789-05-05', court: 'États généraux', libelle: '5 mai 1789 : ouverture des états généraux à Versailles', lien: '#5-mai-1789' },
  { date: '1789-06-20', court: 'Jeu de paume', libelle: '17 et 20 juin 1789 : Assemblée nationale, serment du Jeu de paume', lien: '#20-juin-1789' },
  { date: '1789-07-14', court: 'Bastille', libelle: '14 juillet 1789 : prise de la Bastille', lien: '#14-juillet-1789' },
  { date: '1789-08-04', court: '4 août', libelle: 'Nuit du 4 août 1789 : abolition des privilèges', lien: '#4-aout-1789' },
  { date: '1789-08-26', court: 'Déclaration', libelle: '26 août 1789 : Déclaration des droits de l’homme et du citoyen', lien: '#26-aout-1789' },
  { date: '1789-10-05', court: 'Octobre', libelle: '5 et 6 octobre 1789 : le roi ramené à Paris', lien: '#journees-d-octobre' },
  { date: '1790-07-12', court: 'Clergé', libelle: '12 juillet 1790 : Constitution civile du clergé', lien: '#constitution-civile-du-clerge' },
  { date: '1790-07-14', court: 'Fédération', libelle: '14 juillet 1790 : fête de la Fédération', lien: '#fete-de-la-federation' },
  { date: '1791-06-21', court: 'Varennes', libelle: '20-21 juin 1791 : fuite du roi, arrêté à Varennes', lien: '#fuite-a-varennes' },
  { date: '1791-07-17', court: 'Champ-de-Mars', libelle: '17 juillet 1791 : fusillade du Champ-de-Mars', lien: '#champ-de-mars' },
  { date: '1791-09-03', court: 'Constitution', libelle: '3 septembre 1791 : Constitution de 1791', lien: '#constitution-de-1791' },
  { date: '1792-04-20', court: 'Guerre', libelle: '20 avril 1792 : déclaration de guerre au roi de Bohême et de Hongrie', lien: '#20-avril-1792' },
  { date: '1792-08-10', court: '10 août', libelle: '10 août 1792 : prise des Tuileries, chute du roi', lien: '#10-aout-1792' },
  { date: '1792-09-02', court: 'Septembre', libelle: '2-6 septembre 1792 : massacres de Septembre', lien: '#massacres-de-septembre' },
  { date: '1792-09-21', court: 'République', libelle: '20-22 septembre 1792 : Valmy, abolition de la royauté, an I de la République', lien: '#21-septembre-1792' },
  { date: '1793-01-21', court: 'Louis XVI', libelle: '21 janvier 1793 : exécution de Louis XVI', lien: '#21-janvier-1793' },
  { date: '1793-03-11', court: 'Vendée', libelle: 'Mars 1793 : soulèvement de la Vendée', lien: '#guerre-de-vendee' },
  { date: '1793-06-02', court: '2 juin', libelle: '2 juin 1793 : chute des Girondins', lien: '#2-juin-1793' },
  { date: '1793-09-17', court: 'Suspects', libelle: '17 septembre 1793 : loi des suspects', lien: '#la-terreur' },
  { date: '1794-04-05', court: 'Danton', libelle: 'Mars-avril 1794 : exécution des hébertistes, puis des indulgents (Danton)', lien: '#hebertistes-et-indulgents' },
  { date: '1794-06-10', court: 'Prairial', libelle: '22 prairial an II (10 juin 1794) : loi de la Grande Terreur', lien: '#grande-terreur' },
  { date: '1794-07-27', court: 'Thermidor', libelle: '9 thermidor an II (27 juillet 1794) : chute de Robespierre', lien: '#9-thermidor' },
  { date: '1795-05-20', court: 'Prairial III', libelle: '1er prairial an III (20 mai 1795) : dernière insurrection des sans-culottes', lien: '#journees-de-prairial' },
  { date: '1795-10-05', court: 'Vendémiaire', libelle: '13 vendémiaire an IV (5 octobre 1795) : insurrection royaliste écrasée', lien: '#13-vendemiaire' },
  { date: '1796-05-10', court: 'Égaux', libelle: '21 floréal an IV (10 mai 1796) : arrestation de Babeuf et des Égaux', lien: '#conjuration-des-egaux' },
  { date: '1797-09-04', court: 'Fructidor', libelle: '18 fructidor an V (4 septembre 1797) : coup d’État contre les royalistes', lien: '#18-fructidor' },
  { date: '1798-05-11', court: 'Floréal', libelle: '22 floréal an VI (11 mai 1798) : élections jacobines annulées', lien: '#18-fructidor' },
  { date: '1799-11-09', court: 'Brumaire', libelle: '18-19 brumaire an VIII (9-10 novembre 1799) : coup d’État de Bonaparte', lien: '#18-brumaire' },
];

export interface Terme { id: string; terme: string; definition: string }

/** Glossaire (ancre : #glossaire-<id>). Ordre alphabétique. */
export const glossaire: Terme[] = [
  { id: 'assignat', terme: 'Assignat', definition: 'Titre émis à partir de décembre 1789, gagé sur les biens nationaux, puis devenu papier-monnaie (1790). Imprimé en masse pour financer la guerre, il perd presque toute sa valeur ; il est supprimé en 1796.' },
  { id: 'biens-nationaux', terme: 'Biens nationaux', definition: 'Biens confisqués par la nation et vendus aux enchères : ceux de l’Église d’abord (novembre 1789), puis ceux des émigrés. Leurs acheteurs, bourgeois et paysans aisés, deviennent attachés à la Révolution.' },
  { id: 'cahiers-de-doleances', terme: 'Cahiers de doléances', definition: 'Registres de plaintes et de vœux rédigés au printemps 1789 par les assemblées des trois ordres, dans chaque paroisse et chaque bailliage, pour être portés aux états généraux.' },
  { id: 'calendrier-republicain', terme: 'Calendrier républicain', definition: 'Calendrier adopté en octobre 1793 et appliqué jusqu’à la fin de 1805. L’an I commence le 22 septembre 1792 ; douze mois de trente jours aux noms de saison (vendémiaire, brumaire, frimaire ; nivôse, pluviôse, ventôse ; germinal, floréal, prairial ; messidor, thermidor, fructidor), divisés en décades.' },
  { id: 'chouans', terme: 'Chouans', definition: 'Insurgés royalistes de Bretagne, du Maine et de Normandie (1793-1800), qui mènent une guérilla contre la République. On les distingue des Vendéens, dont l’armée affronte la République en bataille rangée en 1793.' },
  { id: 'comite-de-salut-public', terme: 'Comité de salut public', definition: 'Comité de la Convention créé en avril 1793. De l’été 1793 à juillet 1794, ses douze membres (Robespierre, Saint-Just, Couthon, Carnot, Barère…) dirigent la guerre, l’administration et la répression : c’est le vrai gouvernement de la Terreur.' },
  { id: 'constitution-civile', terme: 'Constitution civile du clergé', definition: 'Loi du 12 juillet 1790 qui réorganise l’Église de France : un évêque par département, curés et évêques élus et payés par l’État. Le serment exigé des prêtres (novembre 1790) et la condamnation du pape (1791) coupent le clergé en deux.' },
  { id: 'cordeliers', terme: 'Club des Cordeliers', definition: 'Société populaire parisienne, plus radicale et plus ouverte aux petites gens que les Jacobins (Danton, Marat, Desmoulins, puis Hébert). Elle réclame la République dès la fuite à Varennes.' },
  { id: 'emigres', terme: 'Émigrés', definition: 'Français, surtout nobles, partis à l’étranger à partir de juillet 1789. Rassemblés à Coblence autour des frères du roi, ils appellent les souverains européens à intervenir ; leurs biens sont confisqués et ils sont bannis à perpétuité (1792-1793).' },
  { id: 'enrages', terme: 'Enragés', definition: 'Militants parisiens de 1793 (Jacques Roux, Varlet, Leclerc) qui réclament la taxation des prix et la répression des accapareurs. Leurs revendications sont reprises en partie, et eux-mêmes éliminés, par la Montagne.' },
  { id: 'etats-generaux', terme: 'États généraux', definition: 'Assemblée des députés des trois ordres, convoquée par le roi de manière exceptionnelle pour le conseiller, surtout en matière d’impôt. Avant 1789, ils ne s’étaient plus réunis depuis 1614.' },
  { id: 'federalistes', terme: 'Fédéralistes', definition: 'Nom donné par les Montagnards aux villes et départements (Lyon, Marseille, Bordeaux, Caen…) qui se soulèvent après l’élimination des Girondins en juin 1793, accusés de vouloir briser l’unité de la République.' },
  { id: 'feuillants', terme: 'Feuillants', definition: 'Club fondé en juillet 1791 par les Jacobins modérés (Barnave, Duport, Lameth, La Fayette) qui refusent la déchéance du roi après Varennes et veulent terminer la Révolution avec la Constitution de 1791.' },
  { id: 'girondins', terme: 'Girondins', definition: 'Groupe de députés, dont plusieurs viennent de la Gironde (Vergniaud, Guadet), réunis autour de Brissot et des Roland. Partisans de la guerre en 1792, attachés aux départements et méfiants envers Paris, ils sont éliminés le 2 juin 1793. On disait alors plutôt « brissotins ».' },
  { id: 'jacobins', terme: 'Club des Jacobins', definition: 'Société des amis de la Constitution, installée au couvent des Jacobins de la rue Saint-Honoré. Elle compte des centaines de sociétés affiliées en province. D’abord largement ouverte, elle devient après 1792 le lieu de la Montagne et de Robespierre ; elle est fermée en novembre 1794.' },
  { id: 'loi-des-suspects', terme: 'Loi des suspects', definition: 'Loi du 17 septembre 1793 qui permet d’arrêter tous ceux qui, « par leur conduite, leurs relations, leurs propos ou leurs écrits », paraissent ennemis de la Révolution : nobles non ralliés, parents d’émigrés, fonctionnaires destitués…' },
  { id: 'maximum', terme: 'Maximum', definition: 'Prix maximal imposé : sur les grains (mai 1793), puis maximum général des denrées et des salaires (29 septembre 1793). Réclamé par les sans-culottes, il est aboli en décembre 1794.' },
  { id: 'montagnards', terme: 'Montagnards', definition: 'Députés de la Convention siégeant sur les gradins les plus élevés, « la Montagne » : Robespierre, Danton, Marat, Saint-Just. Appuyés sur les Jacobins et les sans-culottes parisiens, ils dominent la Convention de juin 1793 à juillet 1794.' },
  { id: 'muscadins', terme: 'Muscadins', definition: 'Jeunes gens des beaux quartiers qui, après Thermidor, pourchassent les jacobins à coups de gourdin ; on parle aussi de « jeunesse dorée ». Leurs excentricités de mode leur valent le surnom d’« Incroyables ».' },
  { id: 'ordres', terme: 'Ordres', definition: 'Les trois groupes de la société d’Ancien Régime : le clergé (premier ordre), la noblesse (deuxième), le tiers état (tous les autres). Chaque ordre a son rang, ses droits et ses devoirs.' },
  { id: 'plaine', terme: 'La Plaine (ou le Marais)', definition: 'Les députés de la Convention qui siègent en bas de la salle, entre Girondins et Montagnards. Majoritaires, ils font pencher la balance d’un côté puis de l’autre, et décident de la chute de Robespierre.' },
  { id: 'pretres-refractaires', terme: 'Prêtre jureur, prêtre réfractaire', definition: 'Le jureur (ou constitutionnel) prête le serment à la Constitution civile du clergé ; le réfractaire le refuse. Environ la moitié des curés refusent, selon les estimations, avec de fortes différences selon les régions.' },
  { id: 'privileges', terme: 'Privilèges', definition: 'Littéralement « lois particulières » : droits propres à un ordre, à une province, à une ville ou à un métier (exemptions d’impôt, tribunaux particuliers, droits honorifiques). Ils sont abolis dans la nuit du 4 août 1789.' },
  { id: 'sans-culottes', terme: 'Sans-culottes', definition: 'Militants des quartiers populaires, artisans, boutiquiers et compagnons, qui portent le pantalon et non la culotte des gens aisés. Ils réclament le contrôle des prix, la démocratie directe et la punition des « traîtres ».' },
  { id: 'sections', terme: 'Sections', definition: 'Les 48 circonscriptions de Paris créées en 1790. Leurs assemblées, ouvertes à tous les citoyens après août 1792, sont le cœur de la mobilisation sans-culotte.' },
  { id: 'tiers-etat', terme: 'Tiers état', definition: 'Le troisième ordre : tous ceux qui ne sont ni clercs ni nobles, du riche banquier au journalier, soit l’immense majorité des Français (plus de 95 %, selon les estimations).' },
  { id: 'thermidoriens', terme: 'Thermidoriens', definition: 'Les députés qui renversent Robespierre le 9 thermidor an II et gouvernent ensuite la Convention (1794-1795) : anciens terroristes repentis et modérés de la Plaine, réunis par la volonté de finir la Terreur.' },
  { id: 'veto', terme: 'Veto', definition: 'Droit pour le roi, dans la Constitution de 1791, de suspendre l’application d’une loi pendant deux législatures au plus (veto suspensif). Son usage en 1792 vaut à Louis XVI le surnom de « Monsieur Veto ».' },
];

export interface Personnage { id: string; nom: string; dates: string; role: string }

/** Personnages (ancre : #personnage-<id>). Ordre chronologique d'entrée en scène. */
export const personnages: Personnage[] = [
  { id: 'louis-xvi', nom: 'Louis XVI', dates: '1754-1793', role: 'Roi de France de 1774 à 1792. Bien intentionné mais indécis, il hésite entre réformes et résistance, accepte la Constitution sans y croire et tente de fuir en 1791. Déchu le 10 août 1792, jugé par la Convention, il est guillotiné le 21 janvier 1793.' },
  { id: 'marie-antoinette', nom: 'Marie-Antoinette', dates: '1755-1793', role: 'Archiduchesse d’Autriche, reine de France. Impopulaire dès les années 1780, cible des pamphlets, elle pousse le roi à la résistance et correspond avec les cours étrangères. Elle est guillotinée le 16 octobre 1793.' },
  { id: 'necker', nom: 'Jacques Necker', dates: '1732-1804', role: 'Banquier genevois, ministre des Finances très populaire. Rappelé en août 1788, il fait accorder le doublement du tiers. Son renvoi, le 11 juillet 1789, déclenche l’insurrection parisienne ; rappelé, il quitte définitivement le pouvoir en 1790.' },
  { id: 'sieyes', nom: 'Emmanuel-Joseph Sieyès', dates: '1748-1836', role: 'Abbé, auteur de *Qu’est-ce que le tiers état ?* (1789). Il inspire la proclamation de l’Assemblée nationale, se fait discret sous la Terreur (« J’ai vécu », dira-t-il), entre au Directoire en 1799 et prépare avec Bonaparte le coup d’État de Brumaire.' },
  { id: 'mirabeau', nom: 'Mirabeau', dates: '1749-1791', role: 'Honoré-Gabriel Riqueti, comte de Mirabeau, noble élu par le tiers état de Provence, le plus grand orateur de la Constituante. Partisan d’un roi fort dans une monarchie constitutionnelle, il conseille secrètement la cour contre rémunération. Il meurt en avril 1791.' },
  { id: 'la-fayette', nom: 'La Fayette', dates: '1757-1834', role: 'Marquis, héros de la guerre d’indépendance américaine, commandant de la garde nationale de Paris en 1789. Défenseur de la monarchie constitutionnelle, compromis par la fusillade du Champ-de-Mars, il passe à l’ennemi après le 10 août 1792.' },
  { id: 'olympe-de-gouges', nom: 'Olympe de Gouges', dates: '1748-1793', role: 'Femme de lettres, autrice de la *Déclaration des droits de la femme et de la citoyenne* (1791). Proche des Girondins, hostile à la mort du roi puis à la Montagne, elle est guillotinée le 3 novembre 1793.' },
  { id: 'brissot', nom: 'Jacques-Pierre Brissot', dates: '1754-1793', role: 'Journaliste, chef de file des Girondins (on dit alors « brissotins »). Il pousse à la guerre en 1791-1792 pour démasquer les traîtres et répandre la liberté. Arrêté après le 2 juin 1793, il est guillotiné le 31 octobre 1793.' },
  { id: 'danton', nom: 'Georges Jacques Danton', dates: '1759-1794', role: 'Avocat, orateur des Cordeliers, ministre de la Justice après le 10 août 1792 et voix de la « patrie en danger ». Membre du premier Comité de salut public, il réclame ensuite la fin de la Terreur (les « indulgents ») ; il est guillotiné le 5 avril 1794.' },
  { id: 'marat', nom: 'Jean-Paul Marat', dates: '1743-1793', role: 'Médecin et journaliste, auteur de *L’Ami du peuple*, qui dénonce sans relâche les traîtres et appelle aux exécutions. Député de Paris à la Convention, il est assassiné par Charlotte Corday le 13 juillet 1793 et honoré comme un martyr.' },
  { id: 'robespierre', nom: 'Maximilien de Robespierre', dates: '1758-1794', role: 'Avocat d’Arras, député à la Constituante, figure des Jacobins, surnommé « l’Incorruptible ». Membre du Comité de salut public à partir de juillet 1793, il incarne la Terreur et le culte de l’Être suprême. Renversé le 9 thermidor an II, il est guillotiné le lendemain.' },
  { id: 'saint-just', nom: 'Louis Antoine de Saint-Just', dates: '1767-1794', role: 'Plus jeune député de la Convention, proche de Robespierre. Il réclame la mort du roi, défend le gouvernement révolutionnaire, mène les armées en mission et rédige les rapports contre les factions. Guillotiné avec Robespierre.' },
  { id: 'hebert', nom: 'Jacques-René Hébert', dates: '1757-1794', role: 'Journaliste du *Père Duchesne*, feuille au langage populaire et ordurier, porte-parole des sans-culottes et de la déchristianisation. Accusé de préparer une insurrection, il est guillotiné le 24 mars 1794 avec ses partisans, les hébertistes.' },
  { id: 'charlotte-corday', nom: 'Charlotte Corday', dates: '1768-1793', role: 'Jeune Normande favorable aux Girondins réfugiés à Caen. Elle poignarde Marat dans sa baignoire le 13 juillet 1793, pour, dit-elle, sauver la paix ; elle est guillotinée quatre jours plus tard.' },
  { id: 'barras', nom: 'Paul Barras', dates: '1755-1829', role: 'Ancien noble, conventionnel, l’un des tombeurs de Robespierre. Il fait écraser l’insurrection de Vendémiaire avec Bonaparte, puis reste directeur de 1795 à 1799, symbole d’un régime d’affaires et d’intrigues.' },
  { id: 'bonaparte', nom: 'Napoléon Bonaparte', dates: '1769-1821', role: 'Officier d’artillerie corse remarqué à Toulon (1793), il réprime Vendémiaire (1795), conquiert l’Italie (1796-1797), part en Égypte (1798) et prend le pouvoir par le coup d’État de Brumaire (1799). Premier consul, puis empereur des Français en 1804.' },
];
