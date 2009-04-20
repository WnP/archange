/* Tables pour la gestion des dépôt/paquets/fichiers */
CREATE TABLE repo (id integer primary key autoincrement, name text, url text);
CREATE TABLE pkg (id integer primary key autoincrement, repo_id integer, name text, version text, desc text);
CREATE TABLE file (id integer primary key autoincrement, pkg_id integer, path text);
CREATE INDEX file_path ON file (path);
CREATE VIEW repo_pkg_file as 
  SELECT r.name as repo_name, p.name as pkg_name, p.version, f.path
    FROM file f join pkg p on (p.id = f.pkg_id)
	            join repo r on (r.id = p.repo_id)
;

insert into repo (name, url) values ('core', 'http://mir.archlinux.fr/core/os/i686');
insert into repo (name, url) values ('extra', 'http://mir.archlinux.fr/extra/os/i686');
insert into repo (name, url) values ('community', 'http://mir.archlinux.fr/community/os/i686');
insert into repo (name, url) values ('archlinuxfr', 'http://repo.archlinux.fr/i686');


/* Tables pour la gestion des recherches sur le web */
CREATE TABLE site (id integer primary key autoincrement, code text,  url text, slink text, method_post integer, sparam text, regexp text);
CREATE TABLE site_param (id integer primary key autoincrement, site_id integer, param_name text, param_value text);

CREATE TABLE query (id integer primary key autoincrement, content text);
CREATE TABLE page (id integer primary key autoincrement, url text);
CREATE TABLE result (id integer primary key autoincrement, site_id integer, query_id integer, page_id integer );

insert into site (code, url, slink, method_post, sparam, regexp) values ('wiki_qsearch', 'http://wiki.archlinux.fr', '/lib/exe/ajax.php', 0, 'q', 'href="(.*?)\?');
insert into site_param (site_id, param_name, param_value) values (1, 'call', 'qsearch');

insert into site (code, url, slink, method_post, sparam, regexp) values ('wiki_search', 'http://wiki.archlinux.fr', '/', 0, 'id', 'href="(.*?)\?.*wikilink1');
insert into site_param (site_id, param_name, param_value) values (2, 'do', 'search');

insert into site (code, url, slink, method_post, sparam, regexp) values ('wiki_org', 'http://wiki.archlinux.org/index.php', '/Special:Search', 0, 'search', '<li>.*?href="(.*?)".*search');
insert into site_param (site_id, param_name, param_value) values (3, 'fulltext', 'Search');

insert into site (code, url, slink, method_post, sparam, regexp) values ('bugs_org', 'http://bugs.archlinux.org', '/', 0, 'string', 'task_id.*href="(http://bugs.archlinux.org/task/.*?)\?');
insert into site_param (site_id, param_name, param_value) values (4, 'projet', '0');
insert into site_param (site_id, param_name, param_value) values (4, 'search_for_all', '1');


/* Tables pour la gestion des reponses du bot */
CREATE TABLE r_group (id integer primary key autoincrement,  content text);
CREATE TABLE rule (id integer primary key autoincrement, content text, r_group_id integer);
CREATE TABLE reply (id integer primary key autoincrement,  content text, r_group_id integer);




INSERT INTO "r_group" VALUES(1,'arch_ange');
INSERT INTO "r_group" VALUES(2,'salutation');
INSERT INTO "r_group" VALUES(3,'bye');


INSERT INTO "rule" VALUES (1, 'arch_ange', 1);
INSERT INTO "rule" VALUES (3, '^salut$', 2);
INSERT INTO "rule" VALUES (5, '^bonsoir$', 2);
INSERT INTO "rule" VALUES (6, '^bye$', 3);
INSERT INTO "rule" VALUES (7, '^plop$', 2);
INSERT INTO "rule" VALUES (8, '^salut tlm$', 2);
INSERT INTO "rule" VALUES (9, '^bonjour$', 2);

INSERT INTO "reply" VALUES (1, 'oui?', 1);
INSERT INTO "reply" VALUES (2, 'compilation en cours...', 1);
INSERT INTO "reply" VALUES (3, 'occupé!', 1);
INSERT INTO "reply" VALUES (4, 'on a sonné à la porte?', 1);
INSERT INTO "reply" VALUES (5, 'je peux pas parler au étrangers.', 1);
INSERT INTO "reply" VALUES (7, 'salut %n', 2);
INSERT INTO "reply" VALUES (8, 'Bye %n', 5);
INSERT INTO "reply" VALUES (11, 'a+ %n', 3);
INSERT INTO "reply" VALUES (12, 'plop %n', 2);
INSERT INTO "reply" VALUES (13, 'déjà de retour?', 2);
INSERT INTO "reply" VALUES (14, '%n \o/', 2);
INSERT INTO "reply" VALUES (15, 'hmmm, et un de plus...', 2);
INSERT INTO "reply" VALUES (16, 'Bienvenue, jeune padawan', 2);
INSERT INTO "reply" VALUES (17, 'Archbot, relou en vue', 1);
INSERT INTO "reply" VALUES (18, '%n, oui, tu disais?', 1);
INSERT INTO "reply" VALUES (19, '/quit est la réponse', 1);
INSERT INTO "reply" VALUES (20, 'il faut appeler les renseignements', 1);
INSERT INTO "reply" VALUES (21, 'bon, apparemment, pas de sieste pour aujourd''hui...', 1);
INSERT INTO "reply" VALUES (22, '42', 1);
INSERT INTO "reply" VALUES (23, 'qui commence par a, finit par e et s''en fout?', 1);
INSERT INTO "reply" VALUES (24, 'je me sens fatigué là', 1);
INSERT INTO "reply" VALUES (25, 'tiens, vais me faire un footing', 1);
INSERT INTO "reply" VALUES (26, 'yaourt, ça donne des vitamines', 1);
INSERT INTO "reply" VALUES (27, 'KILL DASH NINE', 1);
INSERT INTO "reply" VALUES (28, 'Tu ferais mieux d’écrire en bépo', 1);

