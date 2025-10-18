# SleepFace - MongoDB Atlas Only Setup

## 🎯 **Atlas-Only Configuration**

This setup uses **MongoDB Atlas only** - no local MongoDB required.

### **📊 Database Structure**
```
MongoDB Atlas Cluster: cluster0.mwnoez2.mongodb.net
├── sleepface_dev (Development)
│   ├── users
│   ├── analyses
│   ├── summaries
│   └── user_sessions
│
└── sleepface (Production)
    ├── users
    ├── analyses
    ├── summaries
    └── user_sessions
```

## 🚀 **Quick Start**

### **Development Mode**
```bash
cd backend
export ENVIRONMENT=development
python3 start_atlas.py
```
- **Database**: `sleepface_dev` (Atlas)
- **Users**: Created in Atlas cloud
- **Debug**: Enabled

### **Production Mode**
```bash
cd backend
export ENVIRONMENT=production
python3 start_atlas.py
```
- **Database**: `sleepface` (Atlas)
- **Users**: Created in Atlas cloud
- **Debug**: Disabled

## 🔧 **Configuration Files**

### **Development (.env.development)**
```bash
ENVIRONMENT=development
MONGO_URL=mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=sleepface_dev
DEBUG=True
```

### **Production (.env.production)**
```bash
ENVIRONMENT=production
MONGO_URL=mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=sleepface
DEBUG=False
```

## 📍 **Where Users Are Created**

### **Development Mode (Current)**
- **Database**: `sleepface_dev` (MongoDB Atlas)
- **Collection**: `users`
- **Location**: Cloud (Atlas cluster)
- **Current Users**: 0

### **Production Mode**
- **Database**: `sleepface` (MongoDB Atlas)
- **Collection**: `users`
- **Location**: Cloud (Atlas cluster)
- **Current Users**: 0

## 🔍 **How to View Users**

### **MongoDB Atlas Web Interface**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Login with your account
3. Select cluster `cluster0`
4. Click "Browse Collections"
5. Choose database:
   - `sleepface_dev` (development)
   - `sleepface` (production)

### **Python Script**
```python
import pymongo

# Connect to Atlas
client = pymongo.MongoClient("mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Development database
dev_db = client['sleepface_dev']
print("Development users:", dev_db.users.count_documents({}))

# Production database
prod_db = client['sleepface']
print("Production users:", prod_db.users.count_documents({}))
```

## ✅ **Benefits of Atlas-Only Setup**

### **No Local Dependencies**
- ✅ **No MongoDB Installation**: No need to install local MongoDB
- ✅ **No Local Database**: Everything in the cloud
- ✅ **No Port Conflicts**: No local port 27017 needed
- ✅ **Clean Setup**: Simple, cloud-only configuration

### **Cloud Benefits**
- ✅ **Access Anywhere**: Access from any device
- ✅ **Automatic Backups**: Built-in backup system
- ✅ **Monitoring**: Atlas monitoring and alerts
- ✅ **Scaling**: Easy to scale as needed
- ✅ **Security**: Enterprise-grade security

### **Development Benefits**
- ✅ **Separate Environments**: Dev and prod isolated
- ✅ **Easy Switching**: Change environment with one variable
- ✅ **Consistent**: Same setup everywhere
- ✅ **Team Friendly**: Everyone uses same cloud setup

## 🚀 **Deployment Commands**

### **Start Development Server**
```bash
cd backend
export ENVIRONMENT=development
python3 start_atlas.py
```

### **Start Production Server**
```bash
cd backend
export ENVIRONMENT=production
python3 start_atlas.py
```

### **Docker Deployment**
```bash
# Build and run with Docker
docker-compose up -d

# Or build manually
docker build -t sleepface-backend ./backend
docker run -d -p 8000:8000 -e ENVIRONMENT=development sleepface-backend
```

## 🔒 **Security Notes**

- **Connection String**: Contains credentials (keep secure)
- **Environment Variables**: Use proper secret management
- **Network Access**: Configure IP whitelist in Atlas
- **Database Users**: Create specific database users for production

## 📈 **Monitoring**

### **Atlas Dashboard**
- **Metrics**: CPU, Memory, Connections
- **Alerts**: Set up alerts for issues
- **Logs**: View connection and query logs

### **Application Health**
- **Health Check**: `GET /health`
- **Database Status**: Check connection status
- **Error Tracking**: Monitor API errors

## 🎯 **Current Status**

- **Environment**: Development
- **Database**: `sleepface_dev` (Atlas)
- **Users**: 0 (fresh start)
- **Server**: Ready to start
- **Configuration**: Atlas-only setup complete

Your app is now fully configured to use MongoDB Atlas only! 🎉









