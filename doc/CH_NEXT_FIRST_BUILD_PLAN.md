# Premier build suisse avec le générateur `next` — plan initial

Une première implémentation et ses résultats sont documentés dans
[CH_NEXT_PREVIEW.md](CH_NEXT_PREVIEW.md). Le contrôle initial a révélé 145
références du cours absentes du catalogue suisse courant ; elles restent
visibles dans le prototype et devront être traitées séparément.

## Objectif et périmètre

Créer, **après validation de ce plan**, une branche locale `next/ch` issue de
`next`. Elle servira à construire et examiner une première version suisse avec
la chaîne DARCdown → MDX → Astro. Le résultat sera un prototype local, sans
publication ni modification des sources canoniques. Les changements réutilisables
pourront ensuite être proposés à `next` ; ce test n'est pas une refonte préalable
en plateforme universelle.

Le premier essai portera sur le **cours allemand dans ses trois éditions
suisses** : `NE` (HB3), `A` (upgrade HB3 → HB9) et `NEA` (cours complet).
Le français, l'italien et la publication seront examinés après ce premier
résultat.

## Entrées suisses

- Le contenu du cours vient du canonical de `50ohm-contents-ch`, reconstruit
  dans une entrée temporaire pour le générateur. Les questions viennent du
  canonical distinct de `50ohm-question-pool`. Le build doit enregistrer les
  révisions réellement utilisées et ne pas lire silencieusement une ancienne
  copie.
- Le catalogue courant préparé s'appelle `fragenkatalog_4.json` et contient
  1 665 questions. L'entrée contient aussi `fragenkatalog3b.json`, qui en
  contient 1 750 et **ne doit pas être sélectionné par défaut pour ce test**.
  Le chemin du catalogue doit être configurable.
- `metadata3b.json` existe déjà dans `50ohm-contents-ch`. Ses 1 750 entrées
  couvrent 1 523 questions du catalogue courant. Pour le build suisse, produire
  un fichier dérivé couvrant les 1 665 questions : conserver les métadonnées
  existantes et compléter les 142 entrées manquantes sans écrire dans le
  canonical. Parmi ces dernières, `AI307` référence le dessin 57 et `EI305` et
  `EI306` le dessin 36 ; les SVG sont présents dans l'entrée préparée. Les
  valeurs de `layout` et les cinq champs d'image doivent être explicites. Le
  prototype doit signaler une référence d'image introuvable.
- Les entrées `work/generator-input/{de,fr,it}` inspectées ont été préparées
  le 12 octobre 2026. Il faut les recréer depuis l'état choisi du canonical
  avant de mesurer le résultat. Le test doit écrire ses sorties dans des
  répertoires de travail ignorés par Git.

## Adaptations ciblées de `next/ch`

1. **Catalogue de questions** : rendre son nom configurable et sélectionner
   explicitement le catalogue suisse courant. Vérifier que les 1 665 questions
   sont présentes dans le JSON MDX/Astro, y compris les 142 nouvelles par
   rapport aux métadonnées historiques. Une question référencée dans une
   section ne doit pas être perdue.
2. **Classe des questions** : toutes les questions canoniques actuelles portent
   `class: 0`. La conversion MDX de `next` ne convertit que `1/2/3` en `N/E/A`
   et omet donc ce champ pour `0`. Le site Astro ne lit ensuite pas cette classe
   pour sélectionner ou afficher les questions ; seul son schéma la rend
   obligatoire. Pour ce premier test, rendre le champ facultatif dans ce
   schéma. Ne pas inventer de correspondance `0 → N/E/A` ni de nouveau filtrage
   par classe de question. La conservation éventuelle de `0` dans le JSON sera
   une décision distincte.
3. **Ordre des réponses** : dans le frontend Astro, le mélange est déclenché
   par un appel à `shuffle(answers)` au chargement de la page. Introduire un
   paramètre de build explicite qui rende cet appel conditionnel. Pour le test
   et la revue suisse, le désactiver : les réponses restent dans l'ordre du
   catalogue, avec A comme bonne réponse. Conserver le comportement actuel
   comme valeur par défaut hors configuration suisse.
4. **Parcours du cours** : la classe d'une *section* est indépendante de celle
   d'une question. Le site suisse actuel construit `A` (passage HB3 → HB9),
   `NE` (HB3) et `NEA` (cours complet) depuis un seul `toc/HB.json`. Une section
   N appartient à NE et NEA, une section E à NE et NEA, une section A à A et
   NEA. Pour les trois éditions du premier build, adapter la lecture du TOC
   et la sélection des sections selon cette règle. `HB.json` ne fournit ni titre ni résumé à
   sa racine : fournir ces informations par configuration. Ne pas confondre
   cette sélection de sections avec `class: 0` des questions.

## Vérification du premier résultat

Le build Python doit produire le MDX, les questions, les images et les deux
index de recherche ; Astro doit ensuite construire les pages sans erreur de
schéma. Vérifier au minimum une section avec question, une question sans
métadonnées historiques, les quatre réponses dans l'ordre A–D, les liens et
une image. Contrôler également que chacune des trois éditions contient les
sections prévues et qu'aucune question référencée ne manque.

Les pages allemandes spécifiques, les URLs absolues, les fonctions Astro non
encore portées, puis le français et l'italien feront l'objet d'un inventaire
séparé à partir de ce résultat. Une réussite technique du build ne vaudra pas
validation éditoriale ou autorisation de publier.

L'implémentation a été autorisée le 16 octobre 2026 sur la branche `next/ch`.
