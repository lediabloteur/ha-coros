<p align="center">
  <img src="icon.png" width="160" height="160" alt="COROS Home Assistant Icon" />
</p>

# COROS Training Hub & Health Integration for Home Assistant 🏃⌚

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/lediabloteur)

A comprehensive Home Assistant integration for **COROS** watches and Training Hub. It natively syncs your workouts, physiological health metrics (Sleep, HRV, Resting Heart Rate, Recovery), monthly realized volumes, and EvoLab race predictions.

---

## ✨ Features

- 📅 **Native Calendar Entity (`calendar.coros_training_schedule`)**
  - Displays all upcoming workouts planned in your COROS calendar.
  - Full details for each session: Warmup, Intervals (Threshold/VMA pace targets), Recovery, and Cooldown.
- 💤 **Physiological & Recovery Tracking**
  - **Sleep Duration & Score** with stage breakdown (Deep, Light, REM ratios).
  - **Sleep HRV (Heart Rate Variability)** with status (Normal / Above / Below normal) and 7-day baseline.
  - **Resting Heart Rate (RHR)** in bpm.
  - **Recovery Status %** and Training Load Assessment (Optimized / Overload ratio).
- 📊 **Monthly Realized Volumes**
  - Realized Running distance, session count, and time (`sensor.coros_course_mois`).
  - Realized Cycling & Gravel distance, count, and time (`sensor.coros_velo_gravel_mois`).
  - Realized PPG / Strength sessions count and time (`sensor.coros_ppg_renfo_mois`).
  - Total monthly time and Training Load (`sensor.coros_temps_total_mois`, `sensor.coros_charge_entrainement_mois`).
- ⏱️ **EvoLab Race Predictor & Fitness**
  - Predicted times and paces for **5 km, 10 km, Half Marathon, and Marathon** (`sensor.coros_prediction_*`).
  - **VO2max, Threshold Pace, and Running Level** (`sensor.coros_vo2max`, `sensor.coros_threshold_pace`, `sensor.coros_running_level`).
  - **Training Load Assessment, Fitness & Fatigue** (`sensor.coros_training_load_status`, `sensor.coros_short_term_load`, `sensor.coros_long_term_load`, `sensor.coros_load_ratio`).

### 📋 Exposed Sensor Entities

| Sensor Entity ID | Friendly Name | Description / Attributes |
|---|---|---|
| `sensor.coros_vo2max` | VO2max | VO2max (ml/kg/min) |
| `sensor.coros_running_level` | Niveau de Course | Running ability score (/100) |
| `sensor.coros_threshold_pace` | Allure Seuil | Threshold pace (/km) |
| `sensor.coros_prediction_5k` | Prédiction 5 km | 5K predicted time & calculated pace attribute |
| `sensor.coros_prediction_10k` | Prédiction 10 km | 10K predicted time & calculated pace attribute |
| `sensor.coros_prediction_semi` | Prédiction Semi-Marathon | Half Marathon predicted time & pace attribute |
| `sensor.coros_prediction_marathon` | Prédiction Marathon | Marathon predicted time & pace attribute |
| `sensor.coros_training_load_status` | Évaluation Charge | Status (Optimized, etc.), load ratio, short & long term loads |
| `sensor.coros_short_term_load` | Charge Court Terme | Short-Term Load / Fatigue metric |
| `sensor.coros_long_term_load` | Charge Long Terme | Long-Term Load / Fitness metric |
| `sensor.coros_load_ratio` | Ratio de Charge | Training load ratio (acute vs chronic) |
| `sensor.coros_recovery` | Niveau de Récupération | Recovery percentage (%) & training allowed level |
| `sensor.coros_recovery_time` | Temps Récupération | Estimated time to full recovery |
| `sensor.coros_fc_repos` | FC Repos | Daily resting heart rate (bpm) |
| `sensor.coros_vfc` | Variabilité FC (VFC) | Sleep HRV average (ms), status, baseline & normal range |
| `sensor.coros_sommeil_duree` | Sommeil (Dernière nuit) | Sleep duration with deep, light, REM & awake ratios |
| `sensor.coros_sommeil_score` | Score de Sommeil | Overall sleep score (/100) |
| `sensor.coros_sommeil_profond` | Sommeil Profond | Deep sleep ratio (%) |
| `sensor.coros_sommeil_leger` | Sommeil Léger | Light sleep ratio (%) |
| `sensor.coros_sommeil_rem` | Sommeil Paradoxal | REM sleep ratio (%) |
| `sensor.coros_course_mois` | Course (Mois) | Monthly running distance (km), count, duration |
| `sensor.coros_velo_gravel_mois` | Vélo & Gravel (Mois) | Monthly cycling distance (km), count, duration |
| `sensor.coros_ppg_renfo_mois` | PPG & Renfo (Mois) | Monthly strength & conditioning sessions count, duration |
| `sensor.coros_temps_total_mois` | Temps Total (Mois) | Total training time across all sports this month |
| `sensor.coros_seances_realisees_mois`| Séances Réalisées (Mois) | Total completed workouts this month |
| `sensor.coros_charge_entrainement_mois` | Charge Entraînement (Mois) | Total monthly training load (TL) & weekly history |
| `sensor.coros_temps_activite_semaine` | Temps d'Activité (Semaine) | Current week activity time (h), duration, distance, count & 8-week history |
| `sensor.coros_charge_entrainement_semaine` | Charge d'Entraînement (Semaine) | Current week training load (TL) & 8-week history |
| `sensor.coros_planning_entrainements` | Planning Entraînements | Next workout name & details, next 10 workouts attribute |
| `calendar.planning_entrainements_coros` | Planning COROS | Full Home Assistant calendar with scheduled workouts |

---

## 🚀 Installation via HACS

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the three dots (top right) > **Custom repositories**.
3. Add the URL of this repository, select category **Integration**, and click **Add**.
4. Click **Download** and restart Home Assistant.
5. Go to **Settings** > **Devices & Services** > **Add Integration** > Search for **COROS**.
6. Enter your COROS credentials.

---

## 🔒 Privacy & Authentication
This integration connects directly and securely to the official COROS European / US Training Hub APIs and MCP endpoint.

## ☕ Support the Project

If this integration makes your training easier or enhances your Home Assistant smart home, consider supporting the project! Your support helps fuel late-night coding sessions, maintain compatibility with COROS API changes, and develop new features for the community.

<p align="left">
  <a href="https://buymeacoffee.com/lediabloteur" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="180" />
  </a>
</p>

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** - see the [LICENSE](LICENSE) file for details.
