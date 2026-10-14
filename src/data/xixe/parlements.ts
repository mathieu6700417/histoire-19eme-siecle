// Données de la sous-page « Les parlements d'Ancien Régime » (spec 21) : frise sur cinq siècles
// (échelle par segments), carte des parlements et conseils souverains en 1789, glossaire et
// personnages. Les ancres (`lien`) sont celles de
// src/content/lecons/xixe/revolution-francaise/parlements.mdx.
import type { BandeFrise, FondCarte, JourneeFrise, LieuCarte, TrancheFrise, ZoneCarte } from '../types';
import fondParlements from './cartes/parlements-1789.json';

export const fond: FondCarte = fondParlements;

// --- Frise ---------------------------------------------------------------

/** Échelle par segments : les siècles anciens sont comprimés (axe en tirets). */
export const tranches: TrancheFrise[] = [
  { debut: 1250, fin: 1700, pxParAn: 1.4, pas: 50, libelle: 'De 1250 à 1700 : échelle très comprimée (un demi-siècle entre deux graduations)' },
  { debut: 1700, fin: 1770, pxParAn: 7, pas: 10, libelle: 'De 1700 à 1770 : échelle comprimée (une décennie entre deux graduations)' },
  { debut: 1770, fin: 1791, pxParAn: 36, pas: 1, libelle: 'De 1770 à 1790 : une année par graduation' },
];

/** Règnes (bandes du haut). `motif` : 0 uni clair, 1 hachures, 2 points, 3 uni moyen. */
export const regnes: BandeFrise[] = [
  { debut: '1250-01-01', fin: '1589-08-02', libelle: 'Capétiens, puis Valois', court: 'Capétiens, Valois', motif: 0, dates: 'jusqu’en 1589' },
  { debut: '1589-08-02', fin: '1610-05-14', libelle: 'Henri IV', court: '', motif: 3, dates: '1589-1610' },
  { debut: '1610-05-14', fin: '1643-05-14', libelle: 'Louis XIII', court: 'L. XIII', motif: 1, dates: '1610-1643' },
  { debut: '1643-05-14', fin: '1715-09-01', libelle: 'Louis XIV', motif: 0, dates: '1643-1715' },
  { debut: '1715-09-01', fin: '1723-02-16', libelle: 'Régence', court: 'Rég.', motif: 2, dates: '1715-1723' },
  { debut: '1723-02-16', fin: '1774-05-10', libelle: 'Louis XV', motif: 3, dates: 'roi en 1715, majeur en 1723, mort en 1774' },
  { debut: '1774-05-10', fin: '1791-01-01', libelle: 'Louis XVI', motif: 1, dates: '1774-1792' },
];

/** Parties du récit (seconde rangée). */
export const parties: BandeFrise[] = [
  { debut: '1250-01-01', fin: '1598-01-01', libelle: '1. Au service du roi', court: '1. Au service du roi', motif: 0, lien: '#au-service-du-roi', dates: 'XIIIe-XVIe siècle' },
  { debut: '1598-01-01', fin: '1715-09-01', libelle: '2. Fronde et mise au pas', court: '2. La Fronde', motif: 3, lien: '#la-fronde', dates: '1598-1715' },
  { debut: '1715-09-01', fin: '1723-02-16', libelle: '3. La revanche de 1715', court: '3', motif: 0, lien: '#la-revanche-de-1715', dates: '1715-1723' },
  { debut: '1723-02-16', fin: '1771-01-20', libelle: '4. Le siècle des conflits', motif: 3, lien: '#le-siecle-des-conflits', dates: '1715-1770' },
  { debut: '1771-01-20', fin: '1774-11-12', libelle: '5. Maupeou', motif: 0, lien: '#le-coup-de-majeste', dates: '1771-1774' },
  { debut: '1774-11-12', fin: '1788-09-25', libelle: '6. Contre les réformes', motif: 3, lien: '#contre-les-reformes', dates: '1774-1788' },
  { debut: '1788-09-25', fin: '1791-01-01', libelle: '7. La chute', court: '7. Chute', motif: 0, lien: '#la-chute', dates: '1788-1790' },
];

