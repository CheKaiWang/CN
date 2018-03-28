import socket
import sys
import random

host = 'localhost'
client_host = 'localhost'
server_host = 'localhost'
port_send_client = 6667
port_send_server = 6669
port_clinet_recv = 6666
port_server_recv = 6668

sock_agent_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_server_recv   = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_client_recv   = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )


sock_server_recv.bind((host,port_server_recv))
sock_client_recv.bind((host,port_clinet_recv))

data, addr = sock_server_recv.recvfrom(1024)
sock_agent_send.sendto(bytes(data),(host,port_send_client))

lossR = 0.0000
loss = 0
whole = 0

while True:
	data, addr = sock_server_recv.recvfrom(1024)
	if "finish" == data.split(b' ',1)[0].decode('utf8'):
		print "get\tfin\nfwd\tfin"
		sock_agent_send.sendto(bytes(data),(client_host,port_send_client))
	else :
		pktnum = int(data.split(b' ',1)[0])
		print "get\tdata\t#"+str(pktnum)
		whole += 1

		if random.random() < 0.987:
			sock_agent_send.sendto(bytes(data),(client_host,port_send_client))
			print "fwd\tdata\t#"+str(pktnum)+",\tloss rate = %f" %(float(float(loss)/float(whole)))
		else:
			loss+=1
			print "drop\tdata\t#"+str(pktnum)+",\tloss rate = %f" %(float(float(loss)/float(whole)))
			continue

	data, addr = sock_client_recv.recvfrom(1024)
	if "finish" == data.split(b' ',1)[0].decode('utf8'):
		print "get\tfinack\nfwd\tfinack"
		sock_agent_send.sendto(bytes(data),(server_host,port_send_server))
		break
	if "drop" == data.decode('utf8'):
		continue
	sock_agent_send.sendto(bytes(data),(server_host,port_send_server))
	acknum = data.split(b' ',1)[1].decode('utf8')
	print "get\tack\t#"+str(acknum)+"\nfwd\tack\t#"+str(acknum)