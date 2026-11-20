"""Lab 13.1 - Deploy a Production Replica Set with Docker Compose & Keyfile Auth.
Author: M Gouthami (24BTRCL130)

Step-by-step automation:
1. Cryptographic Keyfile Generation (756 random bytes, 400 permissions)
2. Production Container Orchestration (3-member set with --keyFile and --auth)
3. Replica Set Initiation (rs0 with primary, secondary, arbiter)
4. Bootstrap Admin User Creation (via localhost exception on newly elected Primary)
5. Cluster Health, Election & Inter-member Replication Verification
"""

import os
import sys
import time
import base64
import secrets
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYFILE_PATH = os.path.join(BASE_DIR, "keyfile")
COMPOSE_FILE = os.path.join(BASE_DIR, "docker-compose-production.yml")

def banner(msg: str):
    line = "=" * (len(msg) + 8)
    print(f"\n{line}\n  [SEC] {msg}\n{line}")

def generate_keyfile():
    """Generates a secure keyfile if it doesn't already exist."""
    print("\n=== Step 1: Generate keyfile ===")
    if not os.path.exists(KEYFILE_PATH):
        raw_key = secrets.token_bytes(567)
        encoded = base64.b64encode(raw_key).decode("ascii")
        with open(KEYFILE_PATH, "w", newline="\n") as f:
            f.write(encoded + "\n")
        try:
            os.chmod(KEYFILE_PATH, 0o400)
        except Exception:
            pass
        print(f"  [OK] Generated keyfile at {KEYFILE_PATH} ({len(encoded)} bytes)")
    else:
        print(f"  [OK] keyfile already exists at {KEYFILE_PATH}")

def start_containers():
    """Starts the 3-node MongoDB cluster via Docker Compose."""
    print("\n=== Step 2: Starting production containers ===")
    cmd_down = ["docker", "compose", "-f", COMPOSE_FILE, "down", "-v"]
    subprocess.run(cmd_down, capture_output=True, text=True, cwd=BASE_DIR)

    cmd_up = ["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"]
    result = subprocess.run(cmd_up, capture_output=True, text=True, cwd=BASE_DIR)
    if result.returncode != 0:
        print("  [ERROR] docker compose up failed:")
        print(result.stderr)
        return False
    print("  [OK] Containers deployed. Waiting 10 seconds for mongod boot...")
    time.sleep(10)
    return True

def initiate_replica_set():
    """Initiates the replica set."""
    print("\n=== Step 3: Initiating replica set ===")
    script = """
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-rs0-1:27017", priority: 2 },
    { _id: 1, host: "mongo-rs0-2:27017" },
    { _id: 2, host: "mongo-rs0-3:27017", arbiterOnly: true }
  ]
});
print("[OK] Replica set initiated.");
"""
    cmd = ["docker", "exec", "-i", "prod-mongo-1", "mongosh", "--quiet", "--port", "27017"]
    res = subprocess.run(cmd, input=script, capture_output=True, text=True)
    print(res.stdout.strip() or res.stderr.strip())
    print("  Waiting 15 seconds for primary election...")
    time.sleep(15)
    return True

def create_admin_user():
    """Create root admin user using localhost exception on the Primary."""
    print("\n=== Step 4: Creating admin user ===")
    script = """
db.getSiblingDB("admin").createUser({
  user: "admin",
  pwd: "AdminPass123!",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "clusterAdmin", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
});
print("[OK] Admin user created on Primary.");
"""
    cmd = ["docker", "exec", "-i", "prod-mongo-1", "mongosh", "--quiet", "--port", "27017"]
    res = subprocess.run(cmd, input=script, capture_output=True, text=True)
    print(res.stdout.strip() or res.stderr.strip())
    return True

def verify_cluster():
    """Verifies cluster health and member states with admin auth."""
    print("\n=== Step 5: Verify Health ===")
    script = """
var status = rs.status();
print("Replica Set Name: " + status.set);
print("Members Status:");
status.members.forEach(m => {
  print(" - " + m.name + " (" + m.stateStr + ") [health=" + m.health + "]");
});
"""
    cmd = [
        "docker", "exec", "-i", "prod-mongo-1",
        "mongosh", "--quiet",
        "-u", "admin", "-p", "AdminPass123!",
        "--authenticationDatabase", "admin",
        "--port", "27017"
    ]
    res = subprocess.run(cmd, input=script, capture_output=True, text=True)
    print(res.stdout.strip() or res.stderr.strip())
    return res.stdout

def test_replication():
    """Tests writing to primary and reading from secondary."""
    print("\n=== Step 6: Test Write & Replication ===")
    write_script = """
db.getSiblingDB("prod_db").orders.insertOne({
  item: "Industrial Turbines",
  quantity: 12,
  status: "Shipped",
  timestamp: new Date()
});
print("[OK] Inserted order document into PRIMARY");
"""
    cmd_write = [
        "docker", "exec", "-i", "prod-mongo-1",
        "mongosh", "--quiet",
        "-u", "admin", "-p", "AdminPass123!",
        "--authenticationDatabase", "admin",
        "--port", "27017"
    ]
    res = subprocess.run(cmd_write, input=write_script, capture_output=True, text=True)
    print(res.stdout.strip())

    time.sleep(2)
    read_script = """
db.getMongo().setReadPref("primaryPreferred");
printjson(db.getSiblingDB("prod_db").orders.find().toArray());
"""
    cmd_read = [
        "docker", "exec", "-i", "prod-mongo-2",
        "mongosh", "--quiet",
        "-u", "admin", "-p", "AdminPass123!",
        "--authenticationDatabase", "admin",
        "--port", "27017"
    ]
    res = subprocess.run(cmd_read, input=read_script, capture_output=True, text=True)
    print("Secondary Read Output:")
    print(res.stdout.strip() or res.stderr.strip())

def get_cluster_status_json():
    """Returns json-serialized cluster status for web dashboard."""
    script = """
try {
  var s = rs.status();
  var members = s.members.map(m => ({
    name: m.name,
    state: m.stateStr,
    health: m.health,
    uptime: m.uptime
  }));
  print(JSON.stringify({ok: 1, set: s.set, members: members}));
} catch(e) {
  print(JSON.stringify({ok: 0, error: e.message}));
}
"""
    cmd = [
        "docker", "exec", "-i", "prod-mongo-1",
        "mongosh", "--quiet",
        "-u", "admin", "-p", "AdminPass123!",
        "--authenticationDatabase", "admin",
        "--port", "27017"
    ]
    try:
        res = subprocess.run(cmd, input=script, capture_output=True, text=True, timeout=10)
        for line in res.stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
    except Exception as ex:
        return {"ok": 0, "error": str(ex)}
    return {"ok": 0, "error": "No cluster response"}

def main():
    banner("Lab 13.1: Production Replica Set Deployment with Keyfile Auth")
    generate_keyfile()
    if not start_containers():
        sys.exit(1)
    initiate_replica_set()
    create_admin_user()
    verify_cluster()
    test_replication()

    print("\n[OK] Production replica set is ready.")
    print("Connection string (with auth):")
    print('  mongodb://admin:AdminPass123!@host.docker.internal:27017,host.docker.internal:27018,host.docker.internal:27019/admin?replicaSet=rs0&authSource=admin')
    print("\nTo stop: docker compose -f docker-compose-production.yml down -v")

if __name__ == "__main__":
    main()