/** Grandes dates (repères cliquables). */
export const journees: JourneeFrise[] = [
  { date: '1254-06-01', court: 'Olim', libelle: 'Vers 1250 : sous Saint Louis, la cour du roi siège « en parlement » ; ses arrêts sont enregistrés à partir de 1254 (registres des Olim)', lien: '#origines' },
  { date: '1345-03-11', court: '1345', libelle: '11 mars 1345 : ordonnance qui fixe l’organisation du parlement de Paris', lien: '#origines' },
  { date: '1443-10-11', court: 'Toulouse', libelle: '11 octobre 1443 : le parlement de Toulouse, premier parlement de province durable', lien: '#paris-et-province' },
  { date: '1593-06-28', court: 'Lemaistre', libelle: '28 juin 1593 : arrêt Lemaistre, le parlement défend la loi salique contre la Ligue', lien: '#arret-lemaistre' },
  { date: '1604-12-12', court: 'Paulette', libelle: 'Décembre 1604 : la paulette rend les offices pratiquement héréditaires', lien: '#magistrats' },
  { date: '1648-05-13', court: 'Fronde', libelle: '13 mai 1648 : arrêt d’Union, début de la Fronde parlementaire', lien: '#la-fronde' },
  { date: '1673-02-24', court: '1673', libelle: '24 février 1673 : Louis XIV impose d’enregistrer d’abord, de remontrer ensuite', lien: '#declaration-de-1673' },
  { date: '1715-09-02', court: 'Testament', libelle: '2 septembre 1715 : le parlement casse le testament de Louis XIV ; le 15, le Régent lui rend le droit de remontrance', lien: '#la-revanche-de-1715' },
  { date: '1732-09-07', court: 'Unigenitus', libelle: '1730-1732 : la bulle Unigenitus, loi de l’État ; grève et exil du parlement', lien: '#unigenitus' },
  { date: '1753-04-09', court: 'Remontrances', libelle: '9 avril 1753 : les Grandes Remontrances sur les refus de sacrements', lien: '#billets-de-confession' },
  { date: '1762-08-06', court: 'Jésuites', libelle: '6 août 1762 : le parlement de Paris condamne la Compagnie de Jésus', lien: '#jesuites' },
  { date: '1766-03-03', court: 'Flagellation', libelle: '3 mars 1766 : séance de la Flagellation, Louis XV rappelle que la souveraineté réside en sa seule personne', lien: '#flagellation' },
  { date: '1771-01-20', court: 'Maupeou', libelle: 'Nuit du 19 au 20 janvier 1771 : les magistrats parisiens exilés, début de la réforme Maupeou', lien: '#le-coup-de-majeste' },
  { date: '1774-11-12', court: 'Rappel', libelle: '12 novembre 1774 : Louis XVI rétablit les anciens parlements', lien: '#rappel-de-1774' },
  { date: '1776-03-12', court: 'Turgot', libelle: '12 mars 1776 : lit de justice pour les édits de Turgot', lien: '#contre-les-reformes' },
  { date: '1787-08-15', court: 'Troyes', libelle: '15 août 1787 : le parlement de Paris exilé à Troyes', lien: '#exil-a-troyes' },
  { date: '1788-05-03', court: '3 mai', libelle: '3 mai 1788 : arrêté du parlement de Paris sur les lois fondamentales', lien: '#3-mai-1788' },
  { date: '1788-06-07', court: 'Tuiles', libelle: '7 juin 1788 : journée des Tuiles à Grenoble ; 21 juillet : assemblée de Vizille', lien: '#journee-des-tuiles' },
  { date: '1788-09-25', court: '1614', libelle: '25 septembre 1788 : le parlement exige des états généraux « suivant la forme observée en 1614 »', lien: '#forme-de-1614' },
  { date: '1789-11-03', court: 'Vacances', libelle: '3 novembre 1789 : la Constituante met les parlements en vacances', lien: '#mise-en-vacances' },
  { date: '1790-08-16', court: 'Fin', libelle: '16-24 août 1790 : loi sur l’organisation judiciaire ; les parlements disparaissent à l’automne 1790', lien: '#suppression' },
];

