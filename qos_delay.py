from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Node
from mininet.log import setLogLevel, info
from threading import Timer
from mininet.util import quietRun
from time import sleep
import os

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

    # (Code for setting MAC addresses remains unchanged)

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

    # (Code for setting ports and controller remains unchanged)

    info( '*** Waiting for switches to connect to the controller' )
    while 'is_connected' not in quietRun( 'ovs-vsctl show' ):
        sleep( 1 )
        info( '.' )
    info( '\n' )

    def cDelay1():
        # (Code for setting delays remains unchanged)
        info( '+++++++++++++ First change started\n' )

    def cDelay2():
        # (Code for setting delays remains unchanged)
        info( '+++++++++++++ Second change started\n' )

    def cDelay3():
        # (Code for setting delays remains unchanged)
        info( '+++++++++++++ Third change started\n' )

    info( '+++++++++++++ Setting t1   ' )
    Timer(5, cDelay1).start()
    info( '+++++++++++++ t1 started\n' )

    info( '+++++++++++++ Setting t2   ' )
    Timer(10, cDelay2).start()
    info( '+++++++++++++ t2 started\n' )

    info( '+++++++++++++ Setting t3   ' )
    Timer(15, cDelay3).start()
    info( '+++++++++++++ t3 started\n' )

    info( "\n*** Running the test\n\n" )

    # Generate 45 ICMP echo requests, one per second
    # h1.cmdPrint( 'ping -i 1 -c 45 ' + h4.IP() )

    # Start Mininet CLI in interactive mode
    CLI(net)

if __name__ == '__main__':
    setLogLevel( 'info' )
    info( '*** Scratch network demo (kernel datapath)\n' )
    myNet()
