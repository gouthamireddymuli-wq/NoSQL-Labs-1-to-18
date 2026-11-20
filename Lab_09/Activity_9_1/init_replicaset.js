/**
 * Initialise 3-Node MongoDB Replica Set for Write Concern Testing
 * Replica Set Name: rs0
 */
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-rs0-1:27017", priority: 2 },
    { _id: 1, host: "mongo-rs0-2:27018", priority: 1 },
    { _id: 2, host: "mongo-rs0-3:27019", priority: 1 }
  ]
});

// Wait for primary to elect
while (!rs.isMaster().ismaster) {
  print("Waiting for primary election...");
  sleep(1000);
}

print("\nReplica Set rs0 Successfully Initialised!");
rs.status();
