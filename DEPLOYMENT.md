# Free demo deployment

This project can be demonstrated with GitHub Pages for the React site, Render for the FastAPI API, Supabase Postgres for saved accounts and cases, and Ollama Cloud for lawyer analysis.

## Setup sequence

1. Merge the open deployment pull request into `main`.
2. Create a free Supabase project. In **Connect**, copy the **Session pooler** PostgreSQL connection string. Do not put this value in GitHub.
3. Create an Ollama API key and choose a model available in your free starter usage. Keep the key private.
4. In Render, create a Blueprint from this repository and select `render.yaml`. Set `DATABASE_URL` to the Supabase Session pooler URL, `OLLAMA_API_KEY` to the Ollama key, and `OLLAMA_MODEL` to the chosen model. The `OLLAMA_URL` and allowed website origin are already in the blueprint.
5. After Render deploys, copy the API service URL (for example, `https://case-outcome-api.onrender.com`). In GitHub, open **Settings → Secrets and variables → Actions → Variables** and add `VITE_API_BASE_URL` with that URL and no trailing slash.
6. In GitHub, open **Settings → Pages** and choose **GitHub Actions** as the source. In **Actions**, run or rerun **Deploy frontend to GitHub Pages**.
7. Open `https://case-outcome-org.github.io/case-outcome-prediction-system/` and create a User or Lawyer account.

Never commit database connection strings, Ollama keys, passwords, or `.env` files. Do not use confidential client documents in this public demo; lawyer analysis sends submitted text to the configured Ollama Cloud API.

## Free-tier limits

Render's free API service sleeps after 15 minutes without traffic and may take about a minute to wake. Supabase may pause an inactive free project after a week. Ollama's free account includes a limited starter amount of cloud-model usage; it is not unlimited. The outcome model is experimental, with low test metrics, and is not legal advice.

The processed case metadata and trained model are included in the backend deployment assets. The original large Kaggle archive and SQLite account database are not included.
