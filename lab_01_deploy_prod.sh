#!/bin/bash
# Lab 13.1 - Deploy a Production Replica Set with Docker Compose
# Includes keyFile authentication and admin bootstrap
set -e
cd "$(dirname "$0")"

echo "======================================="
echo "  Lab 13.1: Production Replica Set Deployment"
echo "======================================="

# Helper to run mongosh either locally or inside container
run_mongosh() {
  local target_container="$1"
  shift
  if command -v mongosh &> /dev/null; then
    mongosh "$@"
  else
    docker exec -i "$target_container" mongosh "$@"
  fi
}

# Step 1: Generate keyfile
echo ""
echo "=== Step 1: Generate keyfile ==="
if [ ! -f keyfile ]; then
  openssl rand -base64 756 > keyfile
  chmod 400 keyfile
  echo "[OK] Generated keyfile (756 bytes)"
else
  echo "[OK] keyfile already exists"
fi

# Step 2: Start containers
echo ""
echo "=== Step 2: Starting production containers ==="
docker compose -f docker-compose-production.yml down -v 2>/dev/null || true
docker compose -f docker-compose-production.yml up -d
echo "Waiting for containers to boot..."
sleep 10

# Step 3: Initiate replica set
echo ""
echo "=== Step 3: Initiating replica set ==="
run_mongosh prod-mongo-1 --quiet --port 27017 --eval '
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-rs0-1:27017", priority: 2 },
    { _id: 1, host: "mongo-rs0-2:27017" },
    { _id: 2, host: "mongo-rs0-3:27017", arbiterOnly: true }
  ]
});
print("[OK] Replica set initiated.");
'
echo "Waiting for election (15s)..."
sleep 15

# Step 4: Create admin user (using localhost exception on newly elected Primary)
echo ""
echo "=== Step 4: Creating admin user ==="
run_mongosh prod-mongo-1 --quiet --port 27017 --eval '
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
'

# Step 5: Verify replica set health and member states
echo ""
echo "=== Step 5: Verify Health ==="
run_mongosh prod-mongo-1 --quiet -u admin -p 'AdminPass123!' --authenticationDatabase admin --port 27017 --eval '
rs.status().members.forEach(m => print(" - " + m.name + ": " + m.stateStr + " (health=" + m.health + ")"));
'

# Step 6: Test write replication
echo ""
echo "=== Step 6: Test Write & Replication ==="
run_mongosh prod-mongo-1 --quiet -u admin -p 'AdminPass123!' --authenticationDatabase admin --port 27017 --eval '
db.getSiblingDB("prod_db").orders.insertOne({
  item: "Industrial Turbines",
  quantity: 12,
  status: "Shipped",
  timestamp: new Date()
});
print("[OK] Inserted order document into PRIMARY");
'

echo "Reading from SECONDARY..."
sleep 2
run_mongosh prod-mongo-2 --quiet -u admin -p 'AdminPass123!' --authenticationDatabase admin --port 27017 --eval '
db.getMongo().setReadPref("primaryPreferred");
printjson(db.getSiblingDB("prod_db").orders.find().toArray());
'

echo ""
echo "[OK] Production replica set is ready."
echo "Connection string (with auth):"
echo '  mongodb://admin:AdminPass123!@host.docker.internal:27017,host.docker.internal:27018,host.docker.internal:27019/admin?replicaSet=rs0&authSource=admin'
echo ""
echo "To stop: docker compose -f docker-compose-production.yml down -v"
