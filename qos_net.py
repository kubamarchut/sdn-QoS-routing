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
from mininet.node import CPULimitedHost
from mininet.log import  setLogLevel, info
from threading import Timer
from mininet.util import quietRun
from mininet.cli import CLI
from mininet.node import RemoteController
from functools import partial
from time import sleep

def myNet(cname='controller', cargs='-v ptcp:'):
    "Create a two-switch network from scratch using Open vSwitch."
    net = Mininet(host=CPULimitedHost, link=TCLink, controller=partial(RemoteController, ip='127.0.0.1', port=6633))
    info( "*** Creating nodes\n" )
    # Creating nodes
    controller = net.addController('c0')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    switch3 = net.addSwitch('s3')
    switch4 = net.addSwitch('s4')
    switch5 = net.addSwitch('s5')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')
    h6 = net.addHost('h6')

    # Creating links
    net.addLink(h1, switch1, bw=100, delay='0ms', loss=0)
    net.addLink(h2, switch1, bw=100, delay='0ms', loss=0)
    net.addLink(h3, switch1, bw=100, delay='0ms', loss=0)
    net.addLink(switch1, switch2, bw=100, delay='200ms', loss=0)
    net.addLink(switch1, switch3, bw=100, delay='50ms', loss=0)
    net.addLink(switch1, switch4, bw=100, delay='10ms', loss=0)
    net.addLink(switch2, switch5, bw=100, delay='0ms', loss=0) 
    net.addLink(switch3, switch5, bw=100, delay='0ms', loss=0)
    net.addLink(switch4, switch5, bw=100, delay='0ms', loss=0)
    net.addLink(switch5, h4, bw=100, delay='0ms', loss=0)
    net.addLink(switch5, h5, bw=100, delay='0ms', loss=0)
    net.addLink(switch5, h6, bw=100, delay='0ms', loss=0)

    # Configuring hosts
    h1.setIP('10.0.0.1/24')
    h2.setIP('10.0.0.2/24')
    h3.setIP('10.0.0.3/24')
    h4.setIP('10.0.0.4/24')
    h5.setIP('10.0.0.5/24')
    h6.setIP('10.0.0.6/24')

    h1.setMAC("1:1:1:1:1:1")
    h2.setMAC("2:2:2:2:2:2")
    h3.setMAC("3:3:3:3:3:3")
    h4.setMAC("4:4:4:4:4:4")
    h5.setMAC("5:5:5:5:5:5")
    h6.setMAC("6:6:6:6:6:6")

    # Setting MAC addresses for switch interfaces
    switch1.intf('s1-eth1').setMAC("0:1:0:0:0:1")
    switch1.intf('s1-eth2').setMAC("0:1:0:0:0:2")
    switch1.intf('s1-eth3').setMAC("0:1:0:0:0:3")

    switch2.intf('s2-eth1').setMAC("0:1:0:0:0:4")
    switch2.intf('s2-eth2').setMAC("0:2:0:0:0:1")

    switch3.intf('s3-eth1').setMAC("0:1:0:0:0:5")
    switch3.intf('s3-eth2').setMAC("0:3:0:0:0:1")

    switch4.intf('s4-eth1').setMAC("0:1:0:0:0:6")
    switch4.intf('s4-eth2').setMAC("0:4:0:0:0:1")

    switch5.intf('s5-eth1').setMAC("0:2:0:0:0:2")
    switch5.intf('s5-eth2').setMAC("0:3:0:0:0:2")
    switch5.intf('s5-eth3').setMAC("0:4:0:0:0:2")
    switch5.intf('s5-eth4').setMAC("0:5:0:0:0:4")
    switch5.intf('s5-eth5').setMAC("0:5:0:0:0:5")
    switch5.intf('s5-eth6').setMAC("0:5:0:0:0:6")

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

    info( "*** Configuring hosts\n" )
    # Starting network
    net.start()

    info( '*** Waiting for switches to connect to the controller' )
    while 'is_connected' not in quietRun( 'ovs-vsctl show' ):
        sleep( 1 )
        info( '.' )
    info( '\n' )

    def cDelay1(): #function called back to set the link delay to 50 ms; both directions have to be set
       #switch.cmdPrint('ethtool -K s0-eth1 gro off') #not supported by VBox, use the tc tool as below
       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 10ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth1 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth1 root handle 10: netem delay 10ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 200ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s3-eth1 root')
       switch3.cmdPrint('tc qdisc add dev s3-eth1 root handle 10: netem delay 200ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth6 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth6 root handle 10: netem delay 50ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s4-eth1 root')
       switch4.cmdPrint('tc qdisc add dev s4-eth1 root handle 10: netem delay 50ms') #originally 10 ms

       info( '+++++++++++++ First change started\n' )

    def cDelay2(): #function called back to set the link delay to 200ms
       #switch.cmdPrint('ethtool -K s0-eth1 gro off')  #ethtool works for GRO only on specific interfaces
       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 50ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth1 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth1 root handle 10: netem delay 50ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 10ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s3-eth1 root')
       switch3.cmdPrint('tc qdisc add dev s3-eth1 root handle 10: netem delay 10ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth6 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth6 root handle 10: netem delay 200ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s4-eth1 root')
       switch4.cmdPrint('tc qdisc add dev s4-eth1 root handle 10: netem delay 200ms') #originally 10 ms

       info( '+++++++++++++ Second change started\n' )

    def cDelay3(): #function called back to set the link delay to 200ms
       #switch.cmdPrint('ethtool -K s0-eth1 gro off')  #ethtool works for GRO only on specific interfaces
       switch1.cmdPrint('tc qdisc del dev s1-eth4 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth4 root handle 10: netem delay 200ms')  #originally 200 ms
       #switch1.cmdPrint('ethtool -K s1-eth0 gro off') #not supported by VBox, use the tc tool as below
       switch2.cmdPrint('tc qdisc del dev s2-eth1 root')
       switch2.cmdPrint('tc qdisc add dev s2-eth1 root handle 10: netem delay 200ms') #originally 200 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth5 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth5 root handle 10: netem delay 50ms')  #originally 50 ms
       switch3.cmdPrint('tc qdisc del dev s3-eth1 root')
       switch3.cmdPrint('tc qdisc add dev s3-eth1 root handle 10: netem delay 50ms') #originally 50 ms

       switch1.cmdPrint('tc qdisc del dev s1-eth6 root')
       switch1.cmdPrint('tc qdisc add dev s1-eth6 root handle 10: netem delay 10ms')  #originally 10 ms 
       switch4.cmdPrint('tc qdisc del dev s4-eth1 root')
       switch4.cmdPrint('tc qdisc add dev s4-eth1 root handle 10: netem delay 10ms') #originally 10 ms

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
    CLI(net)

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

