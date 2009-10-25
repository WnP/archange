CREATE TABLE repo (name text, url text);
CREATE TABLE pkg (repo_id integer, name text, version text, release text, desc text);
CREATE TABLE file (pkg_id integer, path text);
CREATE INDEX file_path ON file (path);
CREATE VIEW repo_pkg_file as 
  SELECT r.name as repo_name, p.name as pkg_name, 
  		 p.version as version, p.release as release, f.path as path
    FROM file f join pkg p on (p.rowid = f.pkg_id)
	            join repo r on (r.rowid = p.repo_id)
;

insert into repo (name, url) values ('core', 'http://mir.archlinux.fr/core/os/i686');
insert into repo (name, url) values ('extra', 'http://mir.archlinux.fr/extra/os/i686');
insert into repo (name, url) values ('community', 'http://mir.archlinux.fr/community/os/i686');
insert into repo (name, url) values ('archlinuxfr', 'http://repo.archlinux.fr/i686');



