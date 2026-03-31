# Documentation du modèle

## 1. Objectif du modèle

Le modèle du projet estime le risque de départ d'un employé à partir d'un ensemble de variables RH, de performance, de satisfaction et d'ancienneté.

Le modèle actuellement déployé est documenté par :

- [`artifacts/model/metadata.json`](../../artifacts/model/metadata.json)
- [`artifacts/model/MLmodel`](../../artifacts/model/MLmodel)
- [`artifacts/model/preprocessing_reference.json`](../../artifacts/model/preprocessing_reference.json)

## 2. Modèle final retenu

Le modèle final exposé par l'API est :

- `model_name` : `linear_svc_attrition`
- `model_version` : `0.1.0`
- méthode de score : `decision_function`
- seuil de décision : `0.1138`

Dans le runtime applicatif, ce modèle est chargé par :

- [`app/ml/loader.py`](../../app/ml/loader.py)
- [`app/ml/predictor.py`](../../app/ml/predictor.py)

## 3. Structure du pipeline

Le pipeline final est un pipeline scikit-learn de type :

1. `StandardScaler`
2. `LinearSVC`

Conséquences importantes :

- le score renvoyé par le modèle est une `decision_function`, pas une probabilité ;
- l'interprétation locale peut être faite proprement par décomposition additive ;
- l'ordre et le nom exact des features d'entrée doivent correspondre strictement à la signature du pipeline.

## 4. À quoi correspond la sortie brute ?

La sortie brute renvoyée par l'API dans le champ `score` correspond au score de marge calculé par `decision_function`.

Concrètement :

- ce score mesure de quel côté de la frontière de décision se situe l'individu ;
- plus le score est élevé, plus le modèle pousse vers la classe `1` ;
- plus le score est faible, plus le modèle pousse vers la classe `0`.

Il ne s'agit pas d'une probabilité :

- un score de `0.5` ne veut pas dire `50 %` de risque ;
- un score négatif ne veut pas dire `risque négatif`, mais simplement une position nette du côté de la classe `0`.

La classe finale est obtenue en comparant ce score au seuil enregistré dans la metadata du modèle :

- `score < threshold`  -> `prediction = 0`
- `score >= threshold` -> `prediction = 1`

Dans certains cas, on peut convertir un score linéaire en pseudo-probabilité à l'aide d'une fonction sigmoïde. Mais ce n'est pas ce que fait ce projet :

- le modèle déployé n'est pas calibré en probabilité ;
- la sortie officielle de l'API reste donc un score brut cohérent avec `decision_function` ;
- cela évite de présenter comme probabiliste une information qui ne l'est pas réellement.

## 5. Feature engineering attendu

Le modèle n'attend pas directement le payload métier brut. Il attend un tableau de features finales reconstruit par [`app/ml/preprocess.py`](../../app/ml/preprocess.py).

Cette étape comprend :

- normalisation des valeurs catégorielles ;
- encodage binaire de certains drapeaux métier ;
- transformations logarithmiques ;
- calcul de ratios ;
- calcul d'indicateurs dérivés ;
- création des colonnes one-hot ;
- réalignement exact sur la liste de features de la metadata.

## 6. Références de preprocessing

Le fichier [`artifacts/model/preprocessing_reference.json`](../../artifacts/model/preprocessing_reference.json) contient les références nécessaires à l'inférence :

- regroupement de certains postes ;
- regroupement de certains domaines d'étude ;
- médianes de revenu par niveau hiérarchique ;
- médianes de revenu par poste regroupé.

Cette décision d'architecture est importante :

- le feature engineering ne dépend plus d'une base de données ni d'un fichier de données brutes au runtime ;
- l'API reste portable en local, en Docker et sur Hugging Face Spaces ;
- le comportement d'inférence reste cohérent avec le notebook d'entraînement.

## 7. Variables principales

La metadata du modèle expose la liste exacte des features finales attendues.

On y retrouve plusieurs familles :

### Variables brutes numériques

- `age`
- `revenu_mensuel`
- `niveau_hierarchique_poste`
- `distance_domicile_travail`
- `niveau_education`

### Variables transformées

- `revenu_mensuel_log`
- `annee_experience_totale_log`
- `annees_dans_l_entreprise_log`
- `annees_dans_le_poste_actuel_log`
- `annees_depuis_la_derniere_promotion_log`
- `annes_sous_responsable_actuel_log`

### Variables dérivées

- `ratio_anciennete_poste`
- `ratio_anciennete_manager`
- `ratio_experience_entreprise`
- `mobilite_interne_potentielle`
- `jamais_promu`
- `retard_promotion_relatif`
- `progression_salariale_faible`
- `revenu_par_niveau`
- `revenu_par_poste`
- `evolution_evaluation`
- `bonne_perf_peu_augmente`

### Variables catégorielles encodées

- `statut_marital_*`
- `departement_*`
- `frequence_deplacement_*`
- `poste_regroupe_*`
- `domaine_etude_regroupe_*`

## 8. Chargement du modèle

Le chargement suit la logique suivante :

1. lecture de la metadata ;
2. résolution robuste du chemin de l'artefact MLflow ;
3. tentative de chargement via `mlflow.sklearn.load_model(...)` ;
4. fallback vers `mlflow.pyfunc.load_model(...)` si nécessaire.

Le projet privilégie le flavor scikit-learn, car il permet de conserver l'accès à :

- `decision_function` ;
- les coefficients linéaires ;
- l'interprétation locale exacte.

## 9. Calcul du score et de la classe

Le scoring est effectué dans [`app/ml/predictor.py`](../../app/ml/predictor.py).

Principe :

1. on calcule le score brut selon la méthode décrite dans la metadata ;
2. on compare ce score au seuil `threshold` ;
3. on produit la classe finale `0` ou `1`.

Important :

- `score` n'est pas une probabilité ;
- un score inférieur au seuil produit `0` ;
- un score supérieur ou égal au seuil produit `1`.

## 10. Explication locale

L'explication locale est calculée dans [`app/ml/explainer.py`](../../app/ml/explainer.py).

Comme le modèle final est linéaire après standardisation, on peut écrire :

```text
score = intercept + somme(coef_i * feature_standardisee_i)
```

Cette propriété permet :

- une explication locale fidèle au runtime réel ;
- une lecture directe des variables qui poussent le score vers le haut ;
- une lecture directe des variables qui le réduisent.

Le portfolio Streamlit s'appuie sur cette décomposition pour afficher :

- les facteurs qui augmentent le risque de départ ;
- les facteurs qui diminuent le risque de départ.

## 11. Limites et vigilance

- Le modèle a été entraîné sur un schéma de features précis : toute dérive de preprocessing modifie les scores.
- Les accents et problèmes d'encodage dans certains libellés MLflow ont nécessité une logique de réparation dans le preprocessing.
- Une erreur de chargement du flavor scikit-learn peut dégrader l'accès à certaines méthodes du modèle.
- Les jeux de démonstration doivent toujours rester cohérents avec les valeurs réellement admises par les CSV bruts et par le modèle final.

### Explication de la limite sur le flavor scikit-learn

Le modèle MLflow peut être chargé de deux manières :

- via le flavor `scikit-learn`, qui restitue l'objet modèle natif ;
- via le flavor `pyfunc`, plus générique.

Si le chargement `scikit-learn` échoue et que l'on retombe sur `pyfunc`, l'API peut encore prédire, mais elle perd potentiellement l'accès à des méthodes spécialisées comme :

- `decision_function` ;
- les coefficients internes du modèle ;
- certains attributs nécessaires à une explication locale fidèle.

Dans ce cas :

- le score risque d'être moins fidèle au contrat du modèle ;
- l'interprétation locale devient plus fragile, voire impossible ;
- il faut diagnostiquer la cause de l'échec de chargement plutôt que d'accepter silencieusement une dégradation du runtime.

## 12. Liens utiles

- Vue architecture : [`../architecture/overview.md`](../architecture/overview.md)
- Documentation API : [`../api/README.md`](../api/README.md)
- Preprocessing : [`../../app/ml/preprocess.py`](../../app/ml/preprocess.py)
- Chargement du modèle : [`../../app/ml/loader.py`](../../app/ml/loader.py)
- Scoring : [`../../app/ml/predictor.py`](../../app/ml/predictor.py)
- Explication locale : [`../../app/ml/explainer.py`](../../app/ml/explainer.py)
