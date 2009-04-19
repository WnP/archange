#!/usr/bin/python
# -*- coding: utf-8 -*-


import sqlite3
import urllib2, urllib
import tarfile, tempfile
import re
#import random


# Classe ArchDB: Gestion du fichier de données
class ArchDB:
	_count = 0				# Nombre de connection
	_con = None				# Connection à la base sqlite
	_cur = None				# Curseur 
	_commit = True			# Commiter les changement à chaque requête
	_file = "archdb.sqlite"	# base sqlite

	def __init__(self, cur=False):
		ArchDB._count += 1
		if ArchDB._con is None:
			self._connect ()
		if cur:
			self.cur = ArchDB._con.cursor ()
		else:
			self.cur = ArchDB._cur

	def __del__(self):
		ArchDB._count -= 1
		if ArchDB._count == 0:
			ArchDB._con.close ()
		ArchDB._con = None

	# Se connecte à la base et ouvre un curseur
	def _connect(self):
		try:
			ArchDB._con = sqlite3.connect (self._file)
			ArchDB._cur = ArchDB._con.cursor ()
		except sqlite3.Error, e:
			print "Erreur lors de la connexion à :", self._file, e.args[0]
			exit (1)

	def setCommit (self, val=True):
		ArchDB._commit = val

	# Committe les modifications
	def commit():
		if not ArchDB._con is None:
			ArchDB._con.commit ()

	commit = staticmethod (commit)

	# Execute une requête
	def execute(self, req, args, commit=False):
		#print req, args, commit, ArchDB._commit
		try:
			if not args is None:
				self.cur.execute (req, tuple (args))
			else:
				self.cur.execute (req)
			if commit and self._commit:
				self.commit ()
			return True
		except sqlite3.Error, e:
			print "Erreur lors de l'éxecution de: ", req
			print "Message: ", e.args[0]
			return False

	# Execute une requête
	def executeCmd (self, req, args, commit=True):
		return self.execute (req, args, commit)

	# Execute une requête et retourne le premier résultat
	def getOne(self, req, args=None):
		if self.execute (req, args, False):
			row = self.cur.fetchone()
			if row:
				return row[0]
		return None

	# Execute une requête et retourne la première ligne du résultat
	def getFirst(self, req, args=None):
		self.execute (req, args, False)
		return self.cur.fetchone()
	

	# Retourne le résultat suivant
	def getNext(self):
		return self.cur.fetchone()

	# Retourne tous les résultats 
	def getAll(self, req, args=None):
		self.execute (req, args, False)
		return self.cur.fetchall()


# Classe WebQuery: Gestion des recherches sur le web
class WebQuery:

	def __init__(self):
		self.db = ArchDB ()
		self.loadSites ()
	
	def __del__(self):
		del self.db

	def _req (self, table, mode='select'):
		arg = {'site': ['site', 'code'],
				'query': ['query', 'content'],
				'page': ['page', 'url']}[table]
		req = {'select': "select id from " + arg[0] + " where " + arg[1] + " = ?",
				'insert': "insert into " + arg[0] + " (" + arg[1] + ") values (?)",
				'delete': "delete from " + arg[0] + " where id = ?"}[mode]
		return req

	def _get (self, table, arg):
		return self.db.getOne (self._req (table, 'select'), [arg])

	def _set (self, table, arg):
		id = self._get (table, arg)
		if id:
			return id
		else:
			ret = self.db.executeCmd (self._req(table, 'insert'), [arg])
			if ret:
				return self._get (table, arg)
		return None

	def _del (self, table, arg):
		return self.db.executeCmd (self._req(table, 'delete'), [arg])


	def loadSites (self):
		# sites:
		#	0 id
		#	1 url
		#	2 slink
		#	3 regexp (compilée)
		#	4 method_post (0: non, !=0: oui)
		#	5 sparam
		#	6 params (ensemble des param/valeur)
		self.sites = {}
		req = "select id, code, url, slink, regexp, method_post, sparam from site"

		try:
			r_sites = self.db.getAll (req)
			for r_site in r_sites:
				req = "select param_name, param_value from site_param where site_id = ?"
				r_params = self.db.getAll (req, [r_site[0]])
				params = {}
				for r_param in r_params:
					params[r_param[0]] = r_param[1]
				regexp_c = re.compile (r_site[4])
				self.sites[r_site[1]] = [ r_site[0], r_site[2],
						r_site[3], regexp_c,
						r_site[5], r_site[6], params]
		except:
			None
			

	def getSite (self, code):
		try:
			ret = self.sites[code][0]
		except:
			ret = None
		return ret

	def setPage (self, site, query, page):
		site_id = self.getSite (site)
		query_id = self._set ('query', query)
		page_id = self._set ('page', page)
		req = """insert into result (site_id, query_id, page_id)
		values (?, ?, ?)"""
		return self.db.executeCmd (req, [site_id, query_id, page_id])

	def searchPages (self, site, query):
		try:
			site_id = self.sites[site][0]
			url_base = self.sites[site][1]
			url_search = self.sites[site][2]
			p_search = self.sites[site][3]
			params = self.sites[site][6]
			params[self.sites[site][5]] =  query
			vars = urllib.urlencode (params)
			if self.sites[site][4] != 0:
				fd = urllib2.urlopen (url_base + url_search, vars)
			else:
				fd = urllib2.urlopen (url_base + url_search + '?' + vars)
			#print url_base + url_search + '?' + vars
			if fd is None:
				return None
			pages = p_search.findall (fd.read())
			fd.close ()
			for page in pages:
				self.setPage (site, query, page)
			return pages
		except:
			return None


	def getPages (self, site, query):
		site_id = self.getSite (site)
		if site_id is None:
			return None
		query_id = self._get ('query', query)
		if query_id is None:
			return self.searchPages (site, query)
		req = """select url 
		from result	join page on (result.page_id = page.id)
		where site_id = ? and query_id = ?"""
		pages = self.db.getAll (req, [site_id, query_id])
		if not pages:
			return self.searchPages (site, query)
		else:
			return pages

	def getResult (self, site=False, query=False, page=False):
		site_id = query_id = page_id = False
		if site:
			site_id = self.getSite (site)
		if query:
			query_id = self._get ('query', query)
		if page:
			page_id = self._get ('page', page)
		req = "select id from result where true"
		args = []
		if site_id:
			req += " and site_id = ? "
			args += [site_id]
		if query_id:
			req += " and query_id = ? "
			args += [query_id]
		if page_id:
			req += " and page_id = ? "
			args += [page_id]

		return self.db.getAll (req, args)

	def delResult (self, site=False, query=False, page=False):
		results = self.getResuls (site, query, page)
		self.db.setCommit (False)
		for result in results:
			self._del ('result', result[0])
		self.db.commit ()
		req = "select p.id from page p left join result r on p.id = r.page_id where r.id is null;"
		results = self.db.getAll (req)
		for result in results:
			self._del ('page', result[0])
		req = "select s.id from site s left join result r on s.id = r.site_id where r.id is null;"
		results = self.db.getAll (req)
		for result in results:
			self._del ('site', result[0])
		req = "select p.id from query q left join result r on q.id = r.query_id where r.id is null;"
		results = self.db.getAll (req)
		for result in results:
			self._del ('query', result[0])
		self.db.commit ()
		self.db.setCommit (True)

