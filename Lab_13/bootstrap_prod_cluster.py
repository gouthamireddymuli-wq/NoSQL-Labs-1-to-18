"""Bootstrap script for Lab 13.1 Production Replica Set."""
import subprocess
import time

def run_in_mongo(cmd_args, script):
    cmd = ["docker", "exec", "-i", "prod-mongo-1", "mongosh", "--quiet"] + cmd_args
    res = subprocess.run(cmd, input=script, text=True, capture_output=True)
    return res.stdout, res.stderr, res.returncode

print("=== Step 3: Creating admin user ===")
admin_script = """
use admin;
try {
  db.createUser({
    user: "admin",
    pwd: "AdminPass123!",
    roles: [
      { role: "userAdminAnyDatabase", db: "admin" },
      { role: "clusterAdmin", db: "admin" },
      { role: "readWriteAnyDatabase", db: "admin" }
    ]
  });
  print("[OK] Admin user created.");
} catch(e) {
  print("[NOTICE] " + e.message);
}
"""
out, err, code = run_in_mongo(["--port", "27017"], admin_script)
print("STDOUT:", out.strip())
if err:
    print("STDERR:", err.strip())

print("\n=== Step 4: Initiating replica set ===")
init_script = """
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
out, err, code = run_in_mongo([
    "-u", "admin", "-p", "AdminPass123!",
    "--authenticationDatabase", "admin",
    "--port", "27017"
], init_script)
print("STDOUT:", out.strip())
if err:
    print("STDERR:", err.strip())

print("\nWaiting 15 seconds for primary election...")
time.sleep(15)

print("\n=== Step 5: Verify Cluster Health ===")
status_script = """
var status = rs.status();
print("Replica Set Name: " + status.set);
print("Cluster State / Members:");
status.members.forEach(function(m) {
  print("  * Member " + m._id + ": " + m.name + " -> " + m.stateStr + " (health: " + m.health + ")");
});
"""
out, err, code = run_in_mongo([
    "-u", "admin", "-p", "AdminPass123!",
    "--authenticationDatabase", "admin",
    "--port", "27017"
], status_script)
print("STDOUT:\n" + out.strip())
if err:
    print("STDERR:", err.strip())
