# Deploying Rubik's Cube Recorder to Streamlit Cloud

## Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

## Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Rubik's Cube Recorder app"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/BartonChenTW/Rubik-s-cube-recorder.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app" button
   - Select your repository: `BartonChenTW/Rubik-s-cube-recorder`
   - Branch: `main`
   - Main file path: `app.py`

3. **Advanced Settings (Optional)**
   - Python version: 3.11 or 3.12 (recommended)
   - Click "Deploy!"

## Step 3: Wait for Deployment

- Streamlit Cloud will:
  - Install dependencies from `requirements.txt`
  - Build and deploy your app
  - Provide a public URL (e.g., `https://your-app.streamlit.app`)

## Step 4: Share Your App

Your app will be available at:
```
https://[your-custom-name].streamlit.app
```

You can share this URL with anyone!

## Troubleshooting

### If deployment fails:

1. **Check Python version compatibility**
   - Use Python 3.11 in advanced settings
   - PyArrow issue is already handled in the code

2. **Check requirements.txt**
   - Make sure all dependencies are listed
   - Streamlit Cloud automatically installs them

3. **Check logs**
   - Click "Manage app" → "View logs"
   - Look for error messages

4. **Data persistence**
   - Note: Files saved in `data/` folder will reset on each deployment
   - For persistent storage, consider using Streamlit's secrets or a database

## Managing Your App

- **Update app**: Just push changes to GitHub, it auto-deploys
- **View analytics**: Check visitor stats in Streamlit Cloud dashboard
- **Custom domain**: Available on paid plans
- **Password protection**: Available in settings

## Tips

✅ **Free tier includes:**
- Unlimited public apps
- 1 private app
- Community support

✅ **Best practices:**
- Keep your app lightweight
- Use caching (@st.cache_data)
- Optimize data loading
- Test locally before pushing

✅ **Sharing:**
- Share the URL directly
- Embed in websites (iframe)
- Add to GitHub README

## Need Help?

- Streamlit Docs: https://docs.streamlit.io/streamlit-cloud
- Community Forum: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/BartonChenTW/Rubik-s-cube-recorder/issues
