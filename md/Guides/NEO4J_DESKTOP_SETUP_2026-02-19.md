# Neo4j Desktop Setup for Chrystallum

**Date:** 2026-02-19  
**Purpose:** Complete setup guide for Neo4j Desktop with fresh Chrystallum database  
**Platform:** Windows

---

## 📥 **Step 1: Download & Install**

### Download

1. Go to: https://neo4j.com/download/
2. Click **"Download Neo4j Desktop"**
3. Fill out the form (or skip if you have account)
4. Download the Windows installer (.exe)

**Recommended Version:** Neo4j Desktop 1.5.x or newer (includes Neo4j 5.x)

### Install

1. Run the downloaded `.exe` file
2. Follow installation wizard
3. **Choose installation location** (default is fine)
4. Wait for installation to complete (~5 minutes)
5. Launch Neo4j Desktop when prompted

---

## 🔧 **Step 2: Create Chrystallum Database**

### Create New Project

1. **Open Neo4j Desktop**
2. Click **"New Project"** (or use "My Project")
3. **Name it:** "Chrystallum Knowledge Graph"

### Create Database (DBMS)

1. In your project, click **"Add"** → **"Local DBMS"**
2. **Settings:**
   - **Name:** `Chrystallum`
   - **Password:** `Chrystallum` (or your choice - remember it!)
   - **Version:** Neo4j 5.x (latest stable - **recommended**)
   - **Database name:** `chrystallum` (will be created automatically)

3. Click **"Create"**

### Start the Database

1. Click **"Start"** button on your Chrystallum DBMS
2. Wait for status to show **"Running"** (green indicator)
3. Database is ready!

---

## ✅ **Step 3: Verify Connection**

### Open Neo4j Browser

1. Click **"Open"** button on your Chrystallum DBMS
2. Or click **"Open with Neo4j Browser"**
3. Browser opens at: http://localhost:7474

### Run Test Query

In the browser, run:

```cypher
RETURN "Connection successful!" AS status;
```

**Expected:** Should return one row with the message

### Check Database Info

```cypher
CALL dbms.components() 
YIELD name, versions, edition 
RETURN name, versions[0] AS version, edition;
```

**Expected:** Should show Neo4j version and edition (Community or Enterprise)

---

## 🔗 **Step 4: Connection Details**

Once your database is running, these are your connection details:

```
URI: bolt://localhost:7687
Username: neo4j
Password: Chrystallum  (or whatever you set)
Database: chrystallum
```

### Test from Command Line

```powershell
cd C:\Projects\Graph1

# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum')); driver.verify_connectivity(); print('Connected!'); driver.close()"
```

**If successful:** You'll see "Connected!"

---

## 🚀 **Step 5: Ready for Fresh Rebuild**

Once connection is verified, you have **two options:**

### **Option A: Automated Batch File (Easiest)**

I'll create a Desktop-specific rebuild script:

```cmd
rebuild_chrystallum_desktop.bat
```

This will run all stages automatically.

### **Option B: Manual Commands** 

Run each stage yourself (from guide):
`md/Guides/FRESH_CHRYSTALLUM_REBUILD_2026-02-19.md`

Just replace the URI with `bolt://localhost:7687`

---

## 🎯 **What to Do Next**

**Tell me when:**
1. ✅ Neo4j Desktop installed
2. ✅ Chrystallum database created and **running**
3. ✅ Connection tested successfully

**Then I'll:**
- Create Desktop-specific rebuild script
- Execute the full rebuild (Temporal → Geographic)
- ~45 minutes to complete

---

## 💡 **Pro Tips**

### **Memory Settings (for large imports)**

If you're loading full Pleiades (42,000 places):

1. In Neo4j Desktop, click **"..."** menu on Chrystallum DBMS
2. Click **"Settings"**
3. Look for memory settings:
   ```
   dbms.memory.heap.initial_size=2G
   dbms.memory.heap.max_size=4G
   dbms.memory.pagecache.size=2G
   ```
4. Adjust if needed (more = faster imports)

### **Multiple Databases**

Desktop allows multiple databases per DBMS:
- Default: `neo4j` database
- Can create: `chrystallum`, `testing`, etc.
- Switch with: `:use chrystallum` in Browser

---

## 🆘 **Troubleshooting**

### "Port 7687 already in use"

**Cause:** Another Neo4j instance running  
**Solution:**
- Stop other Neo4j instances in Desktop
- Or change port in settings

### "Java not found"

**Cause:** Neo4j requires Java  
**Solution:** Neo4j Desktop includes Java - no action needed

### "Cannot start database"

**Cause:** Various (check Desktop logs)  
**Solution:**
- Click "Logs" in Desktop
- Look for error messages
- Share error with me

---

**Let me know when Desktop is installed and running - I'll guide you through the rebuild!** 🚀

