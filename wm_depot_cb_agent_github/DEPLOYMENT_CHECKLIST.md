# 🚀 Deployment Checklist

## Local Setup ✅

- [ ] Clone repository from GitHub
- [ ] Create Python virtual environment
- [ ] Install dependencies: `uv pip install -r requirements.txt`
- [ ] Create `.streamlit/secrets.toml` with GCP credentials
- [ ] Create `.env` file with configuration
- [ ] Test locally: `streamlit run streamlit_app.py`
- [ ] Verify all 3 tabs load (Dashboard, Recommendations, Q&A)
- [ ] Select different depots and verify data loads

## Pre-GitHub Checks ✅

- [ ] Delete `.streamlit/secrets.toml` (NEVER commit secrets!)
- [ ] Verify `.gitignore` includes `.streamlit/secrets.toml`
- [ ] Verify `.gitignore` includes `*.json` (GCP keys)
- [ ] Verify `.gitignore` includes `.env`
- [ ] Run: `git status` and check no secrets are staged
- [ ] Commit all code files
- [ ] Create meaningful commit message

## GitHub Setup ✅

- [ ] Verify repo at: `https://github.com/kn1327/wm-depot-cb-agent`
- [ ] Check main branch is default
- [ ] Verify all code files are pushed
- [ ] Verify `.gitignore` is working (no secrets in repo)
- [ ] Check GitHub has `streamlit_app.py` at root
- [ ] Check GitHub has `requirements.txt` at root
- [ ] Check GitHub has `.streamlit/config.toml`

## Streamlit Cloud Deployment ✅

### Account Setup
- [ ] Create Streamlit account: https://streamlit.io/cloud
- [ ] Link GitHub account to Streamlit
- [ ] Grant Streamlit access to your GitHub repos

### Deploy App
- [ ] Click "Create app"
- [ ] Select repo: `kn1327/wm-depot-cb-agent`
- [ ] Select branch: `main`
- [ ] Select file: `streamlit_app.py`
- [ ] **IMPORTANT**: Add Secrets BEFORE deploying

### Add Secrets (CRITICAL!)
- [ ] Click "Advanced settings"
- [ ] Click "Secrets"
- [ ] Paste entire `.streamlit/secrets.toml` content
- [ ] Include GCP service account JSON
- [ ] **DO NOT** save secrets locally in the Git repo
- [ ] Click "Deploy!"

### Verify Deployment
- [ ] Wait 2-3 minutes for build to complete
- [ ] Check app loads at `https://wm-depot-cb-agent-XXXXX.streamlit.app`
- [ ] Test Dashboard tab loads metrics
- [ ] Test Recommendations tab works
- [ ] Test Q&A tab generates SQL
- [ ] Try selecting different depots
- [ ] Check for any error messages in logs

## Post-Deployment ✅

- [ ] Share app URL with team
- [ ] Document any custom BigQuery table names
- [ ] Set up monitoring/alerts (optional)
- [ ] Plan regular updates and maintenance
- [ ] Create usage guide for team

## Common Issues & Fixes

### ❌ "Secrets not found" Error
```
Fix: Add secrets to Streamlit Cloud before deploying
Go to app settings → Secrets → Paste secrets.toml contents
```

### ❌ "BigQuery authentication failed"
```
Fix: Verify GCP service account has these permissions:
- bigquery.datasets.get
- bigquery.tables.get
- bigquery.tables.list
- bigquery.jobs.create
- bigquery.jobs.get
```

### ❌ "No data returned"
```
Fix:
1. Verify depot number is correct
2. Check BigQuery tables have data for selected dates
3. Try extending historical period
```

### ❌ "Module not found" Error
```
Fix: Add missing dependency to requirements.txt
Run: uv pip freeze > requirements.txt
Push to GitHub and redeploy
```

## Maintenance

### Monthly
- [ ] Check Streamlit Cloud logs for errors
- [ ] Review app performance metrics
- [ ] Update dependencies if needed

### As Needed
- [ ] Add new depots to dropdown in `streamlit_app.py`
- [ ] Update BigQuery table names if they change
- [ ] Add new analysis features
- [ ] Optimize slow queries

---

## Final Command-by-Command Guide

### 1. Local Setup
```bash
cd ~/Documents  # Or your preferred workspace
git clone https://github.com/kn1327/wm-depot-cb-agent.git
cd wm-depot-cb-agent

# Create venv (Walmart network)
uv venv
source venv/bin/activate

uv pip install --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
  --allow-insecure-host pypi.ci.artifacts.walmart.com \
  -r requirements.txt

# Set up secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your GCP credentials

# Test
streamlit run streamlit_app.py
```

### 2. Push to GitHub
```bash
git add .
git commit -m "WM Depot CB% Agent - Initial Release"
git push origin main
```

### 3. Deploy to Streamlit Cloud
1. Visit https://streamlit.io/cloud
2. Click "Create app"
3. Select your repo and file
4. Add secrets in Advanced settings
5. Click "Deploy!"

### 4. Share
```
Share this URL with your team:
https://wm-depot-cb-agent-RANDOMSTRING.streamlit.app
```

---

**You're all set! 🎉**