class ArchPackage:
	def __init__(self):
		self.db = ArchDB ()
	
	def __del__(self):
		del self.db

	def getPkg (self, repo_id, pkg, version=None):
		req = "select id from pkg where repo_id = ? and name = ?"
		args = [repo_id, pkg]
		if version is not None:
			req += " and version = ?"
			args += [version]
		pkg_id = self.db.getOne (req, args)
		if pkg_id is not None:
			return pkg_id
		else:
			return False
		

	def delPkg (self, repo_id, pkg, version=None):
		pkg_id = self.getPkg (repo_id, pkg, version)
		if pkg_id:
			req = "delete from file where pkg_id = ?"
			self.db.executeCmd (req, [pkg_id])
			req = "delete from pkg where id = ?"
			self.db.executeCmd (req, [pkg_id])
		return True

	def addPkg (self, repo_id, pkg, version):
		pkg_id =  self.getPkg (repo_id, pkg, version)
		if pkg_id:
			return pkg_id
		self.delPkg (repo_id, pkg)
		req = "insert into pkg (repo_id, name, version) values (?, ?, ?)"
		if self.db.executeCmd (req, [repo_id, pkg, version]):
			return self.getPkg (repo_id, pkg, version)
		else:
			return False


	def addFile (self, pkg_id, path):
		req = "insert into file (pkg_id, path) values (?, ?)"
		return self.db.executeCmd (req, [pkg_id, path])
	
	
	def sync(self):
		try:
			self.db.setCommit (False)
			req = "select id, name, url from repo"
			repos = self.db.getAll (req)
			for repo in repos:
				print "Récupération de '", repo[1], "' depuis '", repo[2], "'"
				tmp_file = tempfile.NamedTemporaryFile()
				urllib.urlretrieve (repo[2] + '/' + repo[1] + '.files.tar.gz', tmp_file.name)
				file_tgz = tarfile.open (tmp_file.name, "r")
				if not file_tgz:
					continue
				for pkgfile in file_tgz.getnames():
					if pkgfile[-5:] != 'files':
						continue
					str = pkgfile[:pkgfile.rfind ('/')]
					pkgrel_index = pkgfile.rfind ('-')
					pkgrel = str[pkgrel_index+1:]
					str = str[:pkgrel_index]
					pkgver_index = str.rfind ('-')
					pkgver = str[pkgver_index+1:]
					pkgname = str[:pkgver_index]
					print pkgname, "(version:", pkgver, "release:", pkgrel, ")"
					if self.getPkg (repo[0], pkgname, pkgver + '-' + pkgrel):
						continue
					pkg_id = self.addPkg (repo[0], pkgname, pkgver + '-' + pkgrel)
					file_info = file_tgz.extractfile(pkgfile)
					for path in file_info.readlines():
						print path
						if path[-1] == '\n':
							self.addFile (pkg_id, path[:-1])
						else:
							self.addFile (pkg_id, path)
				file_tgz.close()
				tmp_file.close()
			self.db.commit ()
			self.db.setCommit (True)


		except:
			None

	def searchPkg (self, search, max=5):
		req = """select r.name, p.name, p.version 
		from repo r join pkg p on (r.id = p.repo_id)
		where p.name like ? limit ?"""
		return self.db.getAll (req, ['%' + search + '%', max])

	def searchFile (self, search, max=5):
		req = """select repo_name, pkg_name, path
		from repo_pkg_file where path like ? limit ?"""
		return self.db.getAll (req, ['%' + search + '%', max])


