# 🚀 ShakespeareGPT Deployment Guide

This guide will help you deploy ShakespeareGPT using Railway (backend) and Vercel (frontend).

## 📋 Prerequisites

- GitHub account
- Railway account (railway.app)
- Vercel account (vercel.com)
- OpenAI API key
- ChromaDB Cloud account

## 🔧 Backend Deployment (Railway)

### 1. Prepare Your Repository

Make sure your repository has these files:
- `main.py` (FastAPI backend)
- `requirements.txt` (Python dependencies)
- `Procfile` (Railway deployment config)
- `.env` (environment variables - don't commit this!)

### 2. Deploy to Railway

1. **Go to Railway**: Visit [railway.app](https://railway.app) and sign in
2. **Create New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your ShakespeareGPT repository
4. **Railway will detect Python** and install dependencies automatically

### 3. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_API_KEY=your_chroma_api_key_here
CHROMA_TENANT_ID=your_chroma_tenant_id_here
CHROMA_DB_NAME=your_chroma_database_name_here
```

### 4. Deploy

Railway will automatically deploy your app. Note the generated URL (e.g., `https://shakespearegpt-backend.up.railway.app`)

### 5. Test Your Backend

Visit your Railway URL + `/docs` to see the FastAPI documentation and test endpoints.

## 🎨 Frontend Deployment (Vercel)

### 1. Prepare Frontend

Make sure your `frontend/` directory has:
- `package.json`
- `pages/index.tsx`
- `.env.local` (for local development)

### 2. Deploy to Vercel

1. **Go to Vercel**: Visit [vercel.com](https://vercel.com) and sign in
2. **Import Project**: Click "New Project" → Import Git Repository
3. **Select Repository**: Choose your ShakespeareGPT repository
4. **Configure Project**:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### 3. Configure Environment Variables

In Vercel dashboard, go to your project → Settings → Environment Variables and add:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-railway-backend-url.up.railway.app
```

### 4. Deploy

Click "Deploy" and Vercel will build and deploy your frontend.

## 🔗 Connect Frontend to Backend

Your frontend will automatically connect to your Railway backend using the `NEXT_PUBLIC_BACKEND_URL` environment variable.

## 🧪 Testing Your Deployment

### Test Backend Endpoints

```bash
# Health check
curl https://your-railway-url.up.railway.app/

# Get plays
curl https://your-railway-url.up.railway.app/plays

# Ask a question
curl -X POST https://your-railway-url.up.railway.app/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What does Hamlet say about death?"}'
```

### Test Frontend

Visit your Vercel URL and try asking questions about Shakespeare!

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure your backend has CORS middleware configured
2. **Environment Variables**: Double-check all API keys are set correctly
3. **Build Errors**: Check Railway/Vercel logs for dependency issues
4. **API Timeouts**: Consider increasing timeout limits for large responses

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check Vercel logs
vercel logs

# Test backend locally
uvicorn main:app --reload

# Test frontend locally
cd frontend && npm run dev
```

## 📈 Monitoring

- **Railway**: Monitor CPU, memory, and request logs
- **Vercel**: Check analytics and performance metrics
- **OpenAI**: Monitor API usage and costs
- **ChromaDB**: Check database performance

## 🎉 Success!

Your ShakespeareGPT is now live! Share your Vercel URL with the world.

## 🔄 Updates

To update your deployment:
1. Push changes to GitHub
2. Railway and Vercel will automatically redeploy
3. No manual intervention needed

---

**Need help?** Check the logs in Railway and Vercel dashboards for detailed error messages. 