#!/usr/bin/python

import os, sys, re
import shutil
import platform
import fileinput
from optparse import OptionParser
from xml.etree import ElementTree
from datetime import date
import urllib
import zipfile
import tarfile
import shutil
import pwd

version = '4.2'

class powertool:
	# fixme!
	def __init__(self, user):
		self.user = user
		self.home = os.getenv('HOME')
		self.conf = {}

	def setup_mutt(self, distrib, version, group):
		name = self.conf['name']
		# host = 'smtp.' + domain
		now = date.today()
		term = "cs%d%d" % (now.year % 100, (now.month + 1) / 2)

		if self.conf.has_key('email'):
			email = self.conf['email']
		else:
			email = self.name_to_mail(name)

		if self.conf.has_key('epass'):
			epass = self.conf['epass']
		else:
			epass = 'MW%s' % term

		domain = email.split('@')[1]

		maildir = 'Mail/Inbox/cur'
		if not os.path.exists(self.home + '/' + maildir):
			os.makedirs(self.home + '/' + maildir)

		for pkg in group:
			rc = '%s/.%src' % (self.home, pkg)

			if os.path.exists(rc):
				if not self.conf.has_key('email') and not self.conf.has_key('epass'):
					continue
				print 'updating %src ...' % pkg
			else:
				print 'generating %src ...' % pkg

			if pkg == 'msmtp':
				if os.path.exists(rc):
					for line in fileinput.input(rc, 1):
						#os.system('sed -i "s/user\s.*/user %s/" %s' % (email, rc))
						#os.system('sed -i "s/from\s.*/from %s/" %s' % (email, rc))
						s = line.split()
						if len(s) > 0 and (s[0] == 'user' or s[0] == 'from'):
							if self.conf.has_key('email'):
								print line.replace(s[1], email),
							else:
								print line,

						#os.system('sed -i "s/password\s.*/password %s/" %s' % (epass, rc))
						elif len(s) > 0 and (s[0] == 'password'):
							if self.conf.has_key('epass'):
								print line.replace(s[1], epass),
							else:
								print line,

						#os.system('sed -i "s/host\s.*/host smtp.%s/" %s' % (domain, rc))
						elif len(s) > 0 and (s[0] == 'host'):
							print line.replace(s[1], 'smtp.%s' % domain),

						else:
							print line,

					continue

				fd = open(rc, 'w+')
				fd.write('defaults\n\n')
				fd.write('account %s\n' % domain)
				fd.write('host smtp.%s\n' % domain)
				fd.write('user %s\n' % email)
				fd.write('from %s\n' % email)
				fd.write('password %s\n' % epass)
				fd.write('auth login\n\n')
				fd.write('account default: %s' % domain)
				fd.close()
			elif pkg == 'fetchmail':
				if os.path.exists(rc):
					for line in fileinput.input(rc, 1):
						#os.system('sed -i "s/user\s.*/user %s/" %s' % (email, rc))
						#os.system('sed -i "s/poll\s.*/poll pop.%s with protocol pop3/"' % domain)
						s = line.split()
						if len(s) > 0 and (s[0] == 'user'):
							if self.conf.has_key('email'):
								print line.replace(s[1], email),
							else:
								print line,

						elif len(s) > 0 and (s[0] == 'poll'):
							if self.conf.has_key('email'):
								print line.replace(s[1], 'pop.%s' % domain),
							else:
								print line,

						#os.system('sed -i "s/password\s.*/password %s/" %s' % (epass, rc))
						elif len(s) > 0 and (s[0] == 'password'):
							if self.conf.has_key('epass'):
								print line.replace(s[1], epass),
							else:
								print line,

						else:
							print line,

					continue

				fd = open(rc, 'w+')
				fd.write('set daemon 600\n')
				fd.write('poll pop.%s with protocol pop3\n' % domain)
				fd.write('uidl\n')
				fd.write('user "%s"\n' % email)
				fd.write('password "%s"\n' % epass)
				fd.write('keep\n')
				fd.write('mda "/usr/bin/procmail -d %T"\n')
				fd.close()
			elif pkg == 'procmail':
				if os.path.exists(rc):
					continue

				fd = open(rc, 'w+')
				fd.write('MAILDIR=$HOME/Mail\n')
				fd.write('DEFAULT=$MAILDIR/Inbox/\n')
				fd.close()
			elif pkg == 'mutt':
				if os.path.exists(rc):
					for line in fileinput.input(rc, 1):
						#os.system('sed -i "s/my_hdr\s\+From:.*/my_hdr From: %s/" %s' % (email, rc))
						#os.system('sed -i "s/my_hdr\s\+Reply-To:.*/my_hdr Reply-To: %s/" %s' % (email, rc))
						s = line.split()
						if len(s) > 0 and (s[0] == 'my_hdr'):
							if self.conf.has_key('email'):
								print line.replace(s[2], email),
							else:
								print line,
						else:
							print line,

					continue

				fd = open(rc, 'w+')
				# smtp setting
				fd.write('# smtp setting\n')
				fd.write('set sendmail = /usr/bin/msmtp\n')
				fd.write('# set use_from = yes\n')
				fd.write('# set envelope_from = yes\n')
				fd.write('\n')
				# general setting
				fd.write('# general setting\n')
				fd.write('my_hdr From: %s\n' % email)
				#fd.write('my_hdr Reply-To: %s\n' % mail)
				#fd.write('my_hdr Reply-To: \"%s\" <%s>\n' % (name, mail))
				fd.write('\n')

				fd_rc = open('app/mutt/muttrc.common')
				for line in fd_rc:
					fd.write(line)
				fd_rc.close()

				fd.close()

				# signature
				fd = open(self.home + '/Mail/signature', 'w+')
				fd.write('Regards,\n%s\n' % name)
				fd.close()
			else:
				print '%s not configured' % pkg
				continue

			os.chmod(rc, 0600)

	def name_to_mail(self, name):
		return name.lower().replace(' ', '.') + '@maxwit.com'

	def setup_git(self, distrib, version, group):
		fname = self.conf['name']
		if self.conf.has_key('email'):
			email = self.conf['email']
		else:
			email = self.name_to_mail(fname)

		# fixme
		#os.system('app/git/setup.sh "%s" "%s"' % (fname, email))

		rc = '%s/.gitconfig' % (self.home)
		fd_rc = open(rc, 'w+')
		fd_rc.write('[color]\n')
		fd_rc.write('\tui = auto\n')
		fd_rc.write('[user]\n')
		fd_rc.write('\tname = %s\n' % fname)
		fd_rc.write('\temail = %s\n' % email)
		fd_rc.write('[sendemail]\n')
		fd_rc.write('\tsmtpserver = /usr/bin/msmtp\n')
		fd_rc.write('[push]\n')
		fd_rc.write('\tdefault = matching')
		fd_rc.close()

	def setup_vim(self, distrib, version, group):
		dst = open(self.home + '/.vimrc', 'w+')
		src = open('app/vim/vimrc')
		for line in src:
			dst.write(line)
		src.close()
		dst.close()

	def setup_serial(self, distrib, version, group):
		dst = open(self.home + '/.kermrc', 'w+')
		src = open('app/kermit/kermrc')
		for line in src:
			dst.write(line)
		src.close()
		dst.close()

	def extract_file(self, file, path, type):
		print 'extract ' + file
		if type == 'tar':
			tfile = tarfile.open(file)
			for tarinfo in tfile:
				tfile.extract(tarinfo.name, path)
			tfile.close()
		elif type == 'zip':
			zfile = zipfile.ZipFile(file,'r')
			zfile.extractall(path)

	def setup_eclipse(self, distrib, version, curr_arch):
		path = '/maxwit/source'
		if not os.path.exists(path):
			os.mkdir(path)

		path = self.home + '/build/'
		if not os.path.exists(path):
			os.mkdir(path)

		file_name = ''
		url = ''
		if curr_arch == 'x86_64':
			file_name = 'eclipse_64.tar.gz'
			url = 'http://mirrors.ustc.edu.cn/eclipse/technology/epp/downloads/release/kepler/SR2/eclipse-jee-kepler-SR2-linux-gtk-x86_64.tar.gz'
		else:
			file_name = 'eclipse.tar.gz'
			url = 'http://mirrors.neusoft.edu.cn/eclipse/technology/epp/downloads/release/kepler/SR2/eclipse-jee-kepler-SR2-linux-gtk.tar.gz'

		if not os.path.exists('/maxwit/source/' + file_name):
			urllib.urlretrieve(url, '/maxwit/source/' + file_name)
		if os.path.exists(path + 'eclipse'):
			shutil.rmtree(path + 'eclipse')

		self.extract_file('/maxwit/source/' + file_name, path, 'tar')

		fd_rc = open('/tmp/eclipse.desktop', 'w+')
		fd_rc.write('[Desktop Entry]\n')
		fd_rc.write('Encoding=UTF-8\n')
		fd_rc.write('Name=EclipseJEE\n')
		fd_rc.write('Terminal=false\n')
		fd_rc.write('StartupNotify=true\n')
		fd_rc.write('Type=Application\n')
		fd_rc.write('Categories=Application;Development;\n')
		fd_rc.write('Comment=Eclipse Integrated Development Environment\n')
		fd_rc.write('Icon=' + path + 'eclipse/icon.xpm\n')
		fd_rc.write('Exec=env UBUNTU_MENUPROXY= ' + path + 'eclipse/eclipse\n')
		fd_rc.close()
		os.system('sudo cp /tmp/eclipse.desktop /usr/share/applications/')
		os.system('sudo chmod u+x /usr/share/applications/eclipse.desktop')

		if not os.path.exists('/maxwit/source/PyDev203.4.1.zip'):
			url = 'http://jaist.dl.sourceforge.net/project/pydev/pydev/PyDev%203.4.1/PyDev%203.4.1.zip'
			urllib.urlretrieve(url, '/maxwit/source/PyDev203.4.1.zip')
		self.extract_file('/maxwit/source/PyDev203.4.1.zip', path + 'eclipse', 'zip')

	def traverse(self, node, path):
		if not os.path.exists(path):
			print 'creating "%s"' % path
			os.mkdir(path)
		#else:
		#	print "skipping \"%s\"" % path
		lst = node.getchildren()
		for n in lst:
			self.traverse(n, path + '/' + n.attrib['name'])

	# population the target directory
	def populate(self):
		for fn in ['home.xml', 'maxwit.xml']:
			tree = ElementTree.parse('tree/'+fn)
			root = tree.getroot()

			top = root.attrib['name'].strip()
			if top[0] == '$':
				top = os.getenv(top[1:])
				if top == None:
					print '"%s" does NOT exists!' % top
					exit()
			elif top == '/maxwit':
				mounted = False
				fd_chk = open('/proc/mounts')
				for line in fd_chk:
					mount = line.split(' ')
					if mount[1] == top:
						mounted = True
						break
				fd_chk.close()

				if mounted == False:
					print '"%s" NOT mounted!' % top
					exit()

			if not os.access(top, 7):
				print 'Fail to access "' + top + '", permission denied!'
				exit()

			readme = top + '/readme'
			if not os.path.exists(readme):
				fd = open(readme, 'w+')
				fd.write('MaxWit PowerTool v%s\n' % version)
				fd.close()

			print 'Populating %s ...' % top
			self.traverse(root, top)
			print

	def get_user_info(self):
		for struct_pwd in pwd.getpwall():
			if struct_pwd.pw_name == self.user:
				full_name = struct_pwd.pw_gecos.split(',')[0].strip()
				return full_name

	def do_install(self, distrib, version, curr_arch, install_list):
		upgrade  = ''
		install  = ''
		tree = ElementTree.parse(r'app/apps.xml')
		root = tree.getroot()
		dist_list = root.getchildren()

		for dist_node in dist_list:
			if dist_node.attrib['name'] == distrib:
				upgrade = dist_node.attrib['upgrade']
				install = dist_node.attrib['install']

				if upgrade != '':
					#os.system('sudo ' + upgrade)
					print

				if install_list[0] == 'ALL' or 'eclipse' in install_list:
					self.setup_eclipse(distrib, version, curr_arch)

				release_list = dist_node.getchildren()
				for release in release_list:
					ver = release.attrib['version']
					if ver == 'all' or ver == version:
						self.distri_install(curr_arch, distrib, version, install, install_list, release.getchildren())
						if ver == version:
							return

	def distri_install(self, arch, distrib, version, install, install_list, release_list):
		for pkg in install_list:
			for app_node in release_list:
				if arch != app_node.get('arch', arch):
					continue

				members = re.split('\s+', app_node.text)
				if install_list[0] == 'ALL' or pkg in members:
					group = app_node.get('group')
					#attr_post = app_node.get('post')

					print 'Installing %s:\n  %s' % (group.upper(), app_node.text)
					os.system('sudo ' + install + ' ' +  app_node.text)

					#if attr_post != None:
					#	os.system('cd app/%s && ./%s' % (group, attr_post))
					config = getattr(self, 'setup_'+group, None)
					if config != None:
						print 'Configuring %s ...' % group
						config(distrib, version, members)

					print

	def config(self, key, val):
		self.conf[key] = val

	def setup(self, apps):
		distrib = platform.dist()[0].lower()
		version = platform.dist()[1].lower()
		arch = platform.processor()

		self.do_install(distrib, version, arch, apps);

if __name__ == '__main__':
	user = os.getenv('USER')
	if user == 'root':
		print 'cannot run as root!'
		exit()

	power = powertool(user)

	parser = OptionParser()
	parser.add_option('-m', '--email', dest='email',
					  help='E-mail Account')
	parser.add_option('-p', '--epass', dest='epass',
					  help='E-mail Password')
	parser.add_option('-v', '--version', dest='version',
					  default=False, action='store_true',
					  help='show PowerTool version and exit')

	(opts, args) = parser.parse_args()

	if opts.version:
		print '  PowerTool v%s (MaxWit Software, http://www.maxwit.com)' % version
		exit()

	if opts.email != None:
		power.config('email', opts.email)

	if opts.epass != None:
		power.config('epass', opts.epass)

	if len(args) != 0:
		apps  = args
	else:
		apps  = ['ALL']

	power.config('name', power.get_user_info())
	power.setup(apps)
	power.populate()
