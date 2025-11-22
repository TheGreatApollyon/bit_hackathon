# Render Deployment Guide for HealthCredX

## 🚀 Quick Deploy to Render

### Gunicorn Command

Use this command as the **Start Command** in Render:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
```

### Explanation of Parameters:
- `app:app` - Points to the Flask app instance in app.py
- `--bind 0.0.0.0:$PORT` - Binds to all interfaces on Render's dynamic port
- `--workers 2` - Number of worker processes (adjust based on your Render plan)
- `--threads 2` - Number of threads per worker
- `--timeout 120` - Request timeout (120 seconds for AI operations)

---

## 📋 Step-by-Step Deployment

### 1. **Create a New Web Service on Render**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `TheGreatApollyon/bit_hackathon`

### 2. **Configure Build Settings**

| Setting | Value |
|---------|-------|
| **Name** | `healthcredx` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | Leave empty (use root) |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120` |

### 3. **Environment Variables**

Add these environment variables in Render dashboard:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your_actual_api_key` | Your Google Gemini API key |
| `SECRET_KEY` | `random_secure_string` | Flask secret key (generate a secure one) |
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `PORT` | `10000` | Render automatically sets this |

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. **Instance Type**

- **Free Tier**: Good for testing (spins down after 15 min of inactivity)
- **Starter ($7/month)**: Recommended for demos/hackathons
- **Standard**: For production use

---

## 📁 Files Required (Already Created)

✅ `requirements.txt` - Updated with gunicorn and all dependencies
✅ `build.sh` - Build script that installs dependencies and initializes database
✅ `app.py` - Modified to work with gunicorn (doesn't reset DB in production)

---

## 🔧 Alternative Gunicorn Commands

### For Better Performance (Paid Plans):
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --threads 4 --worker-class sync --timeout 120 --keep-alive 5
```

### For Development/Testing:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 60 --reload
```

### With Access Logs:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile -
```

---

## 🗄️ Database Considerations

### Current Setup (SQLite):
- The app uses SQLite which works on Render
- **Important**: SQLite files are **ephemeral** on Render's free tier (data lost on redeploy)
- Database is automatically initialized on first run via `build.sh`

### For Persistent Data (Recommended for Production):

1. **Upgrade to PostgreSQL** (Render provides free PostgreSQL):
   - Add `psycopg2-binary` to requirements.txt
   - Update database.py to use PostgreSQL
   - Get PostgreSQL connection string from Render

2. **Use Render Disk** (Paid feature):
   - Mount a persistent disk at `/opt/render/project/src/data`
   - Keeps SQLite database across deploys

---

## 🌐 Post-Deployment

### Your App URL:
```
https://healthcredx.onrender.com
```
(Replace with your actual Render URL)

### Test the Deployment:

1. Visit your Render URL
2. Login with test accounts:
   - Admin: `admin@healthcredx.com` / `admin123`
   - Doctor: `doctor@test.com` / `password`
   - Patient: `patient@test.com` / `password`

### Monitor Logs:
- Go to Render Dashboard → Your Service → Logs
- Watch for any errors during startup

---

## 🔍 Troubleshooting

### Issue: App fails to start
**Solution**: Check Render logs for errors. Common issues:
- Missing environment variables (GEMINI_API_KEY)
- Build script permissions (ensure build.sh is executable)

### Issue: Database not initializing
**Solution**: Check build.sh logs. Ensure `init_db.py` runs successfully.

### Issue: 504 Gateway Timeout
**Solution**: Increase timeout in gunicorn command:
```bash
--timeout 180
```

### Issue: Workers crashing
**Solution**: Reduce workers for free tier:
```bash
--workers 1 --threads 1
```

---

## 📊 Production Optimizations

### 1. **Use a Process Manager** (Already using Gunicorn ✅)

### 2. **Add Health Check Endpoint**
Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200
```

### 3. **Configure Logging**
Gunicorn already logs to stdout (Render captures this)

### 4. **Static File Serving**
For production, consider using CDN or nginx for static files

---

## 🔐 Security Checklist

- ✅ SECRET_KEY is set to a random secure value
- ✅ GEMINI_API_KEY is stored in environment variables (not in code)
- ✅ Debug mode is OFF in production
- ⚠️ Consider adding rate limiting for API endpoints
- ⚠️ Consider adding HTTPS redirect (Render provides SSL automatically)

---

## 💰 Cost Estimate

| Plan | Cost | Specs |
|------|------|-------|
| **Free** | $0/month | 512 MB RAM, spins down after 15 min |
| **Starter** | $7/month | 512 MB RAM, always on |
| **Standard** | $25/month | 2 GB RAM, better performance |

**Recommended**: Start with Free tier for testing, upgrade to Starter for hackathon demo.

---

## 📝 Deployment Checklist

- [ ] Push latest code to GitHub (`git push origin main`)
- [ ] Create new Web Service on Render
- [ ] Configure build and start commands
- [ ] Add environment variables (GEMINI_API_KEY, SECRET_KEY)
- [ ] Deploy and monitor logs
- [ ] Test all user roles and features
- [ ] Share deployment URL with team/judges

---

## 🎯 Next Steps After Deployment

1. **Custom Domain** (Optional):
   - Add your custom domain in Render settings
   - Update DNS records

2. **Monitoring**:
   - Set up uptime monitoring (UptimeRobot, Pingdom)
   - Configure error notifications

3. **Database Backup** (If using persistent data):
   - Set up automated backups
   - Test restore procedures

---

## 📞 Support

- **Render Documentation**: https://render.com/docs
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Flask Deployment Guide**: https://flask.palletsprojects.com/en/3.0.x/deploying/

---

**Good luck with your deployment! 🚀**

*For issues, check Render logs first. Most problems are related to environment variables or build script execution.*
