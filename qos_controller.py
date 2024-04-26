# The program implements a simple controller for a network with 6 hosts and 5 switches.
# The switches are connected in a diamond topology (without vertical links):
#    - 3 hosts are connected to the left (s1) and 3 to the right (s5) edge of the diamond.
# Overall operation of the controller:
#    - default routing is set in all switches on the reception of packet_in messages form the switch,
#    - then the routing between each host pair is set based on QoS rules

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.packet_base import packet_base
from pox.lib.packet.packet_utils import *
import pox.lib.packet as pkt
from pox.lib.recoco import Timer

import time
import json
 
log = core.getLogger()
 
s1_dpid=0
s2_dpid=0
s3_dpid=0
s4_dpid=0
s5_dpid=0
 
s1_p1=0
s1_p4=0
s1_p5=0
s1_p6=0
s2_p1=0
s3_p1=0
s4_p1=0
 
pre_s1_p1=0
pre_s1_p4=0
pre_s1_p5=0
pre_s1_p6=0
pre_s2_p1=0
pre_s3_p1=0
pre_s4_p1=0

start_time=0
OWD1=0.0
OWD2=0.0
OWD3=0.0
OWD4=0.0

sent_time1 = 0
sent_time2 = 0
sent_time3 = 0
sent_time4 = 0
sent_time5 = 0
sent_time6 = 0

network_ready = False

class Link:
  def __init__(self, name, delay=float("inf")):
    self.name = name
    self.delay_hist = []
    self.delay = delay
    self.connection = 0
    self.congestion = 0

links = {
  "s1-s2": Link("s1-s2"),
  "s1-s3": Link("s1-s3"),
  "s1-s4": Link("s1-s4"),
}

#probe protocol packet definition; only timestamp field is present in the header (no payload part)
class myproto(packet_base):
  #My Protocol packet struct
  """
  myproto class defines our special type of packet to be sent all the way along including the link between the switches to measure link delays;
  it adds member attribute named timestamp to carry packet creation/sending time by the controller, and defines the 
  function hdr() to return the header of measurement packet (header will contain timestamp)
  """
  #For more info on packet_base class refer to file pox/lib/packet/packet_base.py

  def __init__(self):
     packet_base.__init__(self)
     self.timestamp=0

  def hdr(self, payload):
     return struct.pack('!I', self.timestamp) # code as unsigned int (I), network byte order (!, big-endian - the most significant byte of a word at the smallest memory address)

def getTheTime():  #function to create a timestamp
  flock = time.localtime()
  then = "[%s-%s-%s" %(str(flock.tm_year),str(flock.tm_mon),str(flock.tm_mday))
 
  if int(flock.tm_hour)<10:
    hrs = "0%s" % (str(flock.tm_hour))
  else:
    hrs = str(flock.tm_hour)
  if int(flock.tm_min)<10:
    mins = "0%s" % (str(flock.tm_min))
  else:
    mins = str(flock.tm_min)
 
  if int(flock.tm_sec)<10:
    secs = "0%s" % (str(flock.tm_sec))
  else:
    secs = str(flock.tm_sec)
 
  then +="]%s.%s.%s" % (hrs,mins,secs)
  return then

def measure_delay(src_dpid, dst_dpid, src_mac, dst_mac, port):
  global start_time
  if src_dpid <>0 and not core.openflow.getConnection(src_dpid) is None:
    #send out port_stats_request packet through switch0 connection src_dpid (to measure T1)
    core.openflow.getConnection(src_dpid).send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    sent_time1=time.time() * 1000*10 - start_time #sending time of stats_req: ctrl => switch0
    #print "sent_time1:", sent_time1

    #sequence of packet formating operations optimised to reduce the delay variation of e-2-e measurements (to measure T3)
    f = myproto() #create a probe packet object
    e = pkt.ethernet() #create L2 type packet (frame) object
    e.src = EthAddr(src_mac)
    e.dst = EthAddr(dst_mac)
    e.type=0x5577 #set unregistered EtherType in L2 header type field, here assigned to the probe packet type 
    msg = of.ofp_packet_out() #create PACKET_OUT message object
    msg.actions.append(of.ofp_action_output(port=port)) #set the output port for the packet in switch0
    f.timestamp = int(time.time()*1000*10 - start_time) #set the timestamp in the probe packet
    #print f.timestamp
    e.payload = f
    msg.data = e.pack()
    core.openflow.getConnection(src_dpid).send(msg)
    #print "=====> probe sent: f=", f.timestamp, " after=", int(time.time()*1000*10 - start_time), " [10*ms]"

  #the following executes only when a connection to 'switch1' exists (otherwise AttributeError can be raised)
  if dst_dpid <>0 and not core.openflow.getConnection(dst_dpid) is None:
    #send out port_stats_request packet through switch1 connection dst_dpid (to measure T2)
    core.openflow.getConnection(dst_dpid).send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    sent_time2=time.time() * 1000*10 - start_time #sending time of stats_req: ctrl => switch1
    #print "sent_time2:", sent_time2

  return sent_time1, sent_time2

