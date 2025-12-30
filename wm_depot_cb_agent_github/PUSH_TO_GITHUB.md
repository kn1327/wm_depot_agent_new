# 🚀 Push to GitHub & Deploy to Streamlit Cloud

## Phase 1: Prepare Local Files (5 minutes)

### Step 1: Navigate to Your GitHub Clone

Assuming you cloned your GitHub repo locally, navigate to it:

```bash
cd C:\Users\k0n06do\wm-depot-cb-agent
# or wherever you cloned it
git status
```

If you haven't cloned it yet:

```bash
cd C:\Users\k0n06do\Documents
git clone https://github.com/kn1327/wm-depot-cb-agent.git
cd wm-depot-cb-agent
```

### Step 2: Copy Our New Files

Copy ALL files from `C:\Users\k0n06do\wm_depot_cb_agent_github` to your GitHub repo root:

```bash
# From your repo directory:
cd C:\Users\k0n06do\wm-depot-cb-agent

# Copy the clean structure
xcopy C:\Users\k0n06do\wm_depot_cb_agent_github\* . /E /I /Y

# Verify files are here
dir
```

You should see:
```
C:\Users\k0n06do\wm-depot-cb-agent
├── streamlit_app.py          ✅
├── requirements.txt          ✅
├── README.md                 ✅
├── DEPLOYMENT_CHECKLIST.md   ✅
├── PUSH_TO_GITHUB.md         ✅
├── .env.example              ✅
├── .gitignore                ✅
├── agents/                   ✅
├── connectors/               ✅
├── config/                   ✅
└── .streamlit/               ✅
```

### Step 3: Test Locally (IMPORTANT!)

Before pushing to GitHub, test that everything works:

```bash
# Create venv if you don't have one
uv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with Walmart mirror
uv pip install --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
  --allow-insecure-host pypi.ci.artifacts.walmart.com \
  -r requirements.txt

# Create secrets (copy from existing .streamlit/secrets.toml)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml with your GCP credentials
# vim .streamlit/secrets.toml

# Run the app
streamlit run streamlit_app.py
```

**Expected Result**: App loads at `http://localhost:8501` with:
- ✅ Dashboard tab shows metrics
- ✅ Recommendations tab works
- ✅ Q&A tab generates SQL
- ✅ No error messages

## Phase 2: Push to GitHub (5 minutes)

### Step 1: Check Git Status

```bash
cd C:\Users\k0n06do\wm-depot-cb-agent
git status
```

You should NOT see `.streamlit/secrets.toml` (it's in .gitignore ✅)

### Step 2: Add Files

```bash
# Add all new files
git add .

# Verify nothing sensitive is being added
git status

# Check: Should NOT include:
# - .streamlit/secrets.toml (actual secrets)
# - .env (actual environment vars)
# - *.json (GCP key files)
# - venv/ folder
# - __pycache__/ folders
```

### Step 3: Commit

```bash
git commit -m "refactor: clean streamlit deployment structure

- Consolidate agent modules into clean package structure
- Create Streamlit app with Dashboard, Recommendations, Q&A tabs
- Add comprehensive deployment guides
- Set up GitHub secrets management
- Add .streamlit/config.toml and secrets.toml.example
- Add requirements.txt with Walmart PyPI mirror
- Add README with full setup and deployment instructions"
```

### Step 4: Push to GitHub

```bash
git push origin main
```

Expected output:
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to 8 threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), ...
...
To https://github.com/kn1327/wm-depot-cb-agent.git
  [previous-commit-hash]...[new-commit-hash]  main -> main
```

### Step 5: Verify on GitHub

1. Go to: https://github.com/kn1327/wm-depot-cb-agent
2. Check that you see:
   - `streamlit_app.py` at root
   - `requirements.txt` at root
   - `agents/`, `connectors/`, `config/` folders
   - `.streamlit/config.toml` (visible)
   - `.streamlit/secrets.toml.example` (visible, but not actual secrets!)
   - `.gitignore` protecting secrets
3. Check latest commit shows your changes

## Phase 3: Deploy to Streamlit Cloud (10 minutes)

### Step 1: Create Streamlit Account (if needed)

1. Go to: https://streamlit.io/cloud
2. Click "Sign up" or "Sign in"
3. Choose "Sign in with GitHub"
4. Authorize Streamlit to access your GitHub repos

### Step 2: Create New App

1. Click "Create app" (or "New app" button)
2. Select deployment option:
   - **Repository**: `kn1327/wm-depot-cb-agent`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`

### Step 3: Add Secrets (CRITICAL!)

**IMPORTANT**: Always add secrets BEFORE deploying!

1. Click "Advanced settings" before clicking "Deploy"
2. Find the "Secrets" section
3. Paste the contents of your `.streamlit/secrets.toml` file:

