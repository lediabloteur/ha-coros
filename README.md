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

- 🗺️ **Latest Activities & Route Maps**
  - Instant sync of your latest completed workouts with sport detection (`sensor.coros_derniere_activite`, `sensor.coros_derniere_course`, `sensor.coros_derniere_sortie_velo`).
  - High-definition dark route maps rendered by COROS directly available on sensor `entity_picture` and native Home Assistant image entities (`image.coros_derniere_activite_carte`, etc.).
  - Rich metrics: Distance, Duration, Moving Time, Average Pace (min/km) or Speed (km/h), Heart Rate (Avg & Max), Elevation (D+ / D-), Calories, Cadence, Training Load, Device.
  - Full history attribute `recent_activities` listing the 10 most recent workouts with their respective maps and metrics.
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

### 📋 Exposed Entities

#### Sensors

| Sensor Entity ID | Friendly Name | Description / Attributes |
|---|---|---|
| `sensor.coros_derniere_activite` | Dernière Activité | Name, distance, pace/speed, HR, D+, device, map thumbnail (`entity_picture`), last 10 activities attribute |
| `sensor.coros_derniere_course` | Dernière Course | Latest running workout with pace, HR, D+, calories, map |
| `sensor.coros_derniere_sortie_velo` | Dernière Sortie Vélo | Latest cycling/gravel ride with speed, HR, D+, map |
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
| `sensor.coros_prochaine_course` | Prochaine Compétition | Next official competition/race scheduled in COROS agenda |
| `calendar.planning_entrainements_coros` | Planning COROS | Full Home Assistant calendar with scheduled workouts & races |

#### Route Maps (Image Platform)

| Image Entity ID | Friendly Name | Description |
|---|---|---|
| `image.coros_derniere_activite_carte` | Carte Dernière Activité | High-resolution route map image of your latest activity |
| `image.coros_derniere_course_carte` | Carte Dernière Course | Route map image of your latest running workout |
| `image.coros_derniere_sortie_velo_carte` | Carte Dernière Sortie Vélo | Route map image of your latest cycling/gravel ride |

---

## 🚀 Installation via HACS

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the three dots (top right) > **Custom repositories**.
3. Add the URL of this repository, select category **Integration**, and click **Add**.
4. Click **Download** and restart Home Assistant.
5. Go to **Settings** > **Devices & Services** > **Add Integration** > Search for **COROS**.
6. Enter your COROS credentials (`email` and `password`).

### 🔑 Activating EvoLab & Health Metrics (Optional)

- **Standard credentials (`email` + `password`)**: Natively synchronizes all your activities, route maps, monthly & weekly realized volumes, scheduled workouts, and next race detection.
- **EvoLab & Health Metrics** (Allure seuil, VO2max, Récupération, Prédictions, Sommeil, VFC) :
  COROS provides these advanced metrics through its official OAuth MCP server. To enable them on your personal account:
  1. Run the zero-dependency helper script:
     ```bash
     python tools/get_mcp_token.py
     ```
  2. Log in securely to your COROS account in the browser window that opens.
  3. Copy the generated token string.
  4. In Home Assistant, go to **Paramètres > Appareils et services > COROS > Configurer (Options)**, paste the token into **Jeton MCP COROS**, and submit!

*(If you don't configure an MCP token, the EvoLab sensors will simply remain unavailable without displaying inaccurate foreign data).*

---

## 🎨 Dashboard Lovelace Cards

You can display your latest workout with its dark route map and metrics in your Lovelace dashboard using the pre-built templates below (see also [examples/card_derniere_activite.yaml](examples/card_derniere_activite.yaml)):

### Option 1: Standard Markdown Card (No plugins required)
```yaml
type: markdown
title: Dernière Activité COROS
content: |
  {% if state_attr('sensor.coros_derniere_activite', 'has_gps') and state_attr('sensor.coros_derniere_activite', 'map_url') %}
  <center>
    <a href="https://training.coros.com" target="_blank">
      <img src="{{ state_attr('sensor.coros_derniere_activite', 'map_url') }}" width="100%" style="border-radius: 16px; max-width: 360px; border: 1px solid rgba(255,255,255,0.1);" />
    </a>
  </center>
  {% endif %}

  ### 🏅 [{{ state_attr('sensor.coros_derniere_activite', 'name') }}](https://training.coros.com)
  * **Sport** : {{ state_attr('sensor.coros_derniere_activite', 'sport') }} ({{ state_attr('sensor.coros_derniere_activite', 'device') }})
  * **Date** : {{ state_attr('sensor.coros_derniere_activite', 'date_formatted') }}
  * **Distance** : {{ state_attr('sensor.coros_derniere_activite', 'distance_km') }} km
  * **Durée** : {{ state_attr('sensor.coros_derniere_activite', 'duration') }}
  * **Allure / Vitesse** : {{ state_attr('sensor.coros_derniere_activite', 'pace') or (state_attr('sensor.coros_derniere_activite', 'speed_kmh') ~ ' km/h') }}
  * **Cardio** : {{ state_attr('sensor.coros_derniere_activite', 'avg_hr') }} bpm
  * **Dénivelé** : +{{ state_attr('sensor.coros_derniere_activite', 'elevation_gain') }} m / -{{ state_attr('sensor.coros_derniere_activite', 'elevation_loss') }} m
  * **Charge (TL)** : {{ state_attr('sensor.coros_derniere_activite', 'training_load') }}
```

### Option 2: Pure Route Map Image Card
```yaml
type: picture-entity
entity: image.coros_derniere_activite_carte
name: Dernière Activité COROS
show_state: false
show_name: true
tap_action:
  action: url
  url_path: https://training.coros.com
```

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
