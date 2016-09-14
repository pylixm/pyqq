#-*-coding:utf-8-*-

import socket
import time
import hashlib
import re

import os
import random

from tea import encrypt,decrypt
from binascii import b2a_hex,a2b_hex
from PIL import Image


ip_adress0 = "211.136.236.84"
ip_adress1 = "211.136.236.85"
ip_adress2 = "211.136.236.86"
ip_adress3 = "211.136.236.83"


def bigendian2hex(a):
	c = ""
	b = b2a_hex(a.encode('utf16'))[4:]
	n = len(b)
	for i in xrange(0,n+1,4):
		c+=b[i+2:i+4]
		c+=b[i:i+2]
	return c

class QQ(object):
	def __init__(self,qq_num,paw):
		self.qq_num = hex(qq_num)[2:]
		self.paw = paw
		

	
	def login(self):
		print 'Logining...'
		self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.s.connect((ip_adress3,14000))

		m = hashlib.md5()
		m.update(self.paw)
		paw_md5 = m.hexdigest()
		self.paw_a = "00090001000000003434413741423843414235383746463210{}00".format(paw_md5)
		
		pac_get_key = '020033060800491f27{}0034344137414238434142353837464632010100105643514a4a385739364b3645455a445003'.format(self.qq_num)
		
		self.s.send(a2b_hex(pac_get_key))
		key_0 = self.s.recv(2048)
		key_1 = b2a_hex(key_0)[28:60]
		print key_1
		self.key = a2b_hex(key_1)


		paw_tea = encrypt(a2b_hex(self.paw_a),self.key)

		paw_tea = b2a_hex(paw_tea)
		pac_login_a = "020047060800500002{0}00{1}03".format(self.qq_num,paw_tea)
		print pac_login_a
		pac_login_b = a2b_hex(pac_login_a)
		self.s.send(pac_login_b)

		re_login_a=self.s.recv(2048)

		re_login = b2a_hex(re_login_a)
		print re_login
		while len(re_login)>600:
			print 'Need Verification Code!'
			img = re_login[28:]
			img = img[:-2]
			img_b = decrypt(a2b_hex(img),self.key)
			img_a = b2a_hex(img_b)

			img_a = re.search(r'8950\w+',img_a)
			img =  a2b_hex(img_a.group(0))

			#Maybe use 'with' is better
			f =open('test.jpg','wb')
			f.write(img)
			f.close()

			im = Image.open(os.path.abspath('.').replace('\\','/')+'/test.jpg')
			im.show()
			ver = raw_input('Verification Code: ')
			vercode = "020008003{0}003{1}003{2}003{3}".format(ver[0],ver[1],ver[2],ver[3])
			ver_b = encrypt(a2b_hex(vercode),self.key)
			ver_tea = "020027060800771f2a{}00{}03".format(self.qq_num,b2a_hex(ver_b))
			self.s.send(a2b_hex(ver_tea))

			re_login = b2a_hex(self.s.recv(2048))
			
			print 'Verification Code error,retry again.'

		if len(re_login)==206:
			print 'Login scuess!'
		else:
			print 'Login fail'

	def send(self,to_num,msg):
		to_num = hex(to_num)[2:]
		if  len(to_num)==9:
			to_num = to_num[:-1]
		mid = random.randint(4096,65535)
		mid = hex(mid)[2:]



		msg_0 = "{}0012{}00200000090000000086028b5b534f0d".format(to_num,bigendian2hex(msg))
		msg_1 = b2a_hex(encrypt(a2b_hex(msg_0),self.key))
		msg_3 = "02003706080055{}{}00{}03".format(mid,self.qq_num,msg_1)

		self.s.send(a2b_hex(msg_3))
		print 're_msg'+b2a_hex(self.s.recv(2048))

	def logout(self):
		pac_end = "02000f06080051361e{}0003".format(self.qq_num)
		self.s.send(a2b_hex(pac_end))
		print 'end:' + b2a_hex(self.s.recv(1024))
		self.s.close()



if __name__ == "__main__":
	test = QQ(1111111,'password')
	test.login()
	for i in xrange(10):
		time.sleep(1)
		test.send(22222222,u'This is test message')
	test.logout()