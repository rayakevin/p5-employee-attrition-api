---
title: P5 Employee Attrition Portfolio
emoji: "📊"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
---

# P5 Employee Attrition Portfolio

Docker Space exposing the Streamlit portfolio UI.

## Runtime notes

- the application listens on port `8501`
- it consumes the prediction API exposed through `P5_API_BASE_URL`
- by default, it targets `https://rayakevin-p5-employee-attrition-api.hf.space`

## Main page

- Streamlit dashboard for attrition risk scoring
- local explanation of the deployed linear model
