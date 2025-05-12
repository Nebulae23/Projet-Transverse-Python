# Magic Survivor


## 📖 Présentation

Magic Survivor est un jeu de rôle et de survie qui combine des éléments d'exploration, de gestion de ressources et de combat. Le joueur incarne un mage qui doit protéger sa cité contre des vagues d'ennemis tout en explorant un monde ouvert riche en découvertes.

### Principales caractéristiques

- **Cycle jour/nuit** : Explorez la carte pendant la journée pour collecter des ressources, puis défendez votre cité contre des vagues d'ennemis pendant la nuit.
- **Système de sorts** : Débloquez et améliorez des sorts magiques pour combattre vos ennemis.
- **Construction de cité** : Développez votre cité en construisant diverses structures qui vous apporteront des bonus et des avantages.
- **Monde ouvert** : Explorez une carte générée avec différents types de terrain, des points d'intérêt et des ressources à collecter.
- **Système de reliques** : Découvrez des reliques qui confèrent des capacités uniques à votre personnage.
- **Progression du personnage** : Améliorez votre personnage en gagnant de l'expérience et en trouvant de l'équipement.

## 🎮 Comment jouer

### Contrôles

- **ZQSD** / **Flèches directionnelles** : Déplacement du personnage
- **F** : Interagir avec des objets et des points d'intérêt
- **Espace** : Attaque principale
- **1-5** : Utiliser les sorts équipés
- **E** : Ouvrir l'inventaire
- **C** : Afficher les statistiques du personnage
- **M** : Afficher/Cacher la mini-carte
- **Échap** : Menu pause

### Objectifs

1. Survivez aussi longtemps que possible en défendant votre cité contre les attaques nocturnes.
2. Explorez le monde à la recherche de ressources, de reliques et de points d'intérêt.
3. Développez votre cité pour obtenir des avantages stratégiques.
4. Améliorez votre personnage pour affronter des ennemis toujours plus puissants.

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Pygame 2.0.0 ou supérieur

### Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/Nebulae23/Projet-Transverse-Python
   cd Projet_transverse
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancez le jeu :
   ```bash
   python main.py
   ```

## 🧰 Développement

### Structure du projet

```
main.py                # Point d'entrée du jeu
README.md              # Documentation du projet
requirements.txt       # Dépendances Python
assets/                # Ressources graphiques et sonores
  ├── fonts/           # Polices de caractères
  ├── sounds/          # Sons et musiques
  │   ├── effects/     # Effets sonores
  │   └── music/       # Musiques de fond
  └── sprites/         # Images et sprites
data/                  # Données du jeu (JSON)
src/                   # Code source
  ├── editor/          # Éditeur de niveau et de données
  └── states/          # États du jeu (menu, jeu, pause)
```

### Extensibilité

Le jeu est conçu pour être facilement extensible :
- Ajoutez de nouveaux types d'ennemis dans `data/enemies.json`
- Créez de nouveaux sorts dans `data/spells.json`
- Définissez de nouvelles reliques dans `data/relics.json`
- Ajoutez des bâtiments dans `data/city_buildings.json`


## 👥 Crédits

Développé par :

- [@Jeremie](https://github.com/jeremiel1110)
- [@Aaron](https://github.com/Joeeeemamaa)
- [@Marine](https://github.com/Marine-Be)
- [@Medhi](https://github.com/TierSnow)
- [@Artus](https://github.com/Nebulae23)

---

*Magic Survivor - Version 7.0 - Mai 2025*
