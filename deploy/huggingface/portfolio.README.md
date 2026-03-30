---
title: P5 Portfolio Attrition Employes
emoji: "📊"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
---

# P5 Portfolio Attrition Employes

Ce Space Docker expose l'interface Streamlit du portfolio.

## Notes de runtime

- l'application ecoute sur le port `8501`
- elle consomme l'API via `P5_API_BASE_URL`
- par defaut, elle cible `https://rayakevin-p5-employee-attrition-api.hf.space`

## Ce que montre l'interface

- une analyse unitaire d'un profil employe ;
- une explication locale du score ;
- une analyse batch a partir d'un CSV ;
- un parcours de demonstration plus lisible qu'un simple appel HTTP.

## Role de ce Space

Ce Space sert de vitrine et de support de demonstration.

La logique metier reste portee par l'API :

- validation des payloads ;
- preprocessing ;
- scoring ;
- explication locale.
