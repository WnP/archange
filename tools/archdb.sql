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
CREATE INDEX result_uniq ON result (site_id, query_id, page_id);

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
CREATE TABLE reply_regexp (id integer primary key autoincrement, regexp text);
CREATE TABLE reply (id integer primary key autoincrement, reply_regexp_id integer, content text);



