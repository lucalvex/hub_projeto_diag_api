INSERT INTO users_useraccount (
    username, 
    email, 
    cnpj, 
    cpf, 
    password, 
    is_active, 
    registration_date, 
    deactivation_date, 
    is_staff, 
    is_superuser
) VALUES 
(
    'joao_silva', 
    'joao.silva@exemplo.com', 
    '12345678000190', 
    '12345678901', 
    'pbkdf2_sha256$260000$abc123$def456ghi789jkl012mno345pqr678stu901vwx234yz', 
    TRUE, 
    '2023-01-15 10:30:00', 
    NULL, 
    FALSE, 
    FALSE
),
(
    'maria_souza', 
    'maria.souza@exemplo.com', 
    '98765432000181', 
    '98765432109', 
    'pbkdf2_sha256$260000$def456$ghi789jkl012mno345pqr678stu901vwx234yz567', 
    TRUE, 
    '2023-02-20 14:45:00', 
    NULL, 
    FALSE, 
    FALSE
),
(
    'carlos_lima', 
    'carlos.lima@exemplo.com', 
    '45678912000172', 
    '45678912304', 
    'pbkdf2_sha256$260000$ghi789$jkl012mno345pqr678stu901vwx234yz567abc', 
    FALSE, 
    '2023-03-10 09:15:00', 
    '2023-06-01 18:00:00', 
    FALSE, 
    FALSE
);

-- Inserindo um usuário administrador
INSERT INTO users_useraccount (
    username, 
    email, 
    cnpj, 
    cpf, 
    password, 
    is_active, 
    registration_date, 
    deactivation_date, 
    is_staff, 
    is_superuser
) VALUES 
(
    'admin', 
    'admin@exemplo.com', 
    '11111111000101', 
    '11111111111', 
    'pbkdf2_sha256$260000$xyz789$abc123def456ghi789jkl012mno345pqr678stu901', 
    TRUE, 
    '2023-01-01 00:00:00', 
    NULL, 
    TRUE, 
    TRUE
);

-- Inserindo um usuário da equipe (staff)
INSERT INTO users_useraccount (
    username, 
    email, 
    cnpj, 
    cpf, 
    password, 
    is_active, 
    registration_date, 
    deactivation_date, 
    is_staff, 
    is_superuser
) VALUES 
(
    'suporte', 
    'suporte@exemplo.com', 
    '22222222000102', 
    '22222222222', 
    'pbkdf2_sha256$260000$mno345$pqr678stu901vwx234yz567abc123def456ghi789', 
    TRUE, 
    '2023-01-05 08:00:00', 
    NULL, 
    TRUE, 
    FALSE
);