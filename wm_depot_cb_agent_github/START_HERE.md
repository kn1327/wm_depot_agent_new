# WM Depot CB% Agent - START HERE

## What We Just Built

A **production-ready Streamlit app** for analyzing WM depot Complete Basket (CB%) metrics with:

- Dashboard: View CB% trends and metrics
- Smart Recommendations: AI-powered item suggestions
- Q&A: Ask questions about your data
- Root Cause Analysis: Understand metric changes
- BigQuery: Direct secure connection to your data

---

## Quick Overview

### Project Structure
```
wm-depot-cb-agent/
+-- streamlit_app.py         # Main Streamlit application
+-- requirements.txt         # Python dependencies  
+-- README.md                # Full documentation
+-- PUSH_TO_GITHUB.md        # Deploy guide (YOU ARE HERE)
+-- agents/                  # AI agents
    +-- query_generator.py
    +-- item_recommender.py
    +-- root_cause_analyzer.py
+-- connectors/              # Data connections
    +-- bigquery_connector.py
+-- config/                  # Configuration
    +-- settings.py
+-- .streamlit/              # Streamlit configuration
    +-- config.toml
    +-- secrets.toml.example
```

---

## 3-Step Deployment

### Step 1: Copy Files to Your GitHub Clone (1 min)

```bash
# Go to your GitHub repo
cd C:\Users\k0n06do\wm-depot-cb-agent

# Copy all files from our temp folder
xcopy C:\Users\k0n06do\wm_depot_cb_agent_github\* . /E /I /Y

# Verify
dir
```

### Step 2: Test Locally (3 min)

```bash
# Activate your venv
source venv/bin/activate

# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your GCP credentials
# (Open in editor and paste your service account JSON)

# Run
streamlit run streamlit_app.py
```

**Expected**: App loads at http://localhost:8501 with all 3 tabs working

### Step 3: Push & Deploy (5 min)

```bash
# Push to GitHub
git add .
git commit -m "Clean Streamlit deployment structure"
git push origin main

# Then go to https://streamlit.io/cloud and:
# 1. Create new app
# 2. Select your repo
# 3. Add secrets
# 4. Deploy!
```

**Result**: Live app at https://wm-depot-cb-agent-XXXXX.streamlit.app

---

## Documentation Files

| File | Purpose |
|------|----------|
| **README.md** | Full setup, features, troubleshooting |
| **PUSH_TO_GITHUB.md** | Step-by-step GitHub & Streamlit deployment |
| **DEPLOYMENT_CHECKLIST.md** | Pre/during/post deployment checklist |
| **.env.example** | Environment variables template |
| **.streamlit/secrets.toml.example** | GCP secrets template |

### Read in This Order:
1. **This file** (you're reading it!)
2. **README.md** (understand the app)
3. **PUSH_TO_GITHUB.md** (deploy it)
4. **DEPLOYMENT_CHECKLIST.md** (verify it)

---

## Key Files Explained

### streamlit_app.py (Main App)
- Streamlit UI with 3 tabs
- Imports agents for analysis
- Direct BigQuery connection
- Caching for performance

### agents/ (AI Logic)
- **query_generator.py**: Converts questions to SQL
- **item_recommender.py**: Suggests items to add  
- **root_cause_analyzer.py**: Analyzes metric drops

### connectors/ (Data Access)
- **bigquery_connector.py**: BigQuery interface
- Handles queries and error handling

### config/ (Settings)
- **settings.py**: Configuration management
- Loads from environment variables
- Handles GCP credentials

### .streamlit/ (Streamlit Config)
- **config.toml**: UI settings, theme, etc.
- **secrets.toml.example**: Template (YOUR secrets go here)

---

## IMPORTANT: Secrets Management

### Local Development
```bash
# 1. Copy template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 2. Edit with your GCP service account:
vim .streamlit/secrets.toml
# Paste your service account JSON here

# 3. NEVER commit this file!
# (It's protected by .gitignore)
```

### Streamlit Cloud
```
1. Go to your app settings
2. Click "Secrets"
3. Paste secrets.toml contents
4. App will load them automatically
5. Deploy!
```

**CRITICAL**: Never put actual secrets in Git!

---

## Pre-Deployment Checklist

- [ ] streamlit_app.py works locally
- [ ] All 3 tabs load without errors
- [ ] Q&A tab generates SQL queries
- [ ] .streamlit/secrets.toml is in .gitignore
- [ ] No *.json files in repo (GCP keys)
- [ ] requirements.txt has all dependencies
- [ ] README.md documents everything

---

## GCP Setup (if you haven't done this)

If you need to set up BigQuery credentials:

1. **Get GCP Project ID**:
   ```
   wmt-instockinventory-datamart
   ```

2. **Create Service Account**:
   - Go to GCP Console
   - IAM & Admin > Service Accounts
   - Create new service account
   - Add role: "BigQuery Admin"
   - Create JSON key
   - Download the key file

3. **Add to Streamlit Secrets**:
   ```bash
   # Copy the entire JSON key file contents
   cat your-key-file.json
   
   # Paste into .streamlit/secrets.toml under [gcp_service_account]
   ```

---

## Deployment Paths

### Path A: Streamlit Cloud (Recommended)
- Easiest: No servers to manage
- Best for: Team sharing
- Cost: Free tier available
- Guide: See PUSH_TO_GITHUB.md

### Path B: Google Cloud Run (Advanced)
- More control: Custom containers
- For: Production deployments
- Cost: Pay per use
- Note: Not covered in this guide, but doable

### Path C: Docker (Advanced)
- Flexibility: Full control
- For: Internal servers
- Files: Dockerfile included
- Note: See README.md for Docker setup

---

## Next Steps After Deployment

### Immediate
1. Test the live app
2. Try all features
3. Share URL with team

### Soon
1. Add more depots to dropdown
2. Customize dashboard colors
3. Create usage guide for team

### Later
1. Add more analysis features
2. Set up email alerts
3. Create admin dashboard
4. Integrate with Slack

---

## Helpful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **BigQuery Python**: https://cloud.google.com/bigquery/docs/reference/python
- **GCP Console**: https://console.cloud.google.com
- **Streamlit Cloud**: https://streamlit.io/cloud

---

## Common Questions

**Q: Can I run this locally without deploying?**  
A: Yes! Just run `streamlit run streamlit_app.py` with `.streamlit/secrets.toml` configured.

**Q: How do I add more depots?**  
A: Edit `streamlit_app.py`, find the `st.selectbox()` for depots, add your depot numbers.

**Q: What if it breaks after I deploy?**  
A: Check Streamlit Cloud logs (gear icon -> Manage app -> Logs). Usually missing dependency or secret issue.

**Q: How do I update the app?**  
A: Just commit to GitHub and Streamlit will auto-redeploy in 1-2 minutes.

**Q: Can my team access the live app?**  
A: Yes! Just share the Streamlit Cloud URL. No login needed (unless you add it).

**Q: What about security/privacy?**  
A: All code is on GitHub (private recommended). Data stays in BigQuery. Secrets are not in Git.

---

## You're Ready!

You have everything you need. Next steps:

1. **Read**: Open README.md for full documentation
2. **Deploy**: Follow PUSH_TO_GITHUB.md for step-by-step guide  
3. **Share**: Get that URL and show your team!
4. **Iterate**: Add features based on feedback

---

## Built by KIA (Code Puppy)

This project was generated by **KIA** - your friendly AI code assistant!

- Fast: Generated in minutes, not hours
- Clean: Production-ready structure
- Documented: Everything explained
- Scalable: Easy to extend and maintain

---

## Get Help

If stuck:
1. Check DEPLOYMENT_CHECKLIST.md for your situation
2. Read troubleshooting in README.md
3. Check Streamlit Cloud logs
4. Review code comments in source files

---

Let's go!