def _timer_func ():
  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid
  global start_time, sent_time1, sent_time2, sent_time3, sent_time4, sent_time5, sent_time6
  
  sent_time1, sent_time2 = measure_delay(s1_dpid, s2_dpid, "0:1:0:0:0:4", "0:2:0:0:0:1", 4)
  sent_time3, sent_time4 = measure_delay(s1_dpid, s3_dpid, "0:1:0:0:0:5", "0:3:0:0:0:1", 5)
  sent_time5, sent_time6 = measure_delay(s1_dpid, s4_dpid, "0:1:0:0:0:6", "0:4:0:0:0:1", 6)
  

def _handle_portstats_received (event):
  #Observe the handling of port statistics provided by this function.
  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid
  global s2_p1, s3_p1, s4_p1
  global pre_s2_p1, pre_s3_p1, pre_s4_p1
  global OWD1, OWD2, OWD3, OWD4

  received_time = time.time() * 1000*10 - start_time
  #measure T1 as of lab guide
  if event.connection.dpid == s1_dpid:
    OWD1=0.5*(received_time - sent_time1)
 
  #measure T2 as of lab guide
  elif event.connection.dpid == s2_dpid:
    OWD2=0.5*(received_time - sent_time2)
  
  elif event.connection.dpid == s3_dpid:
    OWD3=0.5*(received_time - sent_time4)
  
  elif event.connection.dpid == s4_dpid:
    OWD4=0.5*(received_time - sent_time6)
 
  if event.connection.dpid==s2_dpid:
    for f in event.stats:
      if int(f.port_no)<65534:
        if f.port_no==1:
          pre_s2_p1=s2_p1
          #s2_p1=f.rx_packets
          s2_p1=f.rx_bytes
          congestion = s2_p1 - pre_s2_p1
          links["s1-s2"].congestion = congestion
    #print getTheTime(), "s2_p1(Received):", congestion
 
  if event.connection.dpid==s3_dpid:
    for f in event.stats:
      if int(f.port_no)<65534:
        if f.port_no==1:
          pre_s3_p1=s3_p1
          #s3_p1=f.rx_packets
          s3_p1=f.rx_bytes
          congestion = s3_p1 - pre_s3_p1
          links["s1-s3"].congestion = congestion
    #print getTheTime(), "s3_p1(Received):", congestion

  if event.connection.dpid==s4_dpid:
    for f in event.stats:
      if int(f.port_no)<65534:
        if f.port_no==1:
          pre_s4_p1=s4_p1
          #s4_p1=f.rx_packets
          s4_p1=f.rx_bytes
          congestion = s4_p1 - pre_s4_p1
          links["s1-s4"].congestion = congestion
    #print getTheTime(), "s4_p1(Received):", congestion

def _handle_ConnectionUp (event):
  # waits for connections from all switches, after connecting to all of them it starts a round robin timer for triggering h1-h4 routing changes
  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid, network_ready
  print "ConnectionUp: ",dpidToStr(event.connection.dpid)
 
  #remember the connection dpid for the switch
  for m in event.connection.features.ports:
    if m.name == "s1-eth0":
      # s1_dpid: the DPID (datapath ID) of switch s1;
      s1_dpid = event.connection.dpid
      print "s1_dpid=", s1_dpid
    elif m.name == "s2-eth0":
      s2_dpid = event.connection.dpid
      print "s2_dpid=", s2_dpid
    elif m.name == "s3-eth0":
      s3_dpid = event.connection.dpid
      print "s3_dpid=", s3_dpid
    elif m.name == "s4-eth0":
      s4_dpid = event.connection.dpid
      print "s4_dpid=", s4_dpid
    elif m.name == "s5-eth0":
      s5_dpid = event.connection.dpid
      print "s5_dpid=", s5_dpid
 
  # start 1-second recurring loop timer for round-robin routing changes; _timer_func is to be called on timer expiration to change the flow entry in s1
  if s1_dpid<>0 and s2_dpid<>0 and s3_dpid<>0 and s4_dpid<>0 and s5_dpid<>0:
    network_ready = True
    Timer(1, _timer_func, recurring=True)

