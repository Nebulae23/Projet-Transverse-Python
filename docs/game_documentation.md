# Documentation de Magic Survivor

Bienvenue dans le monde de Magic Survivor ! Ce document détaille les mécaniques de jeu principales pour vous aider à comprendre et maîtriser les défis qui vous attendent.

## Cycle Jour/Nuit

Le jeu est rythmé par une alternance entre deux phases distinctes : le jour et la nuit.

### Phase de Jour

Pendant la journée, le danger est moindre et vous pouvez vous concentrer sur la préparation et le développement.

*   **Gestion de la Ville :**
    *   Accédez à l'interface de votre ville pour construire de nouveaux bâtiments ou améliorer ceux existants.
    *   Les bâtiments peuvent servir à la production de ressources, à la défense de la ville, ou offrir divers avantages utilitaires.
    *   La gestion des ressources est cruciale pour l'expansion de votre ville.
*   **Exploration du Monde :**
    *   Aventurez-vous sur une vaste carte du monde composée de tuiles.
    *   Collectez des ressources précieuses à partir de nœuds de ressources spécifiques.
    *   Découvrez et interagissez avec des points d'intérêt qui peuvent déclencher des événements ou offrir des récompenses.
    *   Une mini-carte se dévoile au fur et à mesure de votre exploration.
*   **Gestion du Personnage :**
    *   Gérez l'équipement de votre personnage.
    *   Vous aurez la possibilité d'améliorer vos sorts existants ou d'en apprendre de nouveaux.
*   **Progression Temporelle :**
    *   Un minuteur indique le temps restant avant la tombée de la nuit.
    *   Pendant ce temps, vos bâtiments de production génèrent passivement des ressources.

### Phase de Nuit

Lorsque la nuit tombe, le monde devient hostile et votre survie est mise à l'épreuve.

*   **Combat et Survie :**
    *   Préparez-vous à affronter des vagues d'ennemis qui attaqueront à la fois votre personnage et votre ville.
*   **Défense de la Ville :**
    *   Votre ville possède des points de vie et des structures défensives (murs).
    *   Les ennemis tenteront de percer vos défenses et d'endommager la ville. Protégez-la à tout prix !
*   **Mécaniques de Combat du Joueur :**
    *   Utilisez un arsenal de sorts et vos attaques de base pour repousser les assaillants.
    *   Les projectiles que vous et vos ennemis lancez sont gérés par un système dédié.
    *   Les reliques que vous avez collectées fournissent des bonus passifs et peuvent parfois débloquer des capacités actives puissantes.
*   **Progression de la Nuit :**
    *   Si vous survivez à toutes les vagues d'ennemis, la nuit prend fin.
    *   Entre les vagues, ou à la fin de la nuit, vous pourriez avoir l'opportunité de choisir de nouvelles reliques pour renforcer votre personnage.

## Gestion du Joueur

Votre personnage est au centre de l'aventure et sa progression est essentielle.

*   **Statistiques et Progression :**
    *   Votre personnage possède plusieurs statistiques : points de vie (HP), expérience (XP), niveau, vitesse de déplacement, dégâts, etc.
    *   En éliminant des ennemis, vous gagnez de l'XP. Accumuler suffisamment d'XP vous fait monter de niveau.
    *   Chaque montée de niveau améliore vos statistiques et vous soigne complètement.
*   **Équipement :**
    *   Vous pouvez équiper différents sorts et reliques.
    *   Ces équipements influencent directement vos capacités de combat et vos statistiques.
*   **Contrôles et Animation :**
    *   Vous contrôlez directement les mouvements de votre personnage.
    *   Ses animations s'adaptent à ses actions (ralenti, marche, attaque).

## Systèmes de Jeu Détaillés

Plusieurs systèmes interconnectés enrichissent l'expérience de jeu.

### Sorts
*   Les sorts sont votre principal moyen d'attaque et de défense. Ils possèdent des caractéristiques variées : dégâts, temps de recharge (cooldown), type (feu, glace, etc.).
*   Vous pouvez améliorer vos sorts ou les "diverger" pour obtenir des effets modifiés et plus puissants.
*   Certains sorts peuvent être lancés automatiquement, tandis que d'autres nécessitent une activation manuelle.
*   La fusion de sorts pour en créer de nouveaux est une possibilité à explorer.

