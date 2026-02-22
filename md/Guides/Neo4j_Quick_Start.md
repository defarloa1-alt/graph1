# Neo4j Quick Start - Your Setup

You have Neo4j Desktop installed with 2 databases:
- **System** (internal, don't use)
- **neo4j** (your main database - USE THIS ONE)

## Steps to Start

### 1. Start the Database

1. Open **Neo4j Desktop**
2. Find the **"neo4j"** database (NOT "system")
3. Click the **▶️ Start** button next to it
4. Wait for the status to turn **green (✅ Running)**
   - This usually takes 10-30 seconds

### 2. Check Your Password

If you've used this database before:
- You should already know the password
- If not, you'll need to reset it (see below)

### 3. Create/Update `.env` File

In your project root (`C:\Projects\federated-graph-framework\graph 3`), create or update `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
```

**Replace `your_password_here` with your actual Neo4j password.**

### 4. Reset Password (If Needed)

If you don't remember your password:

1. In Neo4j Desktop, click on the **"neo4j"** database
2. Click **"..." (three dots)** or right-click → **Settings**
3. Look for **"Reset Password"** or **"Change Password"**
4. Set a new password
5. **Update your `.env` file** with the new password

### 5. Test Connection

Once the database is running (green ✅):

```bash
# Activate virtual environment
venv312\Scripts\activate

# Test connection
python test_neo4j_connection.py
```

You should see:
```
✅ Connection successful!
```

### 6. Open Browser UI (Op Activate virtual environment
venvtional)

In Neo4j Desktop:
- Click the **"Open"** button next to your running database
- Or go to: http://localhost:7474
- Login with:
  - Username: `neo4j`
  - Password: (your password)

---

## Troubleshooting

### Database Won't Start

- Make sure no other Neo4j instance is running
- Try stopping and restarting
- Check for error messages in Neo4j Desktop logs

### Wrong Password

- Reset password in Neo4j Desktop (Settings → Reset Password)
- Update `.env` file with new password
- Test connection again

### Port Already in Use

If you see "port 7687 already in use":
- You might have another Neo4j instance running
- Stop all Neo4j databases, then start the one you want
- Or restart your computer

### Connection Refused

- Make sure the database shows **green (✅ Running)** status
- Wait a bit longer after clicking Start (it needs time to initialize)
- Check that `.env` file has correct URI: `bolt://localhost:7687`

---

## Next Steps

Once connected:
1. ✅ Test connection works
2. 📝 Load your Cypher script (`test_kingdom_to_sulla.cypher`)
3. 🔍 Run queries in Neo4j Browser or via Python






