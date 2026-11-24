-- =============================================================================
-- INTELLIGENT WATER DISTRIBUTION SYSTEM DATABASE SCHEMA (MySQL / PostgreSQL)
-- =============================================================================

CREATE TABLE IF NOT EXISTS areas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    population INT DEFAULT 0,
    priority INT DEFAULT 4, -- 1: Emergency, 2: Hospital, 3: Essential, 4: Household, 5: Commercial, 6: Low
    daily_quota_litres DOUBLE DEFAULT 50000.0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    area_id INT,
    house_number VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'USER', -- 'USER' or 'ADMIN'
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tanks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tank_id VARCHAR(50) NOT NULL UNIQUE,
    tank_name VARCHAR(120) NOT NULL,
    location VARCHAR(150) NOT NULL,
    capacity DOUBLE NOT NULL,          -- In Litres
    current_level DOUBLE NOT NULL,     -- In Litres
    water_level_percentage DOUBLE GENERATED ALWAYS AS ((current_level / capacity) * 100) STORED,
    status VARCHAR(20) DEFAULT 'ACTIVE', -- 'ACTIVE', 'MAINTENANCE', 'OFFLINE'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS water_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    area_id INT NOT NULL,
    requested_quantity DOUBLE NOT NULL,
    allocated_quantity DOUBLE DEFAULT 0.0,
    request_date DATE NOT NULL,
    priority INT DEFAULT 4,             -- 1 to 6
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'ALLOCATED', 'COMPLETED'
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS distribution (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area_id INT NOT NULL,
    tank_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    allocated_quantity DOUBLE NOT NULL,
    status VARCHAR(20) DEFAULT 'SCHEDULED', -- 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE,
    FOREIGN KEY (tank_id) REFERENCES tanks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS water_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    area_id INT NOT NULL,
    quantity DOUBLE NOT NULL,           -- In Litres
    usage_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'TAP_SUPPLY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS leakage_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    area_id INT NOT NULL,
    location VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20) DEFAULT 'MODERATE', -- 'MINOR', 'MODERATE', 'HIGH', 'CRITICAL'
    loss_volume_litres DOUBLE DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'REPORTED', -- 'REPORTED', 'UNDER_REVIEW', 'REPAIRING', 'RESOLVED'
    admin_comment TEXT,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(30) DEFAULT 'INFO', -- 'INFO', 'ALERT', 'SCHEDULE', 'EMERGENCY'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rating INT DEFAULT 5,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Initial Mock Data for Demonstration
INSERT INTO areas (id, area_name, location, population, priority, daily_quota_litres, status) VALUES
(1, 'Poonamallee', 'Chennai West', 8500, 2, 85000.0, 'ACTIVE'),
(2, 'Avadi', 'Chennai Northwest', 12000, 3, 110000.0, 'ACTIVE'),
(3, 'Porur', 'Chennai Southwest', 9500, 2, 90000.0, 'ACTIVE'),
(4, 'Ambattur', 'Chennai North', 15000, 4, 130000.0, 'ACTIVE'),
(5, 'Guindy Industrial Area', 'Chennai South', 6000, 5, 60000.0, 'ACTIVE');

INSERT INTO tanks (id, tank_id, tank_name, location, capacity, current_level, status) VALUES
(1, 'T001', 'Poonamallee Main Reservoir', 'Poonamallee Hill', 150000.0, 115000.0, 'ACTIVE'),
(2, 'T002', 'Avadi Overhead Tank', 'Avadi Sector 4', 100000.0, 72000.0, 'ACTIVE'),
(3, 'T003', 'Porur Water Tower', 'Porur Junction', 80000.0, 48000.0, 'ACTIVE'),
(4, 'T004', 'Ambattur Feeder Tank', 'Ambattur Estate', 120000.0, 96000.0, 'ACTIVE');