def calculate_delay(received_time, d, OWD1, OWD2, link_name):
    global links
    delay_c = int((received_time - d - OWD1 - OWD2) / 10)
    links[link_name].delay_hist.append(delay_c)
    links[link_name].delay = sum(links[link_name].delay_hist[-2:]) / 2

flag = 0

def setPath(dpid, srcIP, dstIP, port):
  if dpid<>0:
    msg = of.ofp_flow_mod()
    msg.command=of.OFPFC_MODIFY_STRICT
    msg.priority = 100
    msg.idle_timeout = 0
    msg.hard_timeout = 0
    msg.match.dl_type = 0x0800
    msg.match.nw_dst = str(dstIP)
    #msg.match.nw_src = str(srcIP)
    msg.actions.append(of.ofp_action_output(port = port+2))
    core.openflow.getConnection(dpid).send(msg)

def _handle_PacketIn(event):
  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid
  
  global start_time, OWD1, OWD2, links, flag

  received_time = time.time() * 1000*10 - start_time #amount of time elapsed from start_time

  packet = event.parsed
  #print packet
  
  if packet.type == 0x5577:
    flag += 1
    c = packet.find('ethernet').payload
    d, = struct.unpack('!I', c)
  
    if event.connection.dpid == s2_dpid:
      calculate_delay(received_time, d, OWD1, OWD2, "s1-s2")
    elif event.connection.dpid == s3_dpid:
      calculate_delay(received_time, d, OWD1, OWD3, "s1-s3")
    elif event.connection.dpid == s4_dpid:
      calculate_delay(received_time, d, OWD1, OWD4, "s1-s4")

    if flag%3 == 0:
      sorted_delays = sorted(links.items())
      print "delay " + ' | '.join("{}: {:<3} [ms]".format(link_name, delay_value.delay) for link_name, delay_value in sorted_delays)  
  
  #print "_handle_PacketIn is called, packet.type:", packet.type, " event.connection.dpid:", event.connection.dpid

  # Below, set the default/initial routing rules for all switches and ports.
  # All rules are set up in a given switch on packet_in event received from the switch which means no flow entry has been found in the flow table.
  # This setting up may happen either at the very first pactet being sent or after flow entry expirationn inn the switch
 
  if event.connection.dpid==s1_dpid:
     a=packet.find('arp')					# If packet object does not encapsulate a packet of the type indicated, find() returns None
     if a and a.protodst=="10.0.0.4":
       msg = of.ofp_packet_out(data=event.ofp)			# Create packet_out message; use the incoming packet as the data for the packet out
       msg.actions.append(of.ofp_action_output(port=4))		# Add an action to send to the specified port
       event.connection.send(msg)				# Send message to switch
 
     if a and a.protodst=="10.0.0.5":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=5))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.6":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=6))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.1":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=1))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.2":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=2))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.3":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=3))
       event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800		# rule for IP packets (x0800)
     msg.match.nw_dst = "10.0.0.1"
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.2"
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.3"
     msg.actions.append(of.ofp_action_output(port = 3))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 1
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.4"
     msg.actions.append(of.ofp_action_output(port = 4))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.5"
     msg.actions.append(of.ofp_action_output(port = 5))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.6"
     msg.actions.append(of.ofp_action_output(port = 6))
     event.connection.send(msg)
 
  elif event.connection.dpid==s2_dpid: 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0806		# rule for ARP packets (x0806)
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
  
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0806
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
  elif event.connection.dpid==s3_dpid: 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0806
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
  
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0806
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
  
  elif event.connection.dpid==s4_dpid: 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0806
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 1
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
  
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0806
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 2
     msg.match.dl_type=0x0800
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
  elif event.connection.dpid==s5_dpid: 
     a=packet.find('arp')
     if a and a.protodst=="10.0.0.4":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=4))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.5":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=5))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.6":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=6))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.1":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=1))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.2":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=2))
       event.connection.send(msg)
 
     if a and a.protodst=="10.0.0.3":
       msg = of.ofp_packet_out(data=event.ofp)
       msg.actions.append(of.ofp_action_output(port=3))
       event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.1"
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =10
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.in_port = 6
     msg.actions.append(of.ofp_action_output(port = 3))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.1"
     msg.actions.append(of.ofp_action_output(port = 1))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.2"
     msg.actions.append(of.ofp_action_output(port = 2))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.3"
     msg.actions.append(of.ofp_action_output(port = 3))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.4"
     msg.actions.append(of.ofp_action_output(port = 4))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.5"
     msg.actions.append(of.ofp_action_output(port = 5))
     event.connection.send(msg)
 
     msg = of.ofp_flow_mod()
     msg.priority =100
     msg.idle_timeout = 0
     msg.hard_timeout = 0
     msg.match.dl_type = 0x0800
     msg.match.nw_dst = "10.0.0.6"
     msg.actions.append(of.ofp_action_output(port = 6))
     event.connection.send(msg)

