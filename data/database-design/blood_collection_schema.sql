-- Patient Table
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY,
    mrn VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(10),
    allergies TEXT,
    contact_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Healthcare Provider Table
CREATE TABLE healthcare_providers (
    provider_id UUID PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    license_number VARCHAR(50),
    contact_number VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Blood Collection Orders Table
CREATE TABLE blood_collection_orders (
    order_id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id),
    ordering_provider_id UUID REFERENCES healthcare_providers(provider_id),
    order_datetime TIMESTAMP NOT NULL,
    priority VARCHAR(20) NOT NULL, -- (Routine/STAT/Urgent)
    status VARCHAR(30) NOT NULL, -- (Pending/In Progress/Completed/Cancelled)
    special_instructions TEXT,
    diagnosis_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Test Catalog Table
CREATE TABLE test_catalog (
    test_id UUID PRIMARY KEY,
    test_code VARCHAR(20) UNIQUE NOT NULL,
    test_name VARCHAR(200) NOT NULL,
    tube_type VARCHAR(50) NOT NULL,
    required_volume DECIMAL(5,2) NOT NULL, -- in mL
    processing_instructions TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Order Tests Junction Table
CREATE TABLE order_tests (
    order_test_id UUID PRIMARY KEY,
    order_id UUID REFERENCES blood_collection_orders(order_id),
    test_id UUID REFERENCES test_catalog(test_id),
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Specimen Collection Table
CREATE TABLE specimen_collections (
    collection_id UUID PRIMARY KEY,
    order_id UUID REFERENCES blood_collection_orders(order_id),
    collector_id UUID REFERENCES healthcare_providers(provider_id),
    collection_datetime TIMESTAMP NOT NULL,
    collection_site VARCHAR(100),
    number_of_attempts INTEGER,
    collection_method VARCHAR(50),
    collection_notes TEXT,
    patient_position VARCHAR(50),
    complications TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Specimen Labels Table
CREATE TABLE specimen_labels (
    label_id UUID PRIMARY KEY,
    collection_id UUID REFERENCES specimen_collections(collection_id),
    barcode VARCHAR(100) UNIQUE NOT NULL,
    tube_type VARCHAR(50) NOT NULL,
    print_datetime TIMESTAMP NOT NULL,
    printed_by UUID REFERENCES healthcare_providers(provider_id),
    reprint_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Specimen Tracking Table
CREATE TABLE specimen_tracking (
    tracking_id UUID PRIMARY KEY,
    specimen_label_id UUID REFERENCES specimen_labels(label_id),
    tracking_point VARCHAR(50) NOT NULL, -- (Collection/Transport/Lab Receipt)
    tracking_datetime TIMESTAMP NOT NULL,
    tracked_by UUID REFERENCES healthcare_providers(provider_id),
    temperature DECIMAL(4,1),
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Incident Reports Table
CREATE TABLE incident_reports (
    incident_id UUID PRIMARY KEY,
    collection_id UUID REFERENCES specimen_collections(collection_id),
    reported_by UUID REFERENCES healthcare_providers(provider_id),
    incident_datetime TIMESTAMP NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    immediate_action TEXT,
    status VARCHAR(30) NOT NULL, -- (Open/In Progress/Closed)
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_at TIMESTAMP,
    modified_by VARCHAR(50)
);

-- Audit Log Table
CREATE TABLE audit_log (
    audit_id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action_type VARCHAR(20) NOT NULL, -- (INSERT/UPDATE/DELETE)
    action_datetime TIMESTAMP NOT NULL,
    action_by VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45)
);

-- Create indexes for better query performance
CREATE INDEX idx_blood_collection_orders_patient ON blood_collection_orders(patient_id);
CREATE INDEX idx_specimen_collections_order ON specimen_collections(order_id);
CREATE INDEX idx_specimen_tracking_label ON specimen_tracking(specimen_label_id);
CREATE INDEX idx_order_tests_order ON order_tests(order_id);
CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
