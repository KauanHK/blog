INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    ('other', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    ('a', 'scrypt:32768:8:1$VUK48FpLXM3E6aeW$cca282e758535439f0f9b41a2a41ee5983b325304fc154d7904dd6dea14106937201c2d551f8860915d2db3499213acb3e731033425502a64580afb971a55a19'),
    ('b', 'scrypt:32768:8:1$p9CM4aM6qcmey3VT$9f9f44f6f98f0a465b9a912c116fcfa9e84c1d9dd69d3e0e5f0da8135863a94026ce1f66c3fc048f2168b23b7300bd2397eb2bc400f33ecf4dfad54a9ce18e36'),
    ('c', 'scrypt:32768:8:1$fMgrEFJCLpPJya50$6a76a0b6ceb133d301fbab50faa892901a4a90f8ccb74807379a0e8ae1c5654ea6bdfc208d2765e4d82f4870726898e233077a454c456c6c9ab06e29d2674191'),
    ('d', 'scrypt:32768:8:1$4QR7q40Q2KRmts0q$ab00617c149b013ed522c04fb0e64e414550c235acccc3b74df547b5fd6adb040d09ca9eedb48c70c7e55369897b054f2e61cbc42cd25aff83636b7454b4b718');
-- As senhas são iguais ao username:
-- Senha do usuário 'a' é 'a'
-- Senha do usupario 'b' é 'b'

INSERT INTO post (title, body, author_id, created)
VALUES
    ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');