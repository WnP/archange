#!/usr/bin/python
# -*- coding: utf-8 -*-

###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###


import sqlite3
import urllib2, urllib
import tarfile, tempfile
import re
import random


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
			self.connect ()
		if cur:
			self.cur = ArchDB._con.cursor ()
		else:
			self.cur = ArchDB._cur

	def __del__(self):
		ArchDB._count -= 1
		if ArchDB._count == 0:
			self.disconnect ()

	# Se connecte à la base et ouvre un curseur
	def connect(self):
		if ArchDB._con is not None:
			return True
		try:
			ArchDB._con = sqlite3.connect (self._file)
			ArchDB._cur = ArchDB._con.cursor ()
			return True
		except sqlite3.Error, e:
			print "Erreur lors de la connexion à :", self._file, e.args[0]
			return False

	def disconnect (self):
		if ArchDB._con is None:
			return True
		try:
			ArchDB._con.close ()
			ArchDB._con = None
			self.connecte = False
			return True
		except:
			print "Erreur lors de la déconnexion."
			return False
		return False

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
				for i in range (0,len (args)):
					# utf-8, pas utf-8, là est la question...
					if isinstance (args[i], basestring ):
						args[i] = args[i].decode ('utf-8')
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


	# Charge les paramètres des sites et compile la regexp pour trouver les résultats
	def loadSites (self):
		# sites:
		#	clé: code du site
		#	0 id
		#	1 url
		#	2 slink
		#	3 regexp (compilée)
		#	4 method_post (0: non, !=0: oui)
		#	5 sparam
		#	6 params (ensemble des param/valeur)
		self.sites = {}
		req = "select id, code, url, slink, regexp, method_post, sparam from site"

		r_sites = self.db.getAll (req)
		if r_sites is not None:
			for r_site in r_sites:
				req = "select param_name, param_value from site_param where site_id = ?"
				r_params = self.db.getAll (req, [r_site[0]])
				params = {}
				if r_params is not None:
					for r_param in r_params:
						params[r_param[0]] = r_param[1]
					regexp_c = re.compile (r_site[4])
					self.sites[r_site[1]] = [ r_site[0], r_site[2],
							r_site[3], regexp_c,
							r_site[5], r_site[6], params]
			

	def getSite (self, code):
		try:
			ret = self.sites[code][0]
		except:
			ret = False
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
			if pages:
				replies = []
				for page in pages:
					self.setPage (site, query, page.replace (self.sites[site][1], ""))
					replies += [[page]]
				return replies
			else:
				return None
		except:
			return None


	def getPages (self, site, query):
		site_id = self.getSite (site)
		if not site_id:
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
				#print "Récupération de '", repo[1], "' depuis '", repo[2], "'"
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
					#print pkgname, "(version:", pkgver, "release:", pkgrel, ")"
					if self.getPkg (repo[0], pkgname, pkgver + '-' + pkgrel):
						continue
					pkg_id = self.addPkg (repo[0], pkgname, pkgver + '-' + pkgrel)
					file_info = file_tgz.extractfile(pkgfile)
					for path in file_info.readlines():
						#print path
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
		req = """select repo_name, pkg_name, version, path
		from repo_pkg_file where path like ? limit ?"""
		return self.db.getAll (req, ['%' + search + '%', max])


# Classe Reply: Gestion des réponses du bot
class Reply:

	def __init__(self):
		self.db = ArchDB ()
		self.loadGroups ()
		random.seed()

	def __del__(self):
		del self.db

	def loadGroups (self):
		# groupes:
		#	clé: id du groupe
		#	0: contenu du groupe
		#	1: règles regexp {id : contenu}
		#	2: réponses {id : contenu}
		# rules: { id : r_group_id }
		# replies: { id : r_group_id }

		self.groups = {}
		self.rules = {}
		self.replies = {}
		req = "select id, content from r_group"
		r_groups = self.db.getAll (req)
		if r_groups is None:
			return False
		for r_group in r_groups:
			self.groups[r_group[0]] = [r_group[1], {}, {}]
			req = "select id, content from rule where r_group_id = ?"
			r_rules = self.db.getAll (req, [r_group[0]])
			if r_rules is not None:
				for r_rule in r_rules:
					try:
						p = re.compile (r_rule[1], re.I)
					except:
						continue
					self.rules[r_rule[0]] = r_group[0]
					self.groups[r_group[0]][1][r_rule[0]] = p
			req = "select id, content from reply where r_group_id = ? "
			r_replies = self.db.getAll (req, [r_group[0]])
			if r_replies is not None:
				for r_reply in r_replies:
					self.replies[r_reply[0]] = r_group[0]
					self.groups[r_group[0]][2][r_reply[0]] = r_reply[1]

	
	def delGroup (self, group_id):
		self.db.setCommit (False);
		req = "delete from rule where r_group_id = ?"
		self.db.executeCmd (req, [group_id])
		req = "delete from reply where r_group_id = ?"
		self.db.executeCmd (req, [group_id])
		req = "delete from r_group where id = ?"
		self.db.executeCmd (req, [group_id])
		try:
			del self.groups[group_id]
		except:
			pass
		self.db.commit ();
		self.db.setCommit (True);

	def delReply (self, reply_id):
		req = "delete from reply where id = ?"
		self.db.executeCmd (req, [reply_id])
		try:
			group_id = self.replies[reply_id]
			del self.groups[group_id][2][reply_id]
			del self.replies[reply_id]
		except:
			pass

	def delRule (self, rule_id):
		req = "delete from rule where id = ?"
		self.db.executeCmd (req, [rule_id])
		try:
			group_id = self.rules[rule_id]
			del self.groups[group_id][1][rule_id]
			del self.rules[rule_id]
		except:
			pass


	def addGroup (self, content):
		req = "insert into r_group (content) values (?)"
		if self.db.executeCmd (req, [content]):
			req = "select max(id) from r_group"
			group_id = self.db.getOne (req)
			if group_id:
				self.groups[group_id] = [content, {}, {}]
				return True
		return False
	
	def addRule (self, group_id, content):
		try:
			self.groups[group_id]
			p = re.compile (content)
		except:
			return False
		req = "insert into rule (content, r_group_id) values (?, ?)"
		if self.db.executeCmd (req, [content, group_id]):
			req = "select max(id) from rule"
			rule_id = self.db.getOne (req)
			if rule_id:
				self.groups[group_id][1][rule_id] = p
				self.rules[rule_id] = group_id
				return True
		return False

	def addReply (self, group_id, content):
		try:
			self.groups[group_id]
		except:
			return False
		req = "insert into reply (content, r_group_id) values (?, ?)"
		if self.db.executeCmd (req, [content, group_id]):
			req = "select max(id) from reply"
			reply_id = self.db.getOne (req)
			if reply_id:
				self.groups[group_id][2][reply_id] = content
				self.replies[reply_id] = group_id
				return True
		return False

	def modifyGroup (self, group_id, content):
		req = "update r_group  set content = ? where id = ?"
		if self.db.executeCmd (req, [content, group_id]):
			self.groups[group_id][0] = content
			return True
		return False

	def listGroup (self):
		req = "select id, content from r_group"
		return self.db.getAll (req)

	def listRule (self):
		req = "select id, content, r_group_id from rule"
		return self.db.getAll (req)

	def listReply (self):
		req = "select id, content, r_group_id from reply"
		return self.db.getAll (req)

	def randomReply (self, str):
		for i, group in self.groups.items ():
			if len (group[2]) != 0:
				for j, rule in group[1].items ():
					if rule.findall (str):
						return group[2][group[2].keys ()[random.randint (0, len (group[2]) - 1)]]
		return False