// --- Carte ---------------------------------------------------------------

/** Ressorts (zones de la carte), d'après les regroupements de scripts/cartes/parlements.py. */
export const zones: Record<string, ZoneCarte> = {
  paris: { libelle: 'Ressort du parlement de Paris', motif: 'blanc', detail: 'Ressort du parlement de Paris (simplifié) : de la Picardie à l’Auvergne et au Lyonnais, environ un tiers du royaume' },
  rouen: { libelle: 'Parlement de Rouen', motif: 'hachures', detail: 'Ressort du parlement de Rouen (Normandie)' },
  rennes: { libelle: 'Parlement de Rennes', motif: 'moyen', detail: 'Ressort du parlement de Rennes (Bretagne)' },
  bordeaux: { libelle: 'Parlement de Bordeaux', motif: 'points', detail: 'Ressort du parlement de Bordeaux (Guyenne, Périgord, Saintonge, Limousin…, simplifié)' },
  toulouse: { libelle: 'Parlement de Toulouse', motif: 'clair', detail: 'Ressort du parlement de Toulouse (Languedoc, Quercy, Rouergue, une partie de la Gascogne…, simplifié)' },
  pau: { libelle: 'Parlement de Pau', motif: 'hachures', detail: 'Ressort du parlement de Pau (Béarn et Navarre, simplifié)' },
  aix: { libelle: 'Parlement d’Aix', motif: 'moyen', detail: 'Ressort du parlement d’Aix (Provence)' },
  grenoble: { libelle: 'Parlement de Grenoble', motif: 'points', detail: 'Ressort du parlement de Grenoble (Dauphiné)' },
  dijon: { libelle: 'Parlement de Dijon', motif: 'hachures', detail: 'Ressort du parlement de Dijon (Bourgogne, Bresse, Bugey, simplifié)' },
  besancon: { libelle: 'Parlement de Besançon', motif: 'moyen', detail: 'Ressort du parlement de Besançon (Franche-Comté)' },
  metz: { libelle: 'Parlement de Metz', motif: 'points', detail: 'Ressort du parlement de Metz (Trois-Évêchés, très simplifié)' },
  nancy: { libelle: 'Parlement de Nancy', motif: 'clair', detail: 'Ressort du parlement de Nancy (Lorraine et Barrois, simplifié)' },
  douai: { libelle: 'Parlement de Douai', motif: 'moyen', detail: 'Ressort du parlement de Douai, dit de Flandre' },
  colmar: { libelle: 'Conseil souverain d’Alsace', motif: 'hachures', detail: 'Ressort du conseil souverain d’Alsace, à Colmar' },
  perpignan: { libelle: 'Conseil souverain du Roussillon', motif: 'moyen', detail: 'Ressort du conseil souverain du Roussillon, à Perpignan' },
  bastia: { libelle: 'Conseil supérieur de Corse', motif: 'clair', detail: 'Ressort du conseil supérieur de Corse, à Bastia' },
  hors: { libelle: 'Hors du royaume', motif: 'hors', detail: 'Hors du royaume en 1789 : Savoie et comté de Nice, États du roi de Sardaigne (réunis à la France en 1860)' },
};

