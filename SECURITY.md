# Politique de sécurité

## Versions prises en charge

Ce dépôt correspond à un projet pédagogique.  
La version prise en charge est la version la plus récente disponible sur la branche principale du projet.

| Version | Prise en charge |
| ------- | --------------- |
| `main` | :white_check_mark: |
| Tags récents du projet | :white_check_mark: |
| Anciennes branches de travail | :x: |

## Signaler une vulnérabilité

Si vous identifiez une vulnérabilité ou un risque de sécurité, merci de ne pas le publier immédiatement dans une issue publique.

Merci de transmettre au minimum :

- une description du problème ;
- les composants concernés ;
- les étapes de reproduction si possible ;
- l’impact estimé.

Canal recommandé :
- contacter le mainteneur du dépôt ;
- ou utiliser un canal privé si disponible.

## Ce qui est déjà en place

Le projet applique déjà plusieurs mesures simples :

- clé API sur les routes métier ;
- secrets non versionnés dans le dépôt ;
- utilisation de variables d’environnement ;
- tests automatisés ;
- surveillance des dépendances via GitHub.

## Limites actuelles

Ce projet reste un projet étudiant, pas une application de production complète.

Quelques limites connues :
- authentification simple par clé API ;
- sécurité de déploiement perfectible ;
- persistance distante limitée selon l’environnement.

## Améliorations possibles

Si le projet devait évoluer, les pistes prioritaires seraient :

- renforcer l’authentification ;
- améliorer la gestion des secrets ;
- formaliser davantage la maintenance de sécurité ;
- renforcer le déploiement pour un usage réel.