```toml
GCP_PROJECT_ID = "wmt-instockinventory-datamart"
BQ_DATASET = "WM_AD_HOC"

[gcp_service_account]
type = "service_account"
project_id = "wmt-instockinventory-datamart"
private_key_id = "YOUR_KEY_ID_HERE"
private_key = "YOUR_PRIVATE_KEY_HERE" 
client_email = "YOUR_SERVICE_ACCOUNT@gserviceaccount.com"
client_id = "YOUR_CLIENT_ID_HERE"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL_HERE"
```

4. Click "Deploy"

### Step 4: Wait for Build

Streamlit will:
1. Clone your repo
2. Install dependencies from requirements.txt
3. Load secrets
4. Start the app

**Timeline**: 2-3 minutes

You'll see:
```
Installing dependencies...
Installing pip packages...
Running the app...
```

### Step 5: Verify Deployment

Once deployed, you'll see a URL like:
```
https://wm-depot-cb-agent-abc123xyz.streamlit.app
```

1. Click the URL or copy/paste in browser
2. Test all functionality:
   - Dashboard tab loads metrics ✅
   - Select different depots ✅
   - Recommendations tab works ✅
   - Q&A tab generates SQL ✅
3. Check for any errors in logs

### Step 6: Check Logs (if something breaks)

If deployment fails:
1. Go to app settings (⚙️ gear icon)
2. Click "Manage app"
3. View "Logs" section
4. Look for error messages
5. Common issues:
   - Missing dependencies → Add to requirements.txt
   - Secrets not loaded → Re-add in Secrets section
   - Module not found → Check agent imports

## Phase 4: Share with Team (2 minutes)

### Copy Your Public URL

Your app URL:
```
https://wm-depot-cb-agent-RANDOMSTRING.streamlit.app
```

### Share with Team

Send them:
1. **App URL**: The link above
2. **How to Use**: Point them to the `README.md` in the repo
3. **Support**: Let them know to check README troubleshooting

### Create Streamlit Community Badge (Optional)

Add to your GitHub README:
```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wm-depot-cb-agent-RANDOMSTRING.streamlit.app)
```

## Troubleshooting

### ❌ "Module not found" Error

```bash
# Problem: A Python import failed
# Solution:

# 1. Check streamlit_app.py for typos
# 2. Verify all agent files are in agents/ folder
# 3. Check __init__.py files exist in each folder
# 4. Try locally first: streamlit run streamlit_app.py

# If local works but cloud fails:
# Check requirements.txt has all dependencies
# Run: uv pip freeze > requirements.txt
# Commit and push
# Redeploy on Streamlit Cloud
```

### ❌ "Authentication failed" Error

```bash
# Problem: BigQuery credentials not loaded
# Solution:

# 1. Verify secrets.toml in .streamlit/ folder (local)
# 2. Check Streamlit Cloud "Secrets" section has all content
# 3. Ensure GCP_PROJECT_ID is correct
# 4. Test locally first with: streamlit run streamlit_app.py

# If still failing:
# 1. Check GCP service account has BigQuery permissions
# 2. Verify service account email is correct
# 3. Test GCP connection: gcloud auth application-default login
```

### ❌ "No data returned" Error

```bash
# Problem: BigQuery query returns empty
# Solution:

# 1. Verify depot number (try 7634)
# 2. Check BigQuery has data for selected dates
# 3. Try increasing "Days Lookback" slider
# 4. Check table names in agents/query_generator.py
# 5. Test query in BigQuery console
```

### ❌ Deploy Button Disabled

```bash
# Problem: "Deploy" button is greyed out
# Solution:

# This usually means:
# - You haven't authorized Streamlit to access GitHub
# - Your GitHub account isn't linked

# Fix:
# 1. Go to account settings in Streamlit Cloud
# 2. Click "Relink GitHub"
# 3. Authorize again
# 4. Try creating app again
```

## Quick Reference Commands

### Local Development
```bash
# Setup
uv venv && source venv/bin/activate
uv pip install -r requirements.txt

# Run
streamlit run streamlit_app.py

# Test
git status
git add .
git commit -m "Your message"
git push origin main
```

### Check Requirements
```bash
# Generate requirements from current environment
uv pip freeze > requirements.txt

# Check specific package
uv pip show streamlit
```

### Git Verification
```bash
# Check what will be committed
git diff --cached

# Check for secrets
grep -r "private_key" .
grep -r "GCP_" .

# These should NOT appear (they're in .gitignore)
```

## Next Steps

After deployment:

1. **Monitor**: Check app logs weekly for errors
2. **Update**: Keep dependencies current
   ```bash
   pip install --upgrade streamlit google-cloud-bigquery
   ```
3. **Enhance**: Add more depots, features, etc.
4. **Gather Feedback**: Share with team, get insights

---

## SUCCESS! 🎉

Your app is now:
- ✅ On GitHub (https://github.com/kn1327/wm-depot-cb-agent)
- ✅ Live on Streamlit Cloud  
- ✅ Shareable with your team
- ✅ Scalable and maintainable

**Celebrate! You did it!** 🐕