def read_req_conn(file_path):
  try:
      with open(file_path, 'r') as file:
          data = json.load(file)
          return data.get('connections', [])
  except IOError:
      print "Error: File '%s' not found." % file_path
      return []

req_conn = []
MAX_CONNECTIONS_PER_LINK = 3

def find_matching_link():
  global links, req_conn, s1_dpid, s5_dpid, network_ready, MAX_CONNECTIONS_PER_LINK
  if not network_ready:
    print "could not set path"
    return

  total_congestion = float(links["s1-s2"].congestion + links["s1-s3"].congestion + links["s1-s4"].congestion) / 100
  if total_congestion<>0:
    links["s1-s2"].congestion = links["s1-s2"].congestion / total_congestion
    links["s1-s3"].congestion = links["s1-s3"].congestion / total_congestion
    links["s1-s4"].congestion = links["s1-s4"].congestion / total_congestion
    print "congestion: %.2f, %.2f, %.2f" % (links["s1-s2"].congestion, links["s1-s3"].congestion, links["s1-s4"].congestion)
  else:
    print "congestion: ", 0, 0, 0

  sorted_links = sorted(links.values(), key=lambda link: link.delay, reverse=True)
  for link in sorted_links: 
    link.connection = []

  print "path for:",
  paths = []
  links_choosen = []
  for node in req_conn:
    src = node["src"]
    dst = node["dst"]
    min_delay = node["min_delay"]

    paths.append(src + "<->" + dst)
    matching_path_found = False

    for link in sorted_links:
      if link.delay <= min_delay * 1.2 and len(link.connection) < MAX_CONNECTIONS_PER_LINK:
        matching_path_found = True
        link.connection.append(node)
        links_choosen.append(link.name)
        link_port = int(link.name.split("-")[1][1:])
        dstIP = "10.0.0." + dst[1:]
        srcIP = "10.0.0." + src[1:]
        setPath(s1_dpid, srcIP, dstIP, link_port)
        setPath(s5_dpid, dstIP, srcIP, link_port-3)
        break

    if not matching_path_found:
      links_choosen.append("None")

  for path, link in zip(paths, links_choosen):
    print path, link + " | ",
  
  print ""
  # Load redistribution if a link is congested
  congested_link = None
  for link in sorted_links:
    if link.congestion > 85:
      congested_link = link
      break

  if congested_link:
    available_links = [link for link in sorted_links if link != congested_link]
    if available_links:
      for conn in congested_link.connection:
        src = conn["src"]
        dst = conn["dst"]
        min_delay = conn["min_delay"]
        for link in available_links:
          if link.delay <= min_delay * 1.2 and link.connection < MAX_CONNECTIONS_PER_LINK:
            print "reasign"
            congested_link.connection -= 1
            link.connection += 1
            link_port = int(link.name.split("-")[1][1:])
            dstIP = "10.0.0." + dst[1:]
            srcIP = "10.0.0." + src[1:]
            setPath(s1_dpid, srcIP, dstIP, link_port)
            setPath(s5_dpid, dstIP, srcIP, link_port - 3)
            break
    

def launch ():
  global start_time, req_conn
  start_time = time.time() * 1000*10 # factor * 10 applied to increase the accuracy for short delays (capture tenths of ms)
  print "start:", start_time/10

  conn_req_path = "/home/student/Desktop/projekt/conn_req_parralel.json"
  print "loading requested connections data from file", conn_req_path

  req_conn = read_req_conn(conn_req_path)
  print "Requested connections:"
  Timer(1, find_matching_link, recurring=True)
  for node in req_conn:
    print "\t",node

  core.openflow.addListenerByName("PortStatsReceived",_handle_portstats_received)
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
  

  
