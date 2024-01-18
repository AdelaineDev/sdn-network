
from mininet.net import Mininet
from mininet.net import CLI
from mininet.node import Host, Controller, RemoteController
import socket
import time
import subprocess
import threading
import sys
import os

global net, h1, h2, h3, h4, c, c0
global a, b, c, d

def servidor(host, port, net):

    print("->Iniciando servidor %s..." % host.name) 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP

    sock.bind(('0.0.0.0', port))

    print("    Servidor %s pronto e ouvindo na porta %s!" % (host.name, port))
    time.sleep(1)
    try:
        while True:

            data, addr = sock.recvfrom(1024) #recebimento de mensagens udp
            data = eval(data.decode())
            response = " "
            if data[2] == 'DESCOBERTA':
                msg = ( str(host.IP()), str(host.name), str(port) )

            elif data[2] == 'Oi':
                print("%s> %s" % (data[1], data[2]))
                msg = ( host.IP(), host.name, "Em que posso ser util?" )

            elif data[2] == "Apenas testando, obrigado!":
                print("%s> %s" % (data[1], data[2]))
                msg = ( host.IP(), host.name, "Ok, irei finalizar!" )

            elif data[2] == "tudo bem, bye!":
                print("%s> %s" % (data[1], data[2])) 
		time.sleep(1)
		sock.close() 
	        
                a.join()
	        b.join()
	        c.join()
	        d.join()
                break
	    
            if len(data):
	    	sock.sendto(str(msg).encode(), addr)
	    else:
		print("aguardando...")


    finally:   
        return 

        

def cliente(host, net):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("\nInicializando Cliente...")
    for _ in range(2):
        print('  Enviando mensagem de descoberta...')
        sonda = ( host.IP(), host.name, "DESCOBERTA" )
        sock.sendto(str(sonda).encode(), ('<broadcast>', 5001))
        sock.sendto(str(sonda).encode(), ('<broadcast>', 5002))
        sock.sendto(str(sonda).encode(), ('<broadcast>', 5003))
       

    servidores = []
    ends = []

    while len(servidores)!=3:
        data, addr = sock.recvfrom(1024)
        if data and data.decode() not in servidores:
            servidores.append(data.decode())
            ends.append(addr)
            print("  Resposta do servidor %s" % data)
    
                   
    print('\n  Escolha um servidor para se comunicar:')
    for i, servidor in enumerate(servidores):
        print('  %d - %s' % (i+1, servidor))
    try:
        esc = int(input('\n  Escolha:> ')) -1
        concluido = True
        print("\nC H A T  A U T O M A T I C O  I N I C I A D O")
        print("-------------------------------------------------")

        tupla = ends[esc]
        msg = ( host.IP(), host.name, "Oi" )
        sock.sendto(str(msg).encode(), tupla)
    except KeyboardInterrupt:
        net.stop()        
        os._exit(0)

    
    while True:
            data, addr = sock.recvfrom(1024)
            data = eval(data.decode())
            if data[2] == "Em que posso ser util?":
                print("%s> %s" % (data[1], data[2]))
                msg = ( host.IP(), host.name, "Apenas testando, obrigado!" )
                sock.sendto(str(msg).encode(), addr)
            elif data[2] == "Ok, irei finalizar!":
                print("%s> %s" % (data[1], data[2]))
                msg = ( host.IP(), host.name, "tudo bem, bye!" )
                sock.sendto(str(msg).encode(), addr)
                break
    sock.close() 
    time.sleep(1)
    print("\nC h a t   E n c e r r a d o!\nEncerrar programa?")
    r=int(input("[press 0] -> "))
    if r >= 0:
    	net.stop()
    	os._exit(0)
       



def criar_rede():
    net = Mininet(host=Host, controller = RemoteController)

    c0 = net.addController('c0',  controller = RemoteController, ip="0.0.0.0", port=6633)

    h1 = net.addHost('WEB', ip='10.1.1.2')   #SERVIDOR 
    h2 = net.addHost('DADOS', ip='10.2.1.3')  #SERVIDOR
    h3 = net.addHost('MAIL', ip='10.3.1.5')   #SERVIDOR
    h4 = net.addHost('CLIENTE', ip='10.4.1.6') # Cliente
    h5 = net.addHost('h5', ip='10.5.1.7')     #host adicional
    h6 = net.addHost('h6', ip='10.6.1.8')   #host adicional

    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s4)
    net.addLink(s4, s1)

    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)
    net.addLink(h4, s4)
    net.addLink(h5, s1)
    net.addLink(h6, s2)

    net.start()
    
    return net, c0, h1, h2, h3, h4


def ini():
	try:
	    os.system('sudo mn -c')
	    os.system('clear')
	    
	    print("\nM i n i n e t:\n")
	    print("1 - criar topologia")
	    print("0 - sair\n")
	    resp = int(input('-> '))

	    if resp == 1:

		net, c0, h1, h2, h3, h4 = criar_rede()   
		#time.sleep(1)
		
		print("\nnodes:")
		for h in net.hosts:
		    print("  %s (%s)" % (h.name, h.IP()))
		print("  4 switches em loop (s1, s2, s3, s4)")   
		print("\n") 
		while True: 
		   try:
		     if net != None:
			print("Realizando pingall para mapeamento...\n")
			print(net.pingAll())		
			print("\nTeste de conexao final:\n")
			print(net.pingAll())
			break
    		   except KeyboardInterrupt:
        		break
		print("\n--> Inicializacao de servidores:\n")
	        a = threading.Thread(target=servidor, args=(h1, 5001, net))
	        b = threading.Thread(target=servidor, args=(h2, 5002, net))
	        c = threading.Thread(target=servidor, args=(h3, 5003, net))
	        d = threading.Thread(target=cliente, args=(h4, net))
		
		threads = [a,b,c,d]
		for t in threads:
			t.start()
		
	    
	    else:
		sys.exit()    
	    

	except KeyboardInterrupt:
	    print("\n")
            a.join()
	    b.join()
	    c.join()
	    d.join()
            net.stop()     
            time.sleep(2)
	    sys.exit(0)
        except socket.error as e:
	    print("\nproblemas na inicializacao do servidor %s..." % host.name)


ini()


