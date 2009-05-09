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

INSERT INTO "site" VALUES(1,'wiki_qsearch','http://wiki.archlinux.fr','/lib/exe/ajax.php',0,'q','href="(.*?)\?');
INSERT INTO "site" VALUES(2,'wiki_search','http://wiki.archlinux.fr','/',0,'id','href="(.*?)\?.*wikilink1');
INSERT INTO "site" VALUES(3,'wiki_org','http://wiki.archlinux.org/index.php','/Special:Search',0,'search','<li>.*?href="/index.php(.*?)".*search');
INSERT INTO "site" VALUES(4,'bugs_org','http://bugs.archlinux.org','/',0,'string','task_id.*href="http://bugs.archlinux.org(/task/.*?)\?');
INSERT INTO "site" VALUES(5,'aur','http://aur.archlinux.org','/rpc.php',0,'arg','"Name":"(.*?)","Version":"(.*?)"');
INSERT INTO "site" VALUES(6,'scroogle','','http://www.scroogle.org/cgi-bin/nbbw.cgi',1,'Gw','[0-9].*Href="(.*?)"');

INSERT INTO "site_param" VALUES(1,1,'call','qsearch');
INSERT INTO "site_param" VALUES(2,2,'do','search');
INSERT INTO "site_param" VALUES(3,3,'fulltext','Search');
INSERT INTO "site_param" VALUES(4,4,'projet','0');
INSERT INTO "site_param" VALUES(5,4,'search_for_all','1');
INSERT INTO "site_param" VALUES(6,5,'type','search');
INSERT INTO "site_param" VALUES(8,6,'l','fr');
INSERT INTO "site_param" VALUES(9,6,'n','2');


/* Tables pour la gestion des reponses du bot */
CREATE TABLE r_group (id integer primary key autoincrement,  content text);
CREATE TABLE rule (id integer primary key autoincrement, content text, r_group_id integer);
CREATE TABLE reply (id integer primary key autoincrement,  content text, r_group_id integer);


