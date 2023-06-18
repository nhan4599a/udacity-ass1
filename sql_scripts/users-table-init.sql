CREATE TABLE USERS (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password_hash CHAR(102) NULL,
    is_external_user BIT,
    [provider] SMALLINT
);