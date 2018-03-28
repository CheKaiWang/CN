import socket
import time
import sys

host = 'localhost'
agent_host = 'localhost'
port_recv = 6667
port_send = 6666
sock_recv = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_recv.bind((host, port_recv))


wdw = 32
head = 1
acknum = 1
byte = ["" for i in range(wdw)]
hole = [0 for i in range(wdw)]
bytenum = [0 for i in range(wdw)]

data, addr = sock_recv.recvfrom(1024)
f = open("result."+data.decode('utf8'),'wb')
while True:
	chk = 0
	data, addr = sock_recv.recvfrom(1024)
	if "finish" == data.split(b' ',1)[0].decode('utf8'):
		print "recv\tfin\nsend\tfinack\nflush"
		sock_send.sendto(bytes("finish ".encode('utf8')),(agent_host,port_send))
		for i in range(wdw):
			if bytenum[i] != 0:
				f.write(bytes(byte[i]))
		break
	for i in range(wdw):
		if bytenum[i] == 0:
			chk = 1
			break
	if chk == 0:
		print "flush"
		for i in range(wdw):
			if bytenum[i] != 0:
				f.write(bytes(byte[i]))
		head += wdw
		byte = [""for i in range(wdw)]
		bytenum = [0 for i in range(wdw)]
		hole = [0 for i in range(wdw)]
		sock_send.sendto(bytes("drop".encode('utf8')),(agent_host,port_send))
		pktnum = int(data.split(b' ',1)[0])
		print "drop\tdata\t#"+str(pktnum)
		continue
	pktnum = int(data.split(b' ',1)[0])
	pkt = data.split(b' ',1)[1]
	print "recv\tdata\t#"+str(pktnum)
	ack = str(pktnum)+" "+str(acknum)
	print "send\tack\t#"+str(acknum)
	if acknum <= pktnum:	
		sock_send.sendto(bytes(ack.encode('utf8')),(agent_host,port_send))
	if pktnum == acknum:
		for i in range(wdw):
			if hole[i] == 0:
				byte[i] = pkt
				bytenum[i] = pktnum
				acknum += 1
				hole[i] = 1
				break