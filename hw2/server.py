import socket
import sys
import time
import errno

host = 'localhost'
agent_host = 'localhost'
sendfile = sys.argv[1]
port_send = 6668
port_recv = 6669
sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_recv = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_recv.bind((host, port_recv))

sock_send.sendto(bytes(sendfile.encode('utf8')), (agent_host, port_send))
sock_recv.setblocking(0)

exit_sign = False
tot = 0
thd = 16
wdw = 0
byte = ["" for i in range(32)]
cnt = 1
bytenum = [0 for i in range(32)]
acked = [1 for i in range(32)]

def terminate():
	print "send\tfin"
	sock_send.sendto(bytes("finish ".encode('utf8')),(agent_host,port_send))
	get = 0
	while get == 0:
		try:
			data, addr = sock_recv.recvfrom(1024)
		except socket.error:
			continue
		get = 1
		if "finish" == data.split(b' ',1)[0].decode('utf8'):
			print "recv\tfinack"
			sys.exit()

f = open(sys.argv[1],'rb')
while True:
	action = 1
	for i in range(wdw):
		if tot == 1 and acked[i] == 0 and bytenum[i] != 0:
			print "resnd\tdata\t#"+str(bytenum[i])+",\twinsize = "+str(wdw)
			sock_send.sendto(byte[i],(agent_host,port_send))
			action = 0
	tot = 0
	if action == 1 and exit_sign ==1:
		terminate()
	elif action == 1:
		if wdw == 0:
			wdw = 1
		elif wdw < thd:
			wdw *= 2
		elif wdw>= 32:
			wdw = 32
		else:
			wdw+=1
		for i in range(wdw):
			if bytenum[i] == 0:
				acked[i] = 0
				byte[i] = f.read(1020-len(str(cnt)))
				if not byte[i]:
					exit_sign = True
					for j in range(i,32):
						bytenum[j] = 87
						acked[j] = 1	
					break
				bytenum[i] = cnt
				byte[i] = bytes((str(bytenum[i])+' '+byte[i]).encode('utf8'))
				print "send\tdata\t#"+str(bytenum[i])+",\twinsize = "+str(wdw)
				sock_send.sendto(byte[i],(agent_host,port_send))
				cnt = cnt + 1
			else:
				print "resnd\tdata\t#"+str(bytenum[i])+",\twinsize = "+str(wdw)
				sock_send.sendto(byte[i],(agent_host,port_send))
	time.sleep(0.8)
	shift = 0
	for i in range(wdw):
		try:
			data, addr = sock_recv.recvfrom(1024)
		except socket.error:
			continue
		sentnum = int(data.decode('utf8').split(' ',1)[0])
		acknum = int(data.decode('utf8').split(' ',1)[1])
		print "recv\tack\t#"+str(acknum)

		if acknum > sentnum:
			break
		elif sentnum == acknum and i == shift:
			shift+=1
		elif sentnum == acknum:
			for j in range(wdw):
				if sentnum == bytenum[j]:
					acked[j] = 1
					byte[j] = 0
					bytenum[j] = 0
					break
	if shift != 0:
		for i in range(shift,32):
			byte[i - shift] = byte[i]
			bytenum[i - shift] = bytenum[i]
			acked[i - shift] = acked[i]
			if bytenum[i] != 0:
				acked[i] = 1
				byte[i] = 0
				bytenum[i] = 0
		for i in range(32 - shift,32):
			byte[i],bytenum[i],acked[i] = '',0,1
	if not bytenum[0] and bytenum[1] != 0:
		terminate()
	if shift != wdw:
		thd = max(int(wdw/2),1)
		print('time\tout,\t\tthreshold = %d' %(thd))
		tot = 1