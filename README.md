<p align="center">
  <img src="icon.png" width="160" height="160" alt="COROS Home Assistant Icon" />
</p>

# COROS Training Hub & Health Integration for Home Assistant 🏃⌚

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

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
  - Realized Running distance, session count, and time.
  - Realized Cycling & Gravel distance, count, and time.
  - Realized PPG / Strength sessions count and time.
  - Total monthly time and Training Load (TL).
- ⏱️ **EvoLab Race Predictor**
  - Predicted times and paces for **5 km, 10 km, Half Marathon, and Marathon**.
  - **VO2max, Threshold Pace, and Running Level (Marathon Level)**.

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

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** - see the [LICENSE](LICENSE) file for details.
