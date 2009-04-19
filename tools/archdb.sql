/* Tables pour la gestion des dépôt/paquets/fichiers */
CREATE TABLE repo (id integer primary key autoincrement, name text, url text);
CREATE TABLE pkg (id integer primary key autoincrement, repo_id integer, name text, version text, desc text);
CREATE TABLE file (id integer primary key autoincrement, pkg_id integer, path text);


/* Tables pour la gestion des recherches sur le web */
CREATE TABLE query (id integer primary key autoincrement, content text);
CREATE TABLE page (id integer primary key autoincrement, url text);
CREATE TABLE site (id integer primary key autoincrement, url text unique, slink text, regexp text);
CREATE TABLE result (id integer primary key autoincrement, site_id integer, query_id integer, page_id integer );
CREATE INDEX result_uniq ON result (site_id, query_id, page_id);

/* Tables pour la gestion des reponses du bot */
CREATE TABLE reply_regexp (id integer primary key autoincrement, regexp text);
CREATE TABLE reply (id integer primary key autoincrement, reply_regexp_id integer, content text);
