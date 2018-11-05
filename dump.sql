CREATE TABLE background_question (
	idbackground_question INTEGER NOT NULL, 
	background_question VARCHAR(120), 
	experiment_idexperiment INTEGER, 
	PRIMARY KEY (idbackground_question)
);
CREATE TABLE experiment (
	idexperiment INTEGER NOT NULL, 
	name VARCHAR(120), 
	instruction VARCHAR(120), 
	directoryname VARCHAR(120), 
	language VARCHAR(120), 
	status VARCHAR(120), 
	randomization VARCHAR(120), 
	PRIMARY KEY (idexperiment)
);
CREATE TABLE trial_randomization (
	idtrial_randomization INTEGER NOT NULL, 
	page_idpage INTEGER, 
	randomized_idpage INTEGER, 
	answer_set_idanswer_set INTEGER, 
	experiment_idexperiment INTEGER, 
	PRIMARY KEY (idtrial_randomization)
);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(64), 
	email VARCHAR(120), 
	password_hash VARCHAR(128), 
	PRIMARY KEY (id)
);
INSERT INTO user VALUES(1,'timo',NULL,'pbkdf2:sha256:50000$sctKb5R4$688ff9fd63df4a0883b9eb003b6738c6b7baa2010e1cd503c678b43c881c07bf');
CREATE TABLE answer_set (
	idanswer_set INTEGER NOT NULL, 
	experiment_idexperiment INTEGER, 
	session VARCHAR(120), 
	agreement VARCHAR(120), 
	answer_counter INTEGER, 
	PRIMARY KEY (idanswer_set), 
	FOREIGN KEY(experiment_idexperiment) REFERENCES experiment (idexperiment)
);
CREATE TABLE background_question_option (
	idbackground_question_option INTEGER NOT NULL, 
	background_question_idbackground_question INTEGER, 
	option VARCHAR(120), 
	PRIMARY KEY (idbackground_question_option), 
	FOREIGN KEY(background_question_idbackground_question) REFERENCES background_question (idbackground_question)
);
CREATE TABLE page (
	idpage INTEGER NOT NULL, 
	experiment_idexperiment INTEGER, 
	type VARCHAR(120), 
	text VARCHAR(120), 
	media VARCHAR(120), 
	PRIMARY KEY (idpage), 
	FOREIGN KEY(experiment_idexperiment) REFERENCES experiment (idexperiment)
);
CREATE TABLE question (
	idquestion INTEGER NOT NULL, 
	experiment_idexperiment INTEGER, 
	question VARCHAR(120), 
	`left` VARCHAR(120), 
	`right` VARCHAR(120), 
	PRIMARY KEY (idquestion), 
	FOREIGN KEY(experiment_idexperiment) REFERENCES experiment (idexperiment)
);
CREATE TABLE answer (
	idanswer INTEGER NOT NULL, 
	question_idquestion INTEGER, 
	answer_set_idanswer_set INTEGER, 
	answer VARCHAR(120), 
	page_idpage INTEGER, 
	PRIMARY KEY (idanswer), 
	FOREIGN KEY(answer_set_idanswer_set) REFERENCES answer_set (idanswer_set), 
	FOREIGN KEY(page_idpage) REFERENCES page (idpage), 
	FOREIGN KEY(question_idquestion) REFERENCES question (idquestion)
);
CREATE TABLE background_question_answer (
	idbackground_question_answer INTEGER NOT NULL, 
	answer_set_idanswer_set INTEGER, 
	answer VARCHAR(120), 
	background_question_idbackground_question INTEGER, 
	PRIMARY KEY (idbackground_question_answer), 
	FOREIGN KEY(answer_set_idanswer_set) REFERENCES answer_set (idanswer_set), 
	FOREIGN KEY(background_question_idbackground_question) REFERENCES background_question (idbackground_question)
);
CREATE UNIQUE INDEX ix_experiment_directoryname ON experiment (directoryname);
CREATE INDEX ix_experiment_instruction ON experiment (instruction);
CREATE INDEX ix_experiment_name ON experiment (name);
CREATE UNIQUE INDEX ix_user_email ON user (email);
CREATE UNIQUE INDEX ix_user_username ON user (username);
CREATE INDEX ix_page_media ON page (media);
CREATE INDEX ix_page_text ON page (text);
CREATE INDEX ix_page_type ON page (type);

