PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS buildings (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  abbreviation TEXT NOT NULL UNIQUE,
  address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
  id INTEGER PRIMARY KEY,
  building_id INTEGER NOT NULL REFERENCES buildings(id),
  room_number TEXT NOT NULL,
  room_type TEXT NOT NULL CHECK (room_type IN ('Practice', 'Performance', 'Classroom', 'Rehearsal')),
  floor INTEGER NOT NULL,
  capacity INTEGER NOT NULL DEFAULT 1 CHECK (capacity > 0),
  has_climate_control INTEGER NOT NULL DEFAULT 1 CHECK (has_climate_control IN (0, 1)),
  UNIQUE (building_id, room_number)
);

CREATE TABLE IF NOT EXISTS pianos (
  id INTEGER PRIMARY KEY,
  serial_number TEXT NOT NULL UNIQUE,
  manufacturer TEXT NOT NULL,
  model TEXT NOT NULL,
  year_built INTEGER NOT NULL CHECK (year_built BETWEEN 1800 AND 2100),
  piano_type TEXT NOT NULL CHECK (piano_type IN ('Grand', 'Upright', 'Digital')),
  condition_status TEXT NOT NULL CHECK (condition_status IN ('Excellent', 'Good', 'Fair', 'Needs repair')),
  last_tuned_on TEXT NOT NULL,
  next_tuning_due TEXT NOT NULL,
  room_id INTEGER NOT NULL REFERENCES rooms(id),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'storage', 'retired'))
);

CREATE TABLE IF NOT EXISTS technicians (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  phone_number TEXT,
  specialty TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_records (
  id INTEGER PRIMARY KEY,
  piano_id INTEGER NOT NULL REFERENCES pianos(id),
  technician_id INTEGER NOT NULL REFERENCES technicians(id),
  work_type TEXT NOT NULL CHECK (work_type IN ('Tuning', 'Voicing', 'Action regulation', 'Repair', 'Inspection')),
  completed_on TEXT NOT NULL,
  cost REAL NOT NULL DEFAULT 0 CHECK (cost >= 0),
  notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  room_id INTEGER NOT NULL REFERENCES rooms(id),
  piano_id INTEGER REFERENCES pianos(id),
  title TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('Recital', 'Rehearsal', 'Masterclass', 'Lecture')),
  starts_at TEXT NOT NULL,
  ends_at TEXT NOT NULL,
  attendance INTEGER NOT NULL DEFAULT 0 CHECK (attendance >= 0),
  status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
  CHECK (ends_at > starts_at)
);

CREATE INDEX IF NOT EXISTS idx_pianos_room ON pianos(room_id);
CREATE INDEX IF NOT EXISTS idx_pianos_tuning_due ON pianos(next_tuning_due);
CREATE INDEX IF NOT EXISTS idx_maintenance_piano_date ON maintenance_records(piano_id, completed_on);
CREATE INDEX IF NOT EXISTS idx_events_start ON events(starts_at);
