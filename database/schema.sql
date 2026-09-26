CREATE DATABASE IF NOT EXISTS support_ticket_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE support_ticket_db;

CREATE TABLE IF NOT EXISTS users (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(150) NOT NULL UNIQUE,
    first_name      VARCHAR(150) NOT NULL DEFAULT '',
    last_name       VARCHAR(150) NOT NULL DEFAULT '',
    name            VARCHAR(150) GENERATED ALWAYS AS (TRIM(CONCAT(first_name, ' ', last_name))) VIRTUAL,
    email           VARCHAR(254) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,       -- Django's `password` column (hashed, never plain text)
    role            ENUM('customer', 'agent') NOT NULL DEFAULT 'customer',
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    is_staff        TINYINT(1) NOT NULL DEFAULT 0,
    is_superuser    TINYINT(1) NOT NULL DEFAULT 0,
    last_login      DATETIME NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tickets (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL,                        -- customer who raised the ticket
    subject         VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    priority        ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    status          ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    assigned_to     BIGINT NULL,                             -- agent the ticket is assigned to
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tickets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_tickets_status (status),
    INDEX idx_tickets_priority (priority),
    INDEX idx_tickets_status_priority (status, priority),
    INDEX idx_tickets_created_at (created_at),
    INDEX idx_tickets_subject (subject),
    FULLTEXT INDEX ft_tickets_subject_description (subject, description)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ticket_comments (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    ticket_id       BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,                        -- author of the comment (customer or agent)
    comment         TEXT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_comments_ticket_id (ticket_id),
    INDEX idx_comments_created_at (created_at)
) ENGINE=InnoDB;