/** Sièges des cours (coordonnées réelles), dans l'ordre de création. */
export const lieux: LieuCarte[] = [
  { id: 'paris', nom: 'Paris', lon: 2.3455, lat: 48.8559, type: 'principal', date: 'XIIIe s.', position: 'e', liste: true, detail: 'Paris : le parlement, issu de la cour du roi, fixé au palais de la Cité au XIVe siècle' },
  { id: 'toulouse', nom: 'Toulouse', lon: 1.444, lat: 43.6045, type: 'principal', date: '1443', position: 'o', liste: true, detail: 'Toulouse : 1443 (un premier essai en 1420-1428), le premier parlement de province' },
  { id: 'grenoble', nom: 'Grenoble', lon: 5.7245, lat: 45.1885, type: 'principal', date: '1453', position: 'o', liste: true, detail: 'Grenoble : 1453, ancien conseil delphinal devenu parlement du Dauphiné' },
  { id: 'bordeaux', nom: 'Bordeaux', lon: -0.5792, lat: 44.8378, type: 'principal', date: '1462', position: 'e', liste: true, detail: 'Bordeaux : 1462 (une première cour en 1451), après la reconquête de la Guyenne' },
  { id: 'dijon', nom: 'Dijon', lon: 5.0415, lat: 47.322, type: 'principal', date: '1477', position: 'o', liste: true, detail: 'Dijon : 1477, après la réunion de la Bourgogne' },
  { id: 'rouen', nom: 'Rouen', lon: 1.0993, lat: 49.4431, type: 'principal', date: '1499', position: 'n', liste: true, detail: 'Rouen : 1499, l’Échiquier de Normandie devenu permanent (nommé parlement en 1515)' },
  { id: 'aix', nom: 'Aix', lon: 5.4474, lat: 43.5297, type: 'principal', date: '1501', position: 'e', liste: true, detail: 'Aix : 1501, parlement de Provence' },
  { id: 'rennes', nom: 'Rennes', lon: -1.6778, lat: 48.1173, type: 'principal', date: '1554', position: 'e', liste: true, detail: 'Rennes : 1554, parlement de Bretagne' },
  { id: 'pau', nom: 'Pau', lon: -0.3708, lat: 43.2951, type: 'principal', date: '1620', position: 'e', liste: true, detail: 'Pau : 1620, parlement de Navarre, après la réunion du Béarn' },
  { id: 'metz', nom: 'Metz', lon: 6.1757, lat: 49.1193, type: 'principal', date: '1633', position: 'n', liste: true, detail: 'Metz : 1633, pour les Trois-Évêchés (supprimé en 1771, rétabli en 1775)' },
  { id: 'colmar', nom: 'Colmar', lon: 7.3585, lat: 48.0794, type: 'secondaire', date: '1657', position: 'ne', liste: true, detail: 'Colmar : conseil souverain d’Alsace, créé en 1657 à Ensisheim, à Colmar depuis 1698' },
  { id: 'perpignan', nom: 'Perpignan', lon: 2.8948, lat: 42.6887, type: 'secondaire', date: '1660', position: 'e', liste: true, detail: 'Perpignan : conseil souverain du Roussillon, 1660, après le traité des Pyrénées' },
  { id: 'douai', nom: 'Douai', lon: 3.08, lat: 50.3714, type: 'principal', date: '1668', position: 'e', liste: true, detail: 'Douai : parlement de Flandre, créé à Tournai en 1668 (conseil souverain, parlement en 1686), à Douai depuis 1714' },
  { id: 'besancon', nom: 'Besançon', lon: 6.0241, lat: 47.2378, type: 'principal', date: '1676', position: 's', liste: true, detail: 'Besançon : 1676, l’ancien parlement de Dole transféré après la conquête de la Franche-Comté' },
  { id: 'bastia', nom: 'Bastia', lon: 9.4509, lat: 42.697, type: 'secondaire', date: '1768', position: 'o', liste: true, detail: 'Bastia : conseil supérieur de Corse, 1768, après l’achat de l’île à Gênes' },
  { id: 'nancy', nom: 'Nancy', lon: 6.1844, lat: 48.6921, type: 'principal', date: '1775', position: 'so', liste: true, detail: 'Nancy : parlement en 1775, héritier de la cour souveraine des ducs de Lorraine' },
  { id: 'arras', nom: 'Arras', lon: 2.7775, lat: 50.291, type: 'autre', position: 'o', detail: 'Arras : conseil provincial d’Artois, cour qui juge souverainement certaines affaires, les autres allant en appel à Paris' },
  { id: 'avignon', nom: 'Avignon', lon: 4.8055, lat: 43.9493, type: 'hors', position: 'n', detail: 'Avignon et le Comtat Venaissin : terres du pape, enclavées dans le royaume (réunies en 1791)' },
  { id: 'mulhouse', nom: 'Mulhouse', lon: 7.3359, lat: 47.7508, type: 'hors', position: 'e', detail: 'Mulhouse : petite république alliée des cantons suisses (réunie en 1798)' },
  { id: 'montbeliard', nom: 'Montbéliard', lon: 6.7983, lat: 47.51, type: 'hors', position: 'se', detail: 'Montbéliard : principauté des ducs de Wurtemberg (réunie en 1793)' },
];

