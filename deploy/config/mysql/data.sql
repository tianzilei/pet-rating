
/* password:password */
INSERT INTO user VALUES(1,'admin',NULL,'pbkdf2:sha256:50000$6Cc6Mjmo$3fe413a88db1bacfc4d617f7c1547bd1ea4cbd6c5d675a58e78332201f6befc6');

/* password:password */
INSERT INTO user VALUES(2,'editor',NULL,'pbkdf2:sha256:50000$Rq2WwVVi$12335e8d02fa3f25ffd11ba9f02fd1db7ca2964c5eaa13ca179a02ee3f19a656');

INSERT INTO research_group(id, name, tag, description) VALUES(1, 'Human Emotion Systems', 'emotion', 'Welcome to the Human Emotion Systems -laboratory`s Onni-net laboratory! The experiments that are currently underway are listed below - you can participate for as many experiments you want.');
INSERT INTO research_group(id, name, tag, description) VALUES(2, 'Turku Eye-tracking', 'eyelabs', 'Welcome to the Turku Eyelabs -laboratory`s Onni-net laboratory! The experiments that are currently underway are listed below - you can participate for as many experiments you want.');

INSERT INTO user_in_group VALUES (1,1, 'admin');
INSERT INTO user_in_group VALUES (2,1, 'editor');

