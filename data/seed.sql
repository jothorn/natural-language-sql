INSERT INTO buildings (id, name, abbreviation, address) VALUES
  (1, 'Harmon Hall', 'HH', '1200 Campus Drive'),
  (2, 'North Arts Center', 'NAC', '44 College Avenue'),
  (3, 'Founders Auditorium', 'FA', '8 University Way');

INSERT INTO rooms (id, building_id, room_number, room_type, floor, capacity, has_climate_control) VALUES
  (1, 1, '101', 'Practice', 1, 2, 1), (2, 1, '104', 'Practice', 1, 2, 1),
  (3, 1, '210', 'Rehearsal', 2, 18, 1), (4, 1, 'Concert Hall', 'Performance', 1, 420, 1),
  (5, 2, 'B12', 'Practice', 0, 2, 0), (6, 2, '203', 'Classroom', 2, 32, 1),
  (7, 2, 'Studio A', 'Rehearsal', 1, 12, 1), (8, 3, 'Main Stage', 'Performance', 1, 650, 1),
  (9, 3, 'Green Room', 'Practice', 1, 6, 1);

INSERT INTO pianos (id, serial_number, manufacturer, model, year_built, piano_type, condition_status, last_tuned_on, next_tuning_due, room_id, status) VALUES
  (1, '10432', 'Steinway & Sons', 'Model B', 2014, 'Grand', 'Excellent', date('now','-120 days'), date('now','-30 days'), 4, 'active'),
  (2, '21876', 'Yamaha', 'C7X', 2019, 'Grand', 'Good', date('now','-45 days'), date('now','+45 days'), 8, 'active'),
  (3, '30911', 'Kawai', 'GX-2', 2017, 'Grand', 'Good', date('now','-70 days'), date('now','-10 days'), 3, 'active'),
  (4, '41205', 'Yamaha', 'U3', 2012, 'Upright', 'Fair', date('now','-160 days'), date('now','-40 days'), 1, 'active'),
  (5, '51773', 'Kawai', 'K-300', 2021, 'Upright', 'Excellent', date('now','-20 days'), date('now','+70 days'), 2, 'active'),
  (6, '62008', 'Steinway & Sons', 'Model D', 2008, 'Grand', 'Good', date('now','-75 days'), date('now','+15 days'), 8, 'active'),
  (7, '73449', 'Baldwin', 'Hamilton', 1998, 'Upright', 'Needs repair', date('now','-250 days'), date('now','-100 days'), 5, 'active'),
  (8, '84516', 'Yamaha', 'C3X', 2020, 'Grand', 'Excellent', date('now','-35 days'), date('now','+55 days'), 7, 'active'),
  (9, '95620', 'Roland', 'LX-708', 2023, 'Digital', 'Excellent', date('now','-60 days'), date('now','+120 days'), 6, 'active'),
  (10, '16704', 'Kawai', 'K-500', 2016, 'Upright', 'Good', date('now','-100 days'), date('now','-15 days'), 9, 'active'),
  (11, '27830', 'Yamaha', 'P22', 2003, 'Upright', 'Fair', date('now','-500 days'), date('now','-300 days'), 5, 'storage');

INSERT INTO technicians (id, name, email, phone_number, specialty) VALUES
  (1, 'Mara Chen', 'mara.chen@campus.example.edu', '720-555-0101', 'Concert grands'),
  (2, 'Luis Ortega', 'luis.ortega@campus.example.edu', '720-555-0102', 'Regulation and voicing'),
  (3, 'Priya Nair', 'priya.nair@campus.example.edu', '720-555-0103', 'Uprights and repairs'),
  (4, 'Elliot Brooks', 'elliot.brooks@campus.example.edu', '720-555-0104', 'Digital instruments');

INSERT INTO maintenance_records (id, piano_id, technician_id, work_type, completed_on, cost, notes) VALUES
  (1, 1, 1, 'Tuning', date('now','-120 days'), 185, 'Concert pitch tuning before faculty recital'),
  (2, 1, 2, 'Voicing', date('now','-210 days'), 240, 'Evened out upper register'),
  (3, 2, 1, 'Tuning', date('now','-45 days'), 165, 'Routine seasonal tuning'),
  (4, 3, 2, 'Tuning', date('now','-70 days'), 155, 'Routine tuning'),
  (5, 4, 3, 'Repair', date('now','-90 days'), 320, 'Replaced two worn hammers'),
  (6, 4, 3, 'Tuning', date('now','-160 days'), 145, 'Standard tuning'),
  (7, 5, 3, 'Tuning', date('now','-20 days'), 145, 'Routine tuning'),
  (8, 6, 1, 'Tuning', date('now','-75 days'), 195, 'Concert hall maintenance'),
  (9, 7, 3, 'Inspection', date('now','-35 days'), 85, 'Needs action assembly repair'),
  (10, 8, 2, 'Action regulation', date('now','-35 days'), 275, 'New studio setup'),
  (11, 9, 4, 'Inspection', date('now','-60 days'), 40, 'Firmware and key response check'),
  (12, 10, 3, 'Tuning', date('now','-100 days'), 145, 'Standard tuning'),
  (13, 1, 1, 'Tuning', date('now','-25 days'), 185, 'Seasonal tuning'),
  (14, 2, 1, 'Action regulation', date('now','-18 days'), 295, 'Prepared for upcoming recital'),
  (15, 4, 3, 'Repair', date('now','-12 days'), 180, 'Adjusted sticking key'),
  (16, 5, 3, 'Inspection', date('now','-8 days'), 65, 'Condition check'),
  (17, 8, 2, 'Tuning', date('now','-4 days'), 155, 'Studio tuning'),
  (18, 3, 2, 'Repair', date('now','-65 days'), 210, 'Replaced damper felt'),
  (19, 6, 1, 'Tuning', date('now','-10 days'), 195, 'Concert preparation');

INSERT INTO events (id, room_id, piano_id, title, event_type, starts_at, ends_at, attendance, status) VALUES
  (1, 4, 1, 'Autumn Faculty Recital', 'Recital', datetime('now','+3 days','start of day','+18 hours'), datetime('now','+3 days','start of day','+20 hours'), 280, 'scheduled'),
  (2, 8, 2, 'Young Artists Showcase', 'Recital', datetime('now','+8 days','start of day','+19 hours'), datetime('now','+8 days','start of day','+21 hours'), 410, 'scheduled'),
  (3, 3, 3, 'Chamber Ensemble Rehearsal', 'Rehearsal', datetime('now','+1 day','start of day','+14 hours'), datetime('now','+1 day','start of day','+16 hours'), 12, 'scheduled'),
  (4, 7, 8, 'Piano Studio Masterclass', 'Masterclass', datetime('now','+12 days','start of day','+15 hours'), datetime('now','+12 days','start of day','+17 hours'), 24, 'scheduled'),
  (5, 4, 1, 'Student Honors Recital', 'Recital', datetime('now','+20 days','start of day','+18 hours'), datetime('now','+20 days','start of day','+20 hours'), 190, 'scheduled'),
  (6, 6, 9, 'Music History Lecture', 'Lecture', datetime('now','+4 days','start of day','+10 hours'), datetime('now','+4 days','start of day','+11 hours'), 28, 'scheduled'),
  (7, 8, 6, 'Spring Gala', 'Recital', datetime('now','-120 days'), datetime('now','-120 days','+2 hours'), 500, 'completed'),
  (8, 9, 10, 'Practice Room Maintenance', 'Rehearsal', datetime('now','+2 days','start of day','+9 hours'), datetime('now','+2 days','start of day','+10 hours'), 2, 'cancelled');
