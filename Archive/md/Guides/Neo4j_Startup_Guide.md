# Neo4j Startup Guide

## Connection Settings

Based on your test script, Neo4j should be running at:
- **URI**: `bolt://localhost:7687` (default)
- **Username**: `neo4j` (default)
- **Password**: Set in your `.env` file

---

## Option 1: Neo4j Desktop (Recommended for Windows)

Neo4j Desktop is the easiest way to run Neo4j locally on Windows.

### Installation

1. **Download Neo4j Desktop**:
   - Visit: https://neo4j.com/download/
   - Download the Windows installer
   - Install and launch Neo4j Desktop

2. **Create a Database**:
   - When you first launch, create an account (free)
   - Click "New Project" → Give it a name (e.g., "Chrystallum")
   - Click "Add" → "Local DBMS" → Choose a name and password
   - **Important**: Remember this password! You'll need it for your `.env` file

3. **Start the Database**:
   - Click the ▶️ **Start** button next to your database
   - Wait for it to turn green (✅ Running)
   - The database should be accessible at `bolt://localhost:7687`

4. **Set Password**:
   - First time: You'll be prompted to set an initial password
   - Use this password in your `.env` file

### Creating `.env` File

Create a `.env` file in your project root with:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
```

Replace `your_password_here` with the password you set in Neo4j Desktop.

---

## Option 2: Docker (Alternative)

If you have Docker installed:

### Start Neo4j with Docker

```bash
docker run \
  --name neo4j-chrystallum \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j-data:/data \
  neo4j:latest
```

**Notes:**
- Port 7474: Browser UI (http://localhost:7474)
- Port 7687: Bolt protocol (for your Python connections)
- Replace `your_password` with your desired password
- Data persists in Docker volume `neo4j-data`

### Stop Neo4j

```bash
docker stop neo4j-chrystallum
```

### Start Existing Container

```bash
docker start neo4j-chrystallum
```

---

## Option 3: Neo4j Community Edition (Standalone)

1. **Download**:
   - Visit: https://neo4j.com/download-center/#community
   - Download Windows ZIP

2. **Install**:
   - Extract ZIP to a folder (e.g., `C:\neo4j`)
   - Open Command Prompt as Administrator

3. **Start**:
   ```cmd
   cd C:\neo4j\bin
   neo4j.bat console
   ```

4. **Set Password**:
   - First run: Default password is `neo4j`
   - You'll be prompted to change it
   - Or change it via browser: http://localhost:7474

---

## Verify Neo4j is Running

### Method 1: Browser UI

Open your web browser and go to:
```
http://localhost:7474
```

You should see the Neo4j Browser interface.

### Method 2: Test Script

Run your Python test script:

```bash
# Activate your virtual environment first
venv312\Scripts\activate

# Run the test
python test_neo4j_connection.py
```

You should see:
```
✅ Connection successful!
```

---

## Troubleshooting

### Port Already in Use

If port 7687 is already in use:

1. **Find what's using it**:
   ```cmd
   netstat -ano | findstr :7687
   ```

2. **Stop other Neo4j instances** or change the port in Neo4j Desktop

### Connection Refused

- Make sure Neo4j is actually running (check Neo4j Desktop)
- Verify the URI in `.env` matches your Neo4j setup
- Check firewall settings

### Wrong Password

- Reset password in Neo4j Desktop: Click on your database → Settings → Reset Password
- Update your `.env` file with the new password

### Can't Connect to Browser UI (7474)

- Neo4j Desktop: Click "Open" button to launch browser
- Docker: Check if port 7474 is mapped correctly
- Standalone: Make sure you started Neo4j with `neo4j.bat console`

---

## Quick Start Checklist

- [ ] Neo4j Desktop installed or Docker running
- [ ] Database created and started (green ✅ status)
- [ ] Password set and remembered
- [ ] `.env` file created with correct credentials
- [ ] Test connection: `python test_neo4j_connection.py` succeeds
- [ ] Browser UI accessible at http://localhost:7474

---

## Next Steps

Once Neo4j is running:

1. **Test Connection**: Run `python test_neo4j_connection.py`
2. **Load Test Data**: Import your Cypher script:
   ```bash
   # Copy/paste your Cypher script into Neo4j Browser, or:
   neo4j-admin import --nodes=your_nodes.csv --relationships=your_rels.csv
   ```
3. **Run Queries**: Use Neo4j Browser or your Python scripts

---

## Useful Commands (Neo4j Desktop)

- **Start**: Click ▶️ Start button
- **Stop**: Click ⏹️ Stop button  
- **Open Browser**: Click "Open" button
- **Reset Password**: Click database → Settings → Reset Password
- **View Logs**: Click database → Logs tab

