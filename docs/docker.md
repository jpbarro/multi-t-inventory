# 🐳 Docker Cheat Sheet

**Prerequisite:** All commands must be run from the **Root Directory** of the repository (where `docker-compose.yml` lives).

## 🚀 1. Day-to-Day Development

These are the commands you will use 90% of the time to start and stop your environment.

| Action | Command | Description |
| --- | --- | --- |
| **Start Everything** | `docker compose up` | Starts backend and database. Logs stream to your terminal. Press `Ctrl+C` to stop. |
| **Start in Background** | `docker compose up -d` | "Detached" mode. Returns control to your terminal immediately. |
| **Stop & Remove** | `docker compose down` | Stops containers and removes the networks (preserves data). |
| **Stop Only** | `docker compose stop` | Pauses the containers without removing them. |
| **Restart Services** | `docker compose restart` | Quick reboot of all running containers. |

---

## 🔍 2. Monitoring & Logs

When something breaks, use these to see what's happening inside the containers.

**View Logs:**

```bash
# Stream logs for all services
docker compose logs -f

# Stream logs ONLY for the Backend API
docker compose logs -f api

# Stream logs ONLY for the Database
docker compose logs -f db

```

**Check Status:**

```bash
# See what is running and which ports are open
docker compose ps

```

---

## 🛠 3. Backend Management

Since your backend is isolated in a container, you need specific commands to interact with it (e.g., running tests or installing packages).

**Access the Container Shell:**
This is like "SSH-ing" into your running backend machine.

```bash
docker compose exec api /bin/bash
# You are now inside the container! Type 'exit' to leave.

```

**Run Tests (Pytest):**
Run your test suite inside the container environment.

```bash
docker compose exec api pytest

```

**Install a New Package:**
If you add a package to `requirements.txt`, you need to rebuild the image.

```bash
# 1. Add package to backend/requirements.txt
# 2. Run this to rebuild the container with the new dep:
docker compose up -d --build api

```

---

## 🗄 4. Database Management (Postgres)

**Connect to the Database directly:**
Opens the `psql` command line tool inside the database container.

```bash
docker compose exec db psql -U postgres -d app_db

```

* **Check tables:** `\dt`
* **Quit:** `\q`

**Nuke Everything (Factory Reset):**
⚠️ **DANGER:** This deletes the database volume and **all your data**. Use this if you messed up your schema and want to start fresh.

```bash
docker compose down -v
docker compose up -d

```

---

## 🧹 5. Housekeeping & Troubleshooting

**Force Rebuild:**
If code changes aren't showing up or weird caching issues occur.

```bash
docker compose build --no-cache

```

**Clean Up Space:**
Removes stopped containers, unused networks, and dangling images.

```bash
docker system prune -f

```