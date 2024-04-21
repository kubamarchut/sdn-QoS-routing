#!/usr/bin/python

"""
Create a 2-switch network, change link latency and measure the delay using ping. Wait for connecting to the controller to starting pinging.
The mininet network makes three passes, each ~15 sec long and each with a different value of the delay on the link between the switches.
Derived from: https://github.com/mininet/mininet/blob/master/examples/scratchnet.py and http://csie.nqu.edu.tw/smallko/sdn/latency.htm.
Note: you can change the duration of the experiment by adjusting the timers t1, t2 and the number of ICMP echo copies in option -c of the ping command
"""

from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import  setLogLevel, info
from threading import Timer
from mininet.util import quietRun
from time import sleep

def myNet(cname='controller', cargs='-v ptcp:'):
    "Create a two-switch network from scratch using Open vSwitch."
    info( "*** Creating nodes\n" )
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

    "Initial link settings, initial delay of link switch-switch2 set to 10 ms"
    "host link delays set to 1ms"
    info( "*** Creating links\n" )
    linkopts0=dict(bw=100, delay='1ms', loss=0)
    linkopts1=dict(bw=100, delay='200ms', loss=0)
    linkopts2=dict(bw=100, delay='50ms', loss=0)
    linkopts3=dict(bw=100, delay='10ms', loss=0)
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

    "print link0.intf1, link0.intf2"
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

    info( "*** Configuring hosts\n" )
    h1.setIP( '10.0.0.1/24' )
    h2.setIP( '10.0.0.2/24' )
    h3.setIP( '10.0.0.3/24' )
    h4.setIP( '10.0.0.4/24' )
    h5.setIP( '10.0.0.5/24' )
    h6.setIP( '10.0.0.6/24' ) 
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

    "Setting the connections from the switches to the controller"
    # Note: controller and switch are in root namespace, and we
    # can connect them via the loopback interface; otherwise
    # external IP address of the controller should be specified below
    switch1.cmd( 'ovs-vsctl set-controller dp1 tcp:127.0.0.1:6633') # for the switch and controller both attached to localhost
    switch2.cmd( 'ovs-vsctl set-controller dp2 tcp:127.0.0.1:6633') # for the switch and controller both attached to localhost
    switch3.cmd( 'ovs-vsctl set-controller dp3 tcp:127.0.0.1:6633') # for the switch and controller both attached to localhost
    switch4.cmd( 'ovs-vsctl set-controller dp4 tcp:127.0.0.1:6633') # for the switch and controller both attached to localhost
    switch5.cmd( 'ovs-vsctl set-controller dp5 tcp:127.0.0.1:6633') # for the switch and controller both attached to localhost

    info( '*** Waiting for switches to connect to the controller' )
    while 'is_connected' not in quietRun( 'ovs-vsctl show' ):
        sleep( 1 )
        info( '.' )
    info( '\n' )

    def cDelay1(): #function called back to set the link delay to 50 ms; both directions have to be set
       #switch.cmdPrint('ethtool -K s0-eth1 gro off') #not supported by VBox, use the tc tool as below
       switch1.cmdPrint('tc qdisc del dev s1-eth3 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth3 root handle 10: netem delay 10ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 10ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 200ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s3-eth0 root')
       switch3.cmdPrint('tc qdisc add dev s3-eth0 root handle 10: netem delay 200ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 50ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s4-eth0 root')
       switch4.cmdPrint('tc qdisc add dev s4-eth0 root handle 10: netem delay 50ms') #originally 10 ms

       info( '+++++++++++++ First change started\n' )

    def cDelay2(): #function called back to set the link delay to 200ms
       #switch.cmdPrint('ethtool -K s0-eth1 gro off')  #ethtool works for GRO only on specific interfaces
       switch1.cmdPrint('tc qdisc del dev s1-eth3 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth3 root handle 10: netem delay 50ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 50ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 10ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch3.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 10ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 200ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch4.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 200ms') #originally 10 ms

       info( '+++++++++++++ Second change started\n' )

    def cDelay3(): #function called back to set the link delay to 200ms
       #switch.cmdPrint('ethtool -K s0-eth1 gro off')  #ethtool works for GRO only on specific interfaces
       switch1.cmdPrint('tc qdisc del dev s1-eth3 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth3 root handle 10: netem delay 200ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 200ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 50ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch3.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 50ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 10ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s2-eth0 root')
       switch4.cmdPrint('tc qdisc add dev s2-eth0 root handle 10: netem delay 10ms') #originally 10 ms

       info( '+++++++++++++ Third change started\n' )


    # From this moment, the network is going to route with the inter-switch link delay equal 10 ms (inintial value)
    # The two timers set below will set two another link delay values in the 15th and 30th second of the experiment.
    # Note: 45sec long ping run determines the duration of the whole experiment.

    switch1.cmdPrint('ip a')
    switch2.cmdPrint('ip a')
    switch3.cmdPrint('ip a')
    switch4.cmdPrint('ip a')
    switch5.cmdPrint('ip a')

    #def updateDelays():
    #    cDelay1()
    #    Timer(15, cDelay2).start()
    #    Timer(30, cDelay3).start()
    #    Timer(45, updateDelays).start()

    #updateDelays()

    info( '+++++++++++++ Setting t1   ' )
    "Timer t1 is set to trigger function cDelay1 after the period of 21 sec which will set link delay to 200ms"
    "When t1 expires, cDelay1 is triggered and link delay is set to 50ms"
    t1=Timer(5, cDelay1)
    t1.start()
    info( '+++++++++++++ t1 started\n' )

    info( '+++++++++++++ Setting t2   ' )
    "36 seconds later, link delay from switch to switch 1 will change to 200ms"
    "The whole procedure is analogous to the t1 case commented above"
    t2=Timer(10, cDelay2)
    t2.start()
    info( '+++++++++++++ t2 started\n' )

    info( '+++++++++++++ Setting t3   ' )
    t3=Timer(15, cDelay3)
    t3.start()
    info( '+++++++++++++ t3 started\n' )

    info( "\n*** Running the test\n\n" )

    # Generate 45 ICMP echo requests, one per second, which accounts to 45 seconds
    " The script will stay in this ping phase for 51 seconds only being interrupted by t1 and t2."
    " All values (includig -c 51 in the ping command) have been tuned to provide an equal"
    " number of 15 ICMP echoes in each iteration."
    " Note also h0-to-h1 ping delay (RTT) will include delays h0-switch and switch1-h1"
    #h1.cmdPrint( 'ping -i 1 -c 70 ' + h4.IP() )

    #sleep( 1 )
    #info( "*** Stopping the network\n" )
    #controller.cmd( 'kill %' + cname )
    #switch1.cmd( 'ovs-vsctl del-br dp1' )
    #switch1.deleteIntfs()
    #switch2.cmd( 'ovs-vsctl del-br dp2' )
    #switch2.deleteIntfs()
    #switch3.cmd( 'ovs-vsctl del-br dp3' )
    #switch3.deleteIntfs()
    #switch4.cmd( 'ovs-vsctl del-br dp4' )
    #switch4.deleteIntfs()
    #switch5.cmd( 'ovs-vsctl del-br dp5' )
    #switch5.deleteIntfs()
    #info( '\n' )

if __name__ == '__main__':
    setLogLevel( 'info' )
    info( '*** Scratch network demo (kernel datapath)\n' )
    Mininet.init()
    myNet()

