# Gita Backend - Vercel Deployment Guide

This guide will help you deploy your Python FastAPI backend to Vercel.

## Prerequisites

1. **Vercel CLI** installed:

   ```bash
   npm install -g vercel
   ```

2. **Git** repository with your code

3. **Supabase** project set up with the required environment variables

## Project Structure

```
backend/
├── api/
│   └── index.py          # Vercel entry point
├── agents/               # Your agent modules
├── server.py            # Main FastAPI app
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── supabase_config.py  # Supabase configuration
```

## Environment Variables

You'll need to set these environment variables in Vercel:

1. **SUPABASE_URL**: Your Supabase project URL
2. **SUPABASE_ANON_KEY**: Your Supabase anonymous key

## Deployment Steps

### 1. Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy from the backend directory

```bash
cd backend
vercel
```

### 4. Set Environment Variables

After the initial deployment, set your environment variables:

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
```

Or set them in the Vercel dashboard:

1. Go to your project in the Vercel dashboard
2. Navigate to Settings → Environment Variables
3. Add the required variables

### 5. Redeploy with Environment Variables

```bash
vercel --prod
```

## Important Notes

### File System Limitations

Vercel's serverless functions have limitations:

- **No persistent file system**: Files uploaded to `/uploads` will not persist
- **Temporary storage only**: Use Supabase storage for file uploads
- **Function timeout**: Functions have a maximum execution time (usually 10-60 seconds)

### Recommended Changes for Production

1. **File Uploads**: Modify your upload endpoint to directly upload to Supabase storage instead of local filesystem
2. **Video Processing**: Consider using external services for heavy video processing
3. **Environment Variables**: Always use environment variables for sensitive data

### Testing Your Deployment

After deployment, test your endpoints:

```bash
# Health check
curl https://your-vercel-app.vercel.app/health

# API documentation
curl https://your-vercel-app.vercel.app/docs
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Environment Variables**: Verify all required env vars are set in Vercel
3. **File System**: Remember that Vercel functions don't have persistent storage
4. **Timeout**: Long-running operations may timeout

### Debugging

Check Vercel function logs:

```bash
vercel logs
```

## Local Development

For local development, you can still run your FastAPI server:

```bash
cd backend
pip install -r requirements.txt
python server.py
```

The server will run on `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /upload-video` - Upload and process video
- `POST /generate-music-from-video` - Generate music from video
- `GET /docs` - Interactive API documentation
