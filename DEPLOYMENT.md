# SleepFace Deployment Guide

## 🚀 Production-Ready Configuration

This guide explains how to properly deploy SleepFace in different environments.

## 📁 Environment Structure

```
backend/
├── .env.development    # Local development
├── .env.production     # Production deployment
├── config.py          # Environment configuration
├── start.py           # Startup script
└── Dockerfile         # Production container
```

## 🔧 Environment Configuration

### Development Environment
```bash
# Set environment
export ENVIRONMENT=development

# Start with local MongoDB
python start.py
```

### Production Environment
```bash
# Set environment
export ENVIRONMENT=production

# Set production environment variables
export JWT_SECRET_KEY="your-production-secret-key"
export FIREBASE_PROJECT_ID="your-production-project-id"
# ... other production variables

# Start with MongoDB Atlas
python start.py
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build backend image
docker build -t sleepface-backend ./backend

# Run with production environment
docker run -d \
  --name sleepface-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e JWT_SECRET_KEY="your-secret" \
  sleepface-backend
```

## 🌐 Cloud Deployment

### MongoDB Atlas (Recommended for Production)
1. Create MongoDB Atlas cluster
2. Get connection string
3. Set `MONGO_URL` environment variable
4. Deploy backend with production environment

### Environment Variables for Production
```bash
ENVIRONMENT=production
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=sleepface
JWT_SECRET_KEY=your-secure-secret-key
FIREBASE_PROJECT_ID=your-project-id
# ... other Firebase variables
```

## 🔒 Security Considerations

### Production Checklist
- [ ] Use strong JWT secret key
- [ ] Enable MongoDB Atlas security features
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in production
- [ ] Set up proper logging
- [ ] Configure monitoring
- [ ] Set up backups

### Environment Variable Security
- Never commit `.env.production` to version control
- Use secret management services (AWS Secrets Manager, etc.)
- Rotate secrets regularly
- Use different secrets for different environments

## 📊 Database Strategy

### Development
- **Database**: `sleepface_dev` (local MongoDB)
- **Purpose**: Local development and testing
- **Data**: Can be reset/cleared frequently

### Production
- **Database**: `sleepface` (MongoDB Atlas)
- **Purpose**: Live user data
- **Data**: Persistent, backed up, monitored

## 🚀 Quick Start Commands

### Development
```bash
# Start local development
cd backend
export ENVIRONMENT=development
python start.py
```

### Production
```bash
# Deploy to production
export ENVIRONMENT=production
export JWT_SECRET_KEY="your-secret"
python start.py
```

### Docker
```bash
# Start with Docker
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues
1. **Database Connection**: Check `MONGO_URL` and network access
2. **Environment Variables**: Ensure all required variables are set
3. **Port Conflicts**: Check if port 8000 is available
4. **Dependencies**: Ensure all Python packages are installed

### Logs
```bash
# View application logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f mongodb-dev
```

## 📈 Monitoring

### Health Checks
- Backend: `GET /health`
- Database: Check MongoDB connection
- API: Monitor response times

### Metrics to Monitor
- API response times
- Database connection status
- Error rates
- User registration/login rates
- Memory and CPU usage









