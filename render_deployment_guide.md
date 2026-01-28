# 🚀 Deploying to Render (Free Cloud)

This guide will help you upload your backend to the internet so your app works correctly 24/7 without your laptop.

## Phase 1: Push Code to GitHub
Render needs your code to be on GitHub.

1.  **Create a New Repository** on GitHub (e.g., `plant-growth-backend`).
    - Make sure it's **Public** (or Private, doesn't matter for Render).
    - Do **not** initialize with README/gitignore yet.
2.  **Open Terminal** in your project folder (`growth_prediction\plant_stage_backend`).
3.  **Run these commands**:
    ```bash
    git init
    git add .
    git commit -m "Final Backend Code"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/plant-growth-backend.git
    git push -u origin main
    ```
    *(Replace `YOUR_USERNAME` with your actual GitHub username)*

## Phase 2: Deploy on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Click **Build and deploy from a Git repository**.
4.  Connect your GitHub account and select your `plant-growth-backend` repo.
5.  **Configure Settings**:
    - **Name**: `plant-growth-api` (or whatever you like)
    - **Region**: Frankfurt or Singapore (closest to you)
    - **Branch**: `main`
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn app:app` (It might auto-detect this from the Procfile I created!)
    - **Plan**: Free
6.  Click **Create Web Service**.

## Phase 3: Update Flutter App
Once deployed, Render will give you a URL like:
`https://plant-growth-api.onrender.com`

1.  Open your Flutter project: `lib/services/growth_service.dart`.
2.  Update the `baseUrl`:
    ```dart
    // OLD
    // static const String baseUrl = "http://192.168.1.183:5000/predict";

    // NEW (Render URL)
    static const String baseUrl = "https://plant-growth-api.onrender.com/predict";
    ```
3.  Run your app (`flutter run`). It now uses the cloud! ☁️
