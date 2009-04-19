#!/usr/bin/python
# -*- coding: utf-8 -*-


import sqlite3
import tarfile, tempfile, urllib
import re, random

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

	def setCommit (val=True):
		ArchDB._commit = val

	# Committe les modifications
	def commit():
		if not ArchDB._con is None:
			ArchDB._con.commit ()

	commit = staticmethod (commit)

	# Execute une requête
	def execute(self, req, args, commit=False):
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

def getNext (self):
	id = None
	ret = self.db_all.getNext ()
	if ret is None:
		return False
	else:
		(self.id,) = ret
	self.exid = None
	return self.get()


# Classe WebQuery: Gestion des recherches sur le web
class WebQuery

	def __init__(self):
		self.db = ArchDB ()
		self.loadSites ()
	
	def __del__(self):
		del self.db

	def _req (self, table, mode='select'):
		arg = {'site': ['site', 'url'],
				'query': ['query', 'query'],
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
		self.sites = {}
		req = "select id, url, slink, regexp from site"
		results = self.db.getAll (req)
		for result in results:
			sites[result[1]] = [ result[2], result[2] ]

	def getPages (self, site, query):
		site_id = self._get ('site', site)
		if site_id = None:
			return None
		query_id = self._get ('query', query)
		if query_id = None:
			return self.searchPages (site, self._set ('query', query)
		req = """select url 
		from result	join page on (result.page_id = page.id)
		where site_id = ? and query_id = ?"""
		pages = self.db.getAll (req, [site_id, query_id])
		if not pages:
			return self.searchPages (site, query)
		else:
			return pages

	def setPage (self, site, query, page):
		site_id = self._set ('site', site)
		query_id = self._set ('query', query)
		page_id = self._set ('page', page)
		req = """insert into result (site_id, query_id, page_id)
		values (?, ?, ?)"""
		return self.db.executeCmd (req, [site_id, query_id, page_id])

	def getResult (self, site=False, query=False, page=False):
		if site:
			site_id = self._set ('site', site)
		if query:
			query_id = self._set ('query', query)
		if page:
			page_id = self._set ('page', page)
		req = "select id from result where true"
		args = []
		if site:
			req += " and site_id = ? "
			args += [site_id]
		if query:
			req += " and query_id = ? "
			args += [query_id]
		if page:
			req += " and page_id = ? "
			args += [page_id]

		return self.db.getAll (req, args)

	def delResult (self, site=False, query=False, page=false):
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


			