### Reliques
*   Les reliques sont des objets passifs qui fournissent des bonus statistiques constants à votre personnage.
*   Certaines reliques peuvent également octroyer des capacités actives uniques.
*   Elles sont généralement obtenues en récompense, avec un système de choix basé sur leur rareté.

### Ennemis
*   Vous affronterez une variété d'ennemis, chacun avec ses propres statistiques, comportements et capacités.
*   Ils apparaissent en vagues successives pendant la phase de nuit.

### Projectiles
*   Un système dédié gère la physique, le mouvement et les collisions de tous les projectiles (ceux du joueur et ceux des ennemis).

### Bâtiments
*   Les bâtiments de votre ville peuvent être construits et améliorés.
*   Chaque bâtiment a un coût de construction/amélioration, des prérequis potentiels, et des effets spécifiques (production de ressources, amélioration des défenses, bonus passifs pour le joueur ou la ville).

## Monde et Éléments Interactifs

L'univers de Magic Survivor est vaste et rempli d'éléments à découvrir.

*   **Carte du Monde :**
    *   La carte est générée avec différents biomes, offrant une diversité d'environnements.
    *   Elle peut contenir des éléments de décor (`StaticProp`), des nœuds de ressources (`ResourceNode`) à collecter, et des points d'intérêt (`PointOfInterest`) qui peuvent déclencher des événements ou des interactions spéciales.
*   **Ville :**
    *   Votre ville est un emplacement central sur la carte du monde.
    *   Elle dispose d'une entrée et est protégée par des murs défensifs.

## Progression et Sauvegarde

Votre avancée dans le jeu est précieuse et peut être sauvegardée.

*   **Gestion des Données :**
    *   Toutes les données de jeu (définitions des objets, sprites, configuration des vagues d'ennemis, etc.) sont chargées à partir de fichiers de configuration (JSON).
    *   Les éléments graphiques (sprites) sont également chargés et gérés par le jeu.
*   **Sauvegarde :**
    *   Votre progression est sauvegardée. Cela inclut : le niveau et l'XP de votre personnage, les bâtiments construits et leur niveau, les sorts et reliques acquis, le jour actuel dans le jeu, vos ressources, et votre position sur la carte du monde.
    *   L'état du monde (nœuds de ressources disponibles, points d'intérêt visités) est également sauvegardé.
    *   La sauvegarde s'effectue typiquement à la fin d'une nuit réussie ou via le menu pause.
*   **Génération de Fichiers par Défaut :**
    *   Si certains fichiers de données sont manquants au lancement du jeu, le système peut en créer des versions par défaut.

## Gestion Globale du Jeu

Le jeu est structuré par un gestionnaire global qui orchestre les différentes phases.

*   **Machine à États :**
    *   Le jeu utilise une machine à états pour passer d'une phase à l'autre (menu principal, exploration de la carte du monde, gestion de l'intérieur de la ville, phase de nuit, menu pause, éditeurs de contenu).
*   **Interface Utilisateur (UI) :**
    *   Un système d'interface utilisateur gère tous les éléments affichés à l'écran, qu'ils soient globaux (présents dans plusieurs états) ou spécifiques à un état de jeu particulier.

## Objectifs Probables du Joueur

Pour réussir dans Magic Survivor, vous devrez viser plusieurs objectifs :

*   **Survivre :** Repoussez les assauts nocturnes en protégeant votre personnage et votre ville.
*   **Développer :** Agrandissez et améliorez votre ville en construisant de nouveaux bâtiments pour augmenter votre production de ressources et obtenir des bonus significatifs.
*   **Explorer :** Parcourez la carte du monde à la recherche de ressources, de points d'intérêt mystérieux, et potentiellement pour faire avancer une trame narrative.
*   **Devenir Plus Puissant :** Améliorez constamment votre personnage en montant de niveau, en acquérant des sorts plus dévastateurs, et en trouvant des reliques dont les effets se combinent de manière optimale.

Bonne chance, Survivant !