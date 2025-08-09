// init.js
db = db.getSiblingDB('emealio_phase_db');

db.createCollection('log');
db.createCollection('user');
db.createCollection('users_food_history');

print("✅ emealio_phase_db initialized with log, user, and users_food_history collections.");
