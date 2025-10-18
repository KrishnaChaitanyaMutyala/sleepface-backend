# MongoDB Atlas Setup for Development & Production

## 🎯 **Current Configuration**

### **Development Environment**
- **Database**: `sleepface_dev` (MongoDB Atlas)
- **Purpose**: Development and testing
- **Data**: Can be reset/cleared frequently
- **Collections**: Will be created automatically

### **Production Environment**
- **Database**: `sleepface` (MongoDB Atlas)
- **Purpose**: Live user data
- **Data**: Persistent, backed up, monitored
- **Collections**: Will be created automatically

## 🚀 **How to Use**

### **Development Mode**
```bash
cd backend
export ENVIRONMENT=development
python3 start.py
```
- **Database**: `sleepface_dev` in Atlas
- **Users**: Created in `sleepface_dev.users`
- **Debug**: Enabled

### **Production Mode**
```bash
cd backend
export ENVIRONMENT=production
python3 start.py
```
- **Database**: `sleepface` in Atlas
- **Users**: Created in `sleepface.users`
- **Debug**: Disabled

## 📊 **Database Structure**

### **Atlas Cluster: cluster0.mwnoez2.mongodb.net**
```
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

## 🔧 **Environment Variables**

### **Development (.env.development)**
```bash
MONGO_URL=mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=sleepface_dev
DEBUG=True
```

### **Production (.env.production)**
```bash
MONGO_URL=mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=sleepface
DEBUG=False
```

## 🎯 **Benefits of This Setup**

### **✅ Advantages**
- **No Local MongoDB**: No need to install/run local MongoDB
- **Cloud Access**: Access from anywhere
- **Backup**: Automatic backups in Atlas
- **Monitoring**: Built-in monitoring and alerts
- **Scaling**: Easy to scale as needed
- **Security**: Enterprise-grade security
- **Separation**: Clear dev/prod separation

### **✅ Cost Effective**
- **Free Tier**: 512MB storage, shared clusters
- **Development**: Free for development use
- **Production**: Pay only for what you use

## 🔍 **How to View Data**

### **MongoDB Atlas Web Interface**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Login with your account
3. Select cluster `cluster0`
4. Click "Browse Collections"
5. Choose database: `sleepface_dev` or `sleepface`

### **MongoDB Compass**
```
Connection String: mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

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

## 🚀 **Quick Start Commands**

### **Start Development Server**
```bash
cd backend
export ENVIRONMENT=development
python3 start.py
```

### **Start Production Server**
```bash
cd backend
export ENVIRONMENT=production
python3 start.py
```

### **Check Database Status**
```bash
python3 -c "
from config import get_database_config
print('Current config:', get_database_config())
"
```

## 🔒 **Security Notes**

- **Connection String**: Contains credentials (keep secure)
- **Network Access**: Configure IP whitelist in Atlas
- **Database Users**: Create specific database users for production
- **Environment Variables**: Use proper secret management

## 📈 **Monitoring**

### **Atlas Monitoring**
- **Metrics**: CPU, Memory, Connections
- **Alerts**: Set up alerts for issues
- **Logs**: View connection and query logs

### **Application Monitoring**
- **Health Check**: `GET /health`
- **Database Status**: Check connection status
- **Error Tracking**: Monitor API errors









