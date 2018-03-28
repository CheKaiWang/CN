import time
import socket
f = open('config','r')
chan = f.read()[6:-2]
print chan
IRCSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
IRCSocket.connect(('irc.freenode.net' ,6667))
print IRCSocket.recv(4096)
IRCSocket.send('NICK rendybot\r\n')
print IRCSocket.recv(4096)
IRCSocket.send('USER rendybot rendybot rendybot :rendybot\r\n')
print IRCSocket.recv(4096)
IRCSocket.send('JOIN '+chan+'\r\n')
print IRCSocket.recv(4096)
IRCSocket.send('PRIVMSG '+chan+' :Hello! I am robot.\r\n')
print IRCSocket.recv(4096)
while True:
	data = IRCSocket.recv(4096)
	print data
	if(data.find('@repeat '))!=-1:
		datat = data[data.find('@repeat')+8:]
		IRCSocket.send('PRIVMSG '+chan+' :'+datat+'\r\n')
	elif(data.find('@convert '))!=-1:
		num = data[data.find('@convert ')+9:]
		if(num.find('0x'))!=-1:
			num = str(int(num,16))
		else:
			num = hex(int(num))
		IRCSocket.send('PRIVMSG '+chan+' :'+num+'\r\n')
	elif(data.find('@ip '))!=-1:
		anslist = []
		s = data[data.find('@ip ')+4:-2]
		org = list(s)
		for i in range(1,len(org)-2):
			org.insert(i,'.')
			for j in range(i+2,len(org)-1):
				org.insert(j,'.')
				for k in range(j+2,len(org)):
					org.insert(k,'.')
					a = 0
					new = (''.join(org)).split('.')
					for l in range(4):
						if(int(new[l])>255 or len(new[l])!=len(str(int(new[l])))):
							a = 1
							break
					if(a!=1):
						anslist.append(''.join(org))
					del org[k]
				del org[j]
			del org[i]
		IRCSocket.send('PRIVMSG '+chan+' :'+str(len(anslist))+'\r\n')
		for i in range(len(anslist)):
			time.sleep(0.8)
			IRCSocket.send('PRIVMSG '+chan+' :'+anslist[i]+'\r\n')
	elif(data.find('@help'))!=-1:
			IRCSocket.send('PRIVMSG '+chan+' :@repeat <Message>\r\n')
			IRCSocket.send('PRIVMSG '+chan+' :@convert <Number>\r\n')
			IRCSocket.send('PRIVMSG '+chan+' :@ip <String>\r\n')
	elif(data.find('PING'))!=-1:
		IRCSocket.send('PONG '+ data.split()[1]+'\r\n')


