-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 00_create_database.sql
-- Description: Create development and testing databases with UTF-8
-- =====================================================================

CREATE DATABASE IF NOT EXISTS crms_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS crms_test_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crms_db;
