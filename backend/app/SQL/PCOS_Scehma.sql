-- ============================================
-- AI-Assisted PCOS Risk Assessment System
-- PostgreSQL Schema
-- ============================================

-- =====================
-- USERS
-- =====================

CREATE TABLE users (
    user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,

    email VARCHAR(255) UNIQUE NOT NULL,

    specialization VARCHAR(50) NOT NULL,
    hospital VARCHAR(100),
    clinic_address VARCHAR(150),

    license_number VARCHAR(50) UNIQUE NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE DEFAULT CURRENT_DATE,

    CONSTRAINT chk_specialization
    CHECK (
        specialization IN (
            'Gynecologist',
            'Endocrinologist'
        )
    )
);



-- =====================
-- PATIENTS
-- =====================

CREATE TABLE patients (

    patient_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    doctor_id INT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,

    email VARCHAR(255) UNIQUE,

    date_of_birth DATE NOT NULL,

    height_cm DECIMAL(5,2) NOT NULL,

    created_at DATE DEFAULT CURRENT_DATE,

    CONSTRAINT chk_height
    CHECK (
        height_cm BETWEEN 80 AND 250
    )

);



-- =====================
-- ASSESSMENTS
-- =====================

CREATE TABLE assessments (

    assessment_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    patient_id INT NOT NULL
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    assessment_date DATE DEFAULT CURRENT_DATE,

    weight_kg DECIMAL(5,2) NOT NULL,

    cycle_regular BOOLEAN NOT NULL,

    cycle_length INT NOT NULL,

    fsh_miu_ml DECIMAL(6,2) NOT NULL,

    lh_miu_ml DECIMAL(6,2) NOT NULL,

    amh_ng_ml DECIMAL(6,2),

    fsh_lh_ratio DECIMAL(6,2),

    weight_gain BOOLEAN NOT NULL,

    hair_growth BOOLEAN NOT NULL,

    skin_darkening BOOLEAN NOT NULL,

    fast_food BOOLEAN NOT NULL,

    regular_exercise BOOLEAN NOT NULL,

    follicle_left INT NOT NULL,

    follicle_right INT NOT NULL,

    CONSTRAINT chk_weight
        CHECK (weight_kg BETWEEN 20 AND 300),

    CONSTRAINT chk_cycle_length
        CHECK (cycle_length BETWEEN 15 AND 120),

    CONSTRAINT chk_fsh
        CHECK (fsh_miu_ml BETWEEN 0 AND 200),

    CONSTRAINT chk_lh
        CHECK (lh_miu_ml BETWEEN 0 AND 200),

    CONSTRAINT chk_amh
        CHECK (
            amh_ng_ml IS NULL
            OR amh_ng_ml BETWEEN 0 AND 50
        ),

    CONSTRAINT chk_ratio
        CHECK (
            fsh_lh_ratio IS NULL
            OR fsh_lh_ratio BETWEEN 0 AND 20
        ),

    CONSTRAINT chk_follicle_left
        CHECK (follicle_left BETWEEN 0 AND 50),

    CONSTRAINT chk_follicle_right
        CHECK (follicle_right BETWEEN 0 AND 50)

);



-- =====================
-- ASSESSMENT RESULTS
-- =====================

CREATE TABLE assessment_results (

    result_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assessment_id INT NOT NULL UNIQUE
        REFERENCES assessments(assessment_id)
        ON DELETE CASCADE,

    prediction_probability DECIMAL(5,4) NOT NULL,

    prediction_class VARCHAR(20) NOT NULL,

    doctor_notes TEXT,

    CONSTRAINT chk_prediction_probability
        CHECK (
            prediction_probability BETWEEN 0 AND 1
        ),

    CONSTRAINT chk_prediction_class
        CHECK (
            prediction_class IN (
                'High Risk',
                'Low Risk',
				'Medium Risk'
            )
        )

);