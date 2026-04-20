# Feria de Sevilla AI Agent - GCP Deployment Guide

This repository contains an AI agent application for analyzing Feria de Sevilla data, integrated with BigQuery and deployed on Cloud Run.

## Step 1: Clone the Repository

Whether you are running locally or in Google Cloud Shell, the first step is to clone the repository to get the source files:

```bash
git clone https://github.com/mtoscano84/laferia-adk-bigquery.git
cd laferia-adk-bigquery
```

## Step 2: Data Setup (BigQuery)

Before running or deploying the app, you need to create and populate the BigQuery dataset with the simulated data:

1.  Ensure you are authenticated and have set your project ID:
    ```bash
    export PROJECT_ID="your-project-id"
    gcloud config set project $PROJECT_ID
    ```
2.  Install the required Python packages for the setup script:
    ```bash
    pip install google-cloud-bigquery pandas db-dtypes
    ```
3.  Run the setup script:
    ```bash
    python3 src/backend/setup_bigquery.py
    ```
    This will create the `feria_sevilla_2025` dataset and populate it with records.

## Option A: Local Development

To run the application locally on your machine:

1.  Ensure you have a `.env` file in the root directory with your `GEMINI_API_KEY`.
2.  Run the demo script:
    ```bash
    ./run_demo.sh
    ```
    This will create a virtual environment, install dependencies, copy assets, and start both backend and frontend servers.

## Option B: GCP Deployment (Cloud Run)

Follow these instructions to deploy the application to Google Cloud Platform.

> [!TIP]
> **Recommended**: Use **Google Cloud Shell** to run these commands. It comes pre-installed with `gcloud`, `docker`, and `git`, and is already authenticated to your GCP project.

### Prerequisites

1.  A GCP Project with billing enabled.
2.  If not using Cloud Shell, ensure you have the Google Cloud SDK and Docker installed locally.

### 1. Build and Push Docker Images

We will use Artifact Registry to store our Docker images.

1.  Create a repository in Artifact Registry:
    ```bash
    gcloud artifacts repositories create feria-repo --repository-format=docker --location=us-central1
    ```

2.  Configure Docker to authenticate with Artifact Registry:
    ```bash
    gcloud auth configure-docker us-central1-docker.pkg.dev
    ```

3.  Build and push the **Backend** image:
    ```bash
    docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/backend -f src/backend/Dockerfile .
    docker push us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/backend
    ```

4.  Build and push the **Frontend** image:
    ```bash
    docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/frontend -f src/frontend/Dockerfile .
    docker push us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/frontend
    ```

### 2. Deploy Backend to Cloud Run

1.  Deploy the backend container:
    ```bash
    gcloud run deploy feria-backend \
      --image us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/backend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars GEMINI_API_KEY=[YOUR_GEMINI_API_KEY],GOOGLE_CLOUD_PROJECT=$PROJECT_ID,BIGQUERY_DATASET=feria_sevilla_2025
    ```
2.  **Note the Service URL** returned by this command. It will look like `https://feria-backend-xxxxxx-uc.a.run.app`. This is your `BACKEND_URL`.

### 3. Deploy Frontend to Cloud Run

1.  Deploy the frontend container, passing the Backend URL:
    ```bash
    gcloud run deploy feria-frontend \
      --image us-central1-docker.pkg.dev/$PROJECT_ID/feria-repo/frontend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars BACKEND_URL=https://feria-backend-xxxxxx-uc.a.run.app/api/chat
    ```
    *(Replace with your actual backend URL noted in Step 2)*

### 4. IAM Permissions

For the agent to query BigQuery, the Cloud Run service account must have permission.

1.  Find the service account used by the `feria-backend` service (usually the default compute service account).
2.  Grant the following roles to that service account on your project:
    - **BigQuery Data Viewer**
    - **BigQuery User**

Now you can access the frontend URL provided by Cloud Run and interact with Curro!
