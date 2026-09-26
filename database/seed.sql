USE support_ticket_db;

INSERT INTO users (username, first_name, last_name, email, password_hash, role, is_active, is_staff, is_superuser, created_at) VALUES
('alice@example.com',   'Alice',   'Johnson', 'alice@example.com',   'pbkdf2_sha256$720000$78T3z4bvaekstNy5y06VYo$nRAbyJztQRbci5WHq3hqMjm60E7IXylRl8etcaB8oIU=', 'customer', 1, 0, 0, NOW()),
('bob@example.com',     'Bob',     'Martinez','bob@example.com',     'pbkdf2_sha256$720000$78T3z4bvaekstNy5y06VYo$nRAbyJztQRbci5WHq3hqMjm60E7IXylRl8etcaB8oIU=', 'customer', 1, 0, 0, NOW()),
('carol.agent@example.com', 'Carol', 'Nguyen', 'carol.agent@example.com', 'pbkdf2_sha256$720000$78T3z4bvaekstNy5y06VYo$nRAbyJztQRbci5WHq3hqMjm60E7IXylRl8etcaB8oIU=', 'agent', 1, 0, 0, NOW()),
('dave.agent@example.com',  'Dave',  'Okafor', 'dave.agent@example.com',  'pbkdf2_sha256$720000$78T3z4bvaekstNy5y06VYo$nRAbyJztQRbci5WHq3hqMjm60E7IXylRl8etcaB8oIU=', 'agent', 1, 0, 0, NOW());

INSERT INTO tickets (user_id, subject, description, priority, status, assigned_to, created_at, updated_at) VALUES
(1, 'Cannot reset my password', 'I requested a password reset email 20 minutes ago and it never arrived.', 'high', 'open', NULL, NOW(), NOW()),
(1, 'Invoice shows wrong amount', 'My March invoice charged me twice for the same subscription.', 'medium', 'in_progress', 3, NOW(), NOW()),
(2, 'Feature request: dark mode', 'Would love a dark mode option in the dashboard.', 'low', 'open', NULL, NOW(), NOW()),
(2, 'App crashes on file upload', 'The app crashes every time I try to upload a PDF larger than 5MB.', 'high', 'in_progress', 4, NOW(), NOW()),
(1, 'Old ticket - resolved already', 'This was resolved last week, keeping it for history.', 'low', 'resolved', 3, NOW(), NOW());

INSERT INTO ticket_comments (ticket_id, user_id, comment, created_at) VALUES
(1, 1, 'Still no email, could you check the spam folder policy on your end?', NOW()),
(2, 3, 'Looking into this now, can you confirm the invoice number?', NOW()),
(2, 1, 'Invoice number is INV-10432.', NOW()),
(4, 4, 'Reproduced the crash, working on a fix.', NOW()),
(5, 3, 'Confirmed resolved on our end, closing soon.', NOW());
