#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import  setLogLevel, info
from threading import Timer
from mininet.util import quietRun
from mininet.cli import CLI
from time import sleep

XTERM_STR = "xterm -xrm \'XTerm.vt100.allowTitleOps: false\'"

def myNet(cname='controller', cargs='-v ptcp:'):
    info( "*** Creating nodes ***\n" )
    controller = Node( 'c0', inNamespace=False )
    switch1 = Node( 's1', inNamespace=False )
    switch2 = Node( 's2', inNamespace=False )
    switch3 = Node( 's3', inNamespace=False )
    switch4 = Node( 's4', inNamespace=False )
    switch5 = Node( 's5', inNamespace=False )
    h1 = Node( 'h1' )
    h2 = Node( 'h2' )
    h3 = Node( 'h3' )
    h4 = Node( 'h4' )
    h5 = Node( 'h5' )
    h6 = Node( 'h6' )

    # Initial link settings, initial delay of links
    # host link delays set to 0ms
    info( "*** Creating links ***\n" )
    linkopts0=dict(bw=1000, delay='0ms', loss=0)
    linkopts1=dict(bw=1000, delay='200ms', loss=0)
    linkopts2=dict(bw=1000, delay='50ms', loss=0)
    linkopts3=dict(bw=1000, delay='10ms', loss=0)
    link1 = TCLink( h1, switch1, **linkopts0)
    link2 = TCLink( h2, switch1, **linkopts0)
    link3 = TCLink( h3, switch1, **linkopts0)
    link4 = TCLink( switch1, switch2, **linkopts1) #initially, the delay from switch1 to switch2 is 200ms
    link5 = TCLink( switch1, switch3, **linkopts2) #initially, the delay from switch1 to switch3 is 50ms
    link6 = TCLink( switch1, switch4, **linkopts3) #initially, the delay from switch1 to switch4 is 10ms
    link7 = TCLink( switch2, switch5, **linkopts0)
    link8 = TCLink( switch3, switch5, **linkopts0)
    link9 = TCLink( switch4, switch5, **linkopts0)
    link10 = TCLink( switch5, h4, **linkopts0)
    link11 = TCLink( switch5, h5, **linkopts0)
    link12 = TCLink( switch5, h6, **linkopts0)

    link1.intf2.setMAC("0:1:0:0:0:1") #h1-s1
    link2.intf2.setMAC("0:1:0:0:0:2") #h2-s1
    link3.intf2.setMAC("0:1:0:0:0:3") #h3-s1

    link4.intf1.setMAC("0:1:0:0:0:4") #s1-s2
    link4.intf2.setMAC("0:2:0:0:0:1") #s2-s1

    link5.intf1.setMAC("0:1:0:0:0:5") #s1-s3
    link5.intf2.setMAC("0:3:0:0:0:1") #s3-s1

    link6.intf1.setMAC("0:1:0:0:0:6") #s1-s4
    link6.intf2.setMAC("0:4:0:0:0:1") #s4-s1

    link7.intf1.setMAC("0:2:0:0:0:2") #s2-s5
    link7.intf2.setMAC("0:5:0:0:0:1") #s5-s2

    link8.intf1.setMAC("0:3:0:0:0:2") #s3-s5
    link8.intf2.setMAC("0:5:0:0:0:2") #s5-s3

    link9.intf1.setMAC("0:4:0:0:0:2") #s4-s5
    link9.intf2.setMAC("0:5:0:0:0:3") #s5-s4

    link10.intf1.setMAC("0:5:0:0:0:4") #s5-h4
    link11.intf1.setMAC("0:5:0:0:0:5") #s5-h5
    link12.intf1.setMAC("0:5:0:0:0:6") #s5-h6

    info( "*** Configuring hosts ***\n" )
    h1.setIP( '10.0.0.1/24' )
    h2.setIP( '10.0.0.2/24' )
    h3.setIP( '10.0.0.3/24' )
    h4.setIP( '10.0.0.4/24' )
    h5.setIP( '10.0.0.5/24' )
    h6.setIP( '10.0.0.6/24' )
    
    h1_cmd = XTERM_STR + " -T \'host 1\' &"
    h2_cmd = XTERM_STR + " -T \'host 2\' &"
    h3_cmd = XTERM_STR + " -T \'host 3\' &"
    
    h1.cmd(h1_cmd)
    h2.cmd(h2_cmd)
    h3.cmd(h3_cmd)
    
    h1.setMAC("1:1:1:1:1:1")
    h2.setMAC("2:2:2:2:2:2")
    h3.setMAC("3:3:3:3:3:3")
    h4.setMAC("4:4:4:4:4:4")
    h5.setMAC("5:5:5:5:5:5")
    h6.setMAC("6:6:6:6:6:6")

    info( "*** Starting network using Open vSwitch\n" )
    switch1.cmd( 'ovs-vsctl del-br dp1' )
    switch1.cmd( 'ovs-vsctl add-br dp1' )
    switch2.cmd( 'ovs-vsctl del-br dp2' )
    switch2.cmd( 'ovs-vsctl add-br dp2' )
    switch3.cmd( 'ovs-vsctl del-br dp3' )
    switch3.cmd( 'ovs-vsctl add-br dp3' )
    switch4.cmd( 'ovs-vsctl del-br dp4' )
    switch4.cmd( 'ovs-vsctl add-br dp4' )
    switch5.cmd( 'ovs-vsctl del-br dp5' )
    switch5.cmd( 'ovs-vsctl add-br dp5' )


    controller.cmd( cname + ' ' + cargs + '&' )
    for intf in switch1.intfs.values():
        print intf
        print switch1.cmd( 'ovs-vsctl add-port dp1 %s' % intf )

    for intf in switch2.intfs.values():
        print intf
        print switch2.cmd( 'ovs-vsctl add-port dp2 %s' % intf )

    for intf in switch3.intfs.values():
        print intf
        print switch3.cmd( 'ovs-vsctl add-port dp3 %s' % intf )

    for intf in switch4.intfs.values():
        print intf
        print switch4.cmd( 'ovs-vsctl add-port dp4 %s' % intf )

    for intf in switch5.intfs.values():
        print intf
        print switch5.cmd( 'ovs-vsctl add-port dp5 %s' % intf )

    # Setting the connections from the switches to the controller
    switch1.cmd( 'ovs-vsctl set-controller dp1 tcp:127.0.0.1:6633') 
    switch2.cmd( 'ovs-vsctl set-controller dp2 tcp:127.0.0.1:6633')
    switch3.cmd( 'ovs-vsctl set-controller dp3 tcp:127.0.0.1:6633')
    switch4.cmd( 'ovs-vsctl set-controller dp4 tcp:127.0.0.1:6633')
    switch5.cmd( 'ovs-vsctl set-controller dp5 tcp:127.0.0.1:6633')

    info( '*** Waiting for switches to connect to the controller ***' )
    while 'is_connected' not in quietRun( 'ovs-vsctl show' ):
        sleep( 1 )
        info( '.' )
    info( '\n' )

    def cDelay1():
        # Function to change delays of links between s1 and s2, s3, s4 (first turn)
        switch1.cmd('tc qdisc del dev s1-eth3 root')
        switch1.cmd('tc qdisc add dev s1-eth3 root handle 10: netem delay 10ms')  #originally 200 ms
        switch2.cmd('tc qdisc del dev s2-eth0 root')
        switch2.cmd('tc qdisc add dev s2-eth0 root handle 10: netem delay 10ms') #originally 200 ms

        switch1.cmd('tc qdisc del dev s1-eth4 root')
        switch1.cmd('tc qdisc add dev s1-eth4 root handle 10: netem delay 200ms')  #originally 50 ms
        switch3.cmd('tc qdisc del dev s3-eth0 root')
        switch3.cmd('tc qdisc add dev s3-eth0 root handle 10: netem delay 200ms') #originally 50 ms

        switch1.cmd('tc qdisc del dev s1-eth5 root')
        switch1.cmd('tc qdisc add dev s1-eth5 root handle 10: netem delay 50ms')  #originally 10 ms 
        switch4.cmd('tc qdisc del dev s4-eth0 root')
        switch4.cmd('tc qdisc add dev s4-eth0 root handle 10: netem delay 50ms') #originally 10 ms

        info( '++++++ First change started ++++++\n' )

    def cDelay2():
        # Function to change delays of links between s1 and s2, s3, s4 (second turn)
        switch1.cmd('tc qdisc del dev s1-eth3 root')
        switch1.cmd('tc qdisc add dev s1-eth3 root handle 10: netem delay 50ms')  #originally 200 ms
        switch2.cmd('tc qdisc del dev s2-eth0 root')
        switch2.cmd('tc qdisc add dev s2-eth0 root handle 10: netem delay 50ms') #originally 200 ms

        switch1.cmd('tc qdisc del dev s1-eth4 root')
        switch1.cmd('tc qdisc add dev s1-eth4 root handle 10: netem delay 10ms')  #originally 50 ms
        switch3.cmd('tc qdisc del dev s3-eth0 root')
        switch3.cmd('tc qdisc add dev s3-eth0 root handle 10: netem delay 10ms') #originally 50 ms

        switch1.cmd('tc qdisc del dev s1-eth5 root')
        switch1.cmd('tc qdisc add dev s1-eth5 root handle 10: netem delay 200ms')  #originally 10 ms 
        switch4.cmd('tc qdisc del dev s4-eth0 root')
        switch4.cmd('tc qdisc add dev s4-eth0 root handle 10: netem delay 200ms') #originally 10 ms
        
        info( '++++++ Second change started ++++++\n' )

    def cDelay3():
        # Function to change delays of links between s1 and s2, s3, s4 (comming back to initial delays)
        switch1.cmd('tc qdisc del dev s1-eth3 root')
        switch1.cmd('tc qdisc add dev s1-eth3 root handle 10: netem delay 200ms')  #originally 200 ms
        switch2.cmd('tc qdisc del dev s2-eth0 root')
        switch2.cmd('tc qdisc add dev s2-eth0 root handle 10: netem delay 200ms') #originally 200 ms

        switch1.cmd('tc qdisc del dev s1-eth4 root')
        switch1.cmd('tc qdisc add dev s1-eth4 root handle 10: netem delay 50ms')  #originally 50 ms
        switch3.cmd('tc qdisc del dev s3-eth0 root')
        switch3.cmd('tc qdisc add dev s3-eth0 root handle 10: netem delay 50ms') #originally 50 ms

        switch1.cmd('tc qdisc del dev s1-eth5 root')
        switch1.cmd('tc qdisc add dev s1-eth5 root handle 10: netem delay 10ms')  #originally 10 ms 
        switch4.cmd('tc qdisc del dev s4-eth0 root')
        switch4.cmd('tc qdisc add dev s4-eth0 root handle 10: netem delay 10ms') #originally 10 ms

        info( '++++++ Third change started ++++++\n' )

    switch1.cmdPrint('ip a')
    switch2.cmdPrint('ip a')
    switch3.cmdPrint('ip a')
    switch4.cmdPrint('ip a')
    switch5.cmdPrint('ip a')
    
    interval = 30
    def updateDelays():
        cDelay1()
        Timer(interval, cDelay2).start()
        Timer(2*interval, cDelay3).start()
        Timer(3*interval, updateDelays).start()

    updateDelays()

    def start_ping():
        while True:
            try:
                src = input("Enter source host: ")
                dest = input("Enter destination host: ")
                src_host = globals()[src]
                dest_host = globals()[dest]
                info("*** Pinging between {} and {}\n".format(src, dest))
                result = src_host.cmd('ping -c 15 ' + dest_host.IP())
                print(result)
            except KeyError as e:
                print("Error: Host not found. Please enter valid host names.")
            except Exception as e:
                print("Error:", e)
            try:
                again = input("Do you want to ping again? (y/n): ").strip().lower()
                if again != 'y':
                    break
            except KeyboardInterrupt:
                break

    #start_ping()

def main():
    setLogLevel( 'info' )
    info( '*** Project network topology ***\n' )
    Mininet.init()
    myNet()

if __name__ == '__main__':
    main()