// --- Glossaire et personnages ------------------------------------------------

export interface Terme { id: string; terme: string; definition: string }

/** Glossaire (ancre : #glossaire-<id>). Ordre alphabétique. */
export const glossaire: Terme[] = [
  { id: 'arret-de-reglement', terme: 'Arrêt de règlement', definition: 'Décision générale qu’un parlement prend de lui-même, toutes chambres assemblées, et qui s’impose dans son ressort comme une loi (sur la procédure, la police des grains, les métiers…). Le Code civil de 1804 l’interdit aux juges.' },
  { id: 'billets-de-confession', terme: 'Billets de confession', definition: 'Certificats exigés des mourants, surtout à Paris à partir de 1749-1752, prouvant qu’ils s’étaient confessés à un prêtre acceptant la bulle *Unigenitus*. Sans billet, pas de derniers sacrements : les parlements poursuivent les curés qui les refusent.' },
  { id: 'chambre-des-vacations', terme: 'Chambre des vacations', definition: 'Petite chambre qui expédie les affaires urgentes pendant les vacances judiciaires (de septembre à novembre). En novembre 1789, la Constituante ne laisse subsister que ces chambres.' },
  { id: 'conseil-souverain', terme: 'Conseil souverain', definition: 'Cour qui juge en dernier ressort comme un parlement, sans en porter le nom, dans une province réunie tardivement : Alsace (Colmar), Roussillon (Perpignan) ; en Corse, conseil supérieur (Bastia).' },
  { id: 'conseils-superieurs', terme: 'Conseils supérieurs', definition: 'Cours d’appel créées par Maupeou en 1771 pour découper l’immense ressort du parlement de Paris (Arras, Blois, Châlons, Clermont, Lyon, Poitiers) ; leurs juges, nommés et payés par le roi, ne prennent pas d’épices. Supprimées en 1774.' },
  { id: 'cour-souveraine', terme: 'Cour souveraine', definition: 'Tribunal qui juge en dernier ressort, au nom du roi : parlements, mais aussi chambres des comptes, cours des aides, Grand Conseil. Louis XIV les rebaptise « cours supérieures » pour rappeler que seul le roi est souverain.' },
  { id: 'enregistrement', terme: 'Enregistrement', definition: 'Copie d’un acte du roi (ordonnance, édit, déclaration, lettres patentes) sur les registres d’une cour, après examen (« vérification »). Il vaut publication : sans lui, le texte ne s’applique pas dans le ressort de la cour.' },
  { id: 'epices', terme: 'Épices', definition: 'À l’origine, cadeaux de dragées et d’épices offerts aux juges par les plaideurs ; devenus des honoraires obligatoires, en argent, payés aux magistrats pour chaque procès.' },
  { id: 'evocation', terme: 'Évocation', definition: 'Décision du roi de retirer une affaire à un tribunal pour la faire juger par son Conseil ou par des commissaires : c’est la « justice retenue » à l’œuvre.' },
  { id: 'gallicanisme', terme: 'Gallicanisme', definition: 'Doctrine qui défend les « libertés de l’Église gallicane » : le pape n’a aucun pouvoir sur le temporel du roi, et son autorité en France est limitée par les usages du royaume. Les parlements en sont les gardiens les plus jaloux.' },
  { id: 'gens-du-roi', terme: 'Gens du roi (parquet)', definition: 'Le procureur général et les avocats généraux, qui défendent dans chaque cour les intérêts du roi et de la société ; leurs substituts forment le « parquet ». Ils portent au parlement les actes à enregistrer.' },
  { id: 'grand-chambre', terme: 'Grand-Chambre', definition: 'La chambre principale d’un parlement, où siègent le premier président, les présidents à mortier et les conseillers les plus anciens. Elle juge les causes majeures ; le roi y tient ses lits de justice.' },
  { id: 'jansenisme', terme: 'Jansénisme', definition: 'Courant catholique austère, né des thèses de l’évêque Jansénius (1640) et de l’abbaye de Port-Royal, qui insiste sur la grâce divine et la rigueur morale. Persécuté par Louis XIV et par Rome, il trouve des appuis dans les parlements au XVIIIe siècle.' },
  { id: 'lettre-de-cachet', terme: 'Lettre de cachet', definition: 'Ordre du roi, fermé de son cachet, adressé à une personne : exil, emprisonnement sans jugement, convocation. Elle sert notamment à exiler les magistrats récalcitrants.' },
  { id: 'lettres-de-jussion', terme: 'Lettres de jussion', definition: 'Lettres par lesquelles le roi ordonne à une cour d’enregistrer sans délai un acte qu’elle refuse ou retarde.' },
  { id: 'lit-de-justice', terme: 'Lit de justice', definition: 'Séance solennelle où le roi vient en personne au parlement (ou le convoque auprès de lui) et fait enregistrer un acte par son exprès commandement : la justice déléguée cesse quand le roi est présent. Le nom vient du dais et des coussins sur lesquels il siège.' },
  { id: 'lois-fondamentales', terme: 'Lois fondamentales', definition: 'Règles non écrites que le roi lui-même ne peut changer : succession de mâle en mâle par ordre de primogéniture (loi dite salique), catholicité du roi, inaliénabilité du domaine. Au XVIIIe siècle, les parlements y ajoutent le consentement à l’impôt ou l’inamovibilité des juges.' },
  { id: 'noblesse-de-robe', terme: 'Noblesse de robe', definition: 'Noblesse acquise par l’exercice de certaines charges de justice et de finance, en particulier dans les cours souveraines ; elle se distingue de la noblesse d’épée, d’origine militaire, avec laquelle elle finit par se confondre.' },
  { id: 'office', terme: 'Office', definition: 'Charge publique permanente (juge, greffier, receveur…) dont le titulaire, l’officier, est propriétaire : il l’a achetée et peut la revendre ou la transmettre. Un officier ne peut pas être révoqué, sauf pour forfaiture jugée.' },
  { id: 'parlement', terme: 'Parlement', definition: 'Sous l’Ancien Régime, cour de justice souveraine qui juge en appel et en dernier ressort au nom du roi, et enregistre ses lois. Rien à voir avec une assemblée élue : ses membres sont des magistrats propriétaires de leur charge. Il y en a treize en 1789.' },
  { id: 'paulette', terme: 'Paulette', definition: 'Droit annuel créé en décembre 1604 (du nom du financier Charles Paulet) : moyennant un soixantième de la valeur de son office chaque année, l’officier peut le transmettre à qui il veut, même s’il meurt subitement.' },
  { id: 'premier-president', terme: 'Premier président', definition: 'Chef d’un parlement, choisi par le roi ; c’est le seul magistrat de la cour dont la charge n’est pas achetée. Il préside la Grand-Chambre et parle au nom de la compagnie.' },
  { id: 'presidents-a-mortier', terme: 'Présidents à mortier', definition: 'Présidents de la Grand-Chambre, qui portent un bonnet de velours noir galonné d’or, le mortier. Leurs charges, très chères, sont réservées à quelques grandes familles.' },
  { id: 'remontrances', terme: 'Remontrances', definition: 'Observations écrites ou orales qu’une cour adresse au roi sur un acte qu’on lui demande d’enregistrer, pour en montrer les défauts et en demander le retrait ou la modification. Répétées, elles deviennent « itératives ».' },
  { id: 'ressort', terme: 'Ressort', definition: 'Territoire sur lequel s’étend la compétence d’une cour : les appels de tous les tribunaux de ce territoire « ressortissent » à elle.' },
  { id: 'tournelle', terme: 'Tournelle', definition: 'Chambre criminelle d’un parlement, où les conseillers siègent à tour de rôle. Elle juge en appel les procès criminels graves.' },
  { id: 'unigenitus', terme: '*Unigenitus*', definition: 'Bulle du pape Clément XI (1713), demandée par Louis XIV, qui condamne 101 propositions d’un livre janséniste du père Quesnel. Déclarée loi de l’État en 1730, elle divise l’Église de France et dresse les parlements contre les évêques.' },
  { id: 'venalite', terme: 'Vénalité des offices', definition: 'Pratique qui consiste à vendre les charges publiques : le roi en tire de l’argent, les acheteurs un revenu, un rang et parfois la noblesse. Généralisée au XVIe siècle, elle est abolie dans la nuit du 4 août 1789.' },
  { id: 'vingtieme', terme: 'Vingtième', definition: 'Impôt créé en 1749 par le contrôleur général Machault : un vingtième (5 %) des revenus, dû en principe par tous, privilégiés compris. Les parlements et le clergé le combattent ; il est doublé, puis triplé en temps de guerre.' },
];

export interface Personnage { id: string; nom: string; dates: string; role: string }

/** Personnages (ancre : #personnage-<id>). Ordre chronologique. */
export const personnages: Personnage[] = [
  { id: 'saint-louis', nom: 'Louis IX (Saint Louis)', dates: '1214-1270', role: 'Roi de France de 1226 à 1270. Sous son règne, la cour du roi tient régulièrement des sessions judiciaires « en parlement », ouvertes aux appels venus des baillis et des sénéchaux : c’est la naissance du parlement de Paris. Canonisé en 1297.' },
  { id: 'mole', nom: 'Mathieu Molé', dates: '1584-1656', role: 'Premier président du parlement de Paris de 1641 à 1653, puis garde des Sceaux. Pendant la Fronde, il défend les droits de sa compagnie tout en cherchant à ménager la régente ; son sang-froid face aux émeutiers est resté légendaire.' },
  { id: 'broussel', nom: 'Pierre Broussel', dates: 'vers 1575-1654', role: 'Vieux conseiller de la Grand-Chambre, très populaire à Paris pour son opposition aux impôts de Mazarin. Son arrestation, le 26 août 1648, provoque la journée des Barricades.' },
  { id: 'louis-xiv', nom: 'Louis XIV', dates: '1638-1715', role: 'Roi de 1643 à 1715. Marqué par la Fronde, il réduit les parlements au silence : ses ordonnances de 1667 et surtout sa déclaration du 24 février 1673 les obligent à enregistrer avant de remontrer. Son testament est cassé par le parlement au lendemain de sa mort.' },
  { id: 'regent', nom: 'Philippe d’Orléans, le Régent', dates: '1674-1723', role: 'Neveu de Louis XIV, régent pendant la minorité de Louis XV (1715-1723). Pour obtenir du parlement les pleins pouvoirs que lui refusait le testament du feu roi, il rend aux cours le droit de remontrance préalable ; il doit ensuite les combattre.' },
  { id: 'montesquieu', nom: 'Montesquieu', dates: '1689-1755', role: 'Charles-Louis de Secondat, baron de La Brède et de Montesquieu, président à mortier au parlement de Bordeaux de 1716 à 1726. *De l’esprit des lois* (1748) fait des corps intermédiaires, et d’un « dépôt des lois », les garanties d’une monarchie modérée : les parlementaires y liront leur propre éloge.' },
  { id: 'louis-xv', nom: 'Louis XV', dates: '1710-1774', role: 'Roi de 1715 à 1774. Il hésite longtemps entre fermeté et concessions face aux parlements, les rappelle à l’ordre dans la séance de la Flagellation (1766), puis laisse Maupeou les briser en 1771.' },
  { id: 'la-chalotais', nom: 'La Chalotais', dates: '1701-1785', role: 'Louis-René de Caradeuc de La Chalotais, procureur général au parlement de Bretagne, adversaire des jésuites et du commandant de la province, le duc d’Aiguillon. Son arrestation en 1765 fait de lui un martyr de la cause parlementaire.' },
  { id: 'maupeou', nom: 'René-Nicolas de Maupeou', dates: '1714-1792', role: 'Issu d’une dynastie de magistrats, premier président du parlement de Paris, puis chancelier de France (1768). En 1771, il exile les parlementaires, supprime la vénalité dans les nouvelles cours et rend la justice gratuite. Renvoyé par Louis XVI en 1774.' },
  { id: 'malesherbes', nom: 'Malesherbes', dates: '1721-1794', role: 'Chrétien-Guillaume de Lamoignon de Malesherbes, premier président de la Cour des aides de Paris, auteur de remontrances célèbres contre Maupeou (1771) et contre l’arbitraire fiscal (1775). Ministre de Louis XVI, puis son défenseur devant la Convention (1792), il est guillotiné en avril 1794.' },
  { id: 'louis-xvi', nom: 'Louis XVI', dates: '1754-1793', role: 'Roi de 1774 à 1792. Il rappelle les parlements dès 1774 pour gagner l’opinion, puis se heurte à eux à chaque tentative de réforme fiscale, jusqu’à céder en 1788 en convoquant les états généraux.' },
  { id: 'brienne', nom: 'Loménie de Brienne', dates: '1727-1794', role: 'Étienne-Charles de Loménie de Brienne, archevêque de Toulouse, principal ministre de mai 1787 à août 1788. Il exile le parlement de Paris à Troyes (1787), soutient la réforme de Lamoignon (1788), puis doit annoncer les états généraux.' },
  { id: 'lamoignon', nom: 'Lamoignon', dates: '1735-1789', role: 'Chrétien-François II de Lamoignon, ancien président à mortier, garde des Sceaux de 1787 à 1788. Ses édits de mai 1788 retirent aux parlements l’enregistrement et une grande partie de leurs procès. Renvoyé en septembre 1788, il meurt en mai 1789.' },
  { id: 'epremesnil', nom: 'Jean-Jacques Duval d’Eprémesnil', dates: '1745-1794', role: 'Conseiller au parlement de Paris, orateur fougueux de la résistance au ministère en 1787-1788 : il fait voter l’arrêté du 3 mai 1788 et se laisse arrêter en pleine séance. Député de la noblesse en 1789, hostile à la Révolution, il est guillotiné en 1794.' },
  { id: 'mounier', nom: 'Jean-Joseph Mounier', dates: '1758-1806', role: 'Juge royal à Grenoble, animateur de l’assemblée de Vizille (21 juillet 1788). Député du tiers en 1789, il propose le serment du Jeu de paume, puis quitte l’Assemblée après les journées d’octobre.' },
  { id: 'barnave', nom: 'Antoine Barnave', dates: '1761-1793', role: 'Jeune avocat au parlement de Grenoble, on lui attribue un pamphlet contre les édits de mai 1788. Député du tiers, grand orateur de la Constituante, il devient le conseiller secret de la reine après Varennes ; il est guillotiné en novembre 1793.' },
];
