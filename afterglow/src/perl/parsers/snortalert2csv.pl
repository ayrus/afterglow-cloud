#!/usr/bin/perl
#
# Copyright (c) 2006 by Raffael Marty
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#  
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Title: 	Snort Alert Log 2 CSV
#
# File: 	snortalert2csv.pl
#
# Version: 	1.0
#
# Description:	Takes a snort alert log file and parses it into a csv output.
#
# Usage:	cat snortalert | snortalert2csv.pl ["field list"]
#
# Possible fields:
# 		timestamp  dip  sip  
#
# Known Issues:
#
# URL:		http://afterglow.sourceforge.net
#
# Changes:	
# 
# 09/12/06	Initial Version by ram
#
###############################################################################/

use strict vars;

my $output=$ARGV[0] || "full";

my $DEBUG=1;

#our ($timestamp,$etherproto,$dip,$sip,$ttl,$tos,$id,$offset,$flags,$len,$sourcemac,$destmac,$ipflags,$sport,$dport,$proto,$rest, $dnshostresponse, $dnslookup, $dnsipresponse, $dnstype, $dnslookup);
our ($timestamp,$sip,$dip,$sport,$dport,$sid,$name,$classification,$proto,$priority,$ttl,$tos,$id,$iplen,$dgmlen,$flags,$seq,$ack,$win,$tcplen);

while (<STDIN>) {
	chomp;

	# [**] [1:654:5] SMTP RCPT TO overflow [**]
	# [Classification: Attempted Administrator Privilege Gain] [Priority: 1]
	# 07/12-18:44:57.688640 213.144.137.88:3108 -> 62.2.33.102:25
	# TCP TTL:240 TOS:0x10 ID:0 IpLen:20 DgmLen:2338
	# ***AP*** Seq: 0x6E19100F  Ack: 0xA4FBB7BC  Win: 0x7DDB  TcpLen: 20
	# [Xref => http://cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2001-0260]
	# [Xref => http://www.securityfocus.com/bid/2283]

	if (/\s*\[\*\*\] \[(\S+)\] (.*) \[\*\*\]/) { ($sid,$name) = ($1,$2); }
	if (/([^ ]*) (\S+?)(?::(\d+))? -> ([^:]+)(?::(\d+))?/) { ($timestamp,$sip,$sport,$dip,$dport) = ($1,$2,$3,$4,$5); }
	if (/\[Classification: ([^\]]*) \[Priority: (\S+)\]/) { ($classification,$priority) = ($1,$2); }
	if (/(\S+) TTL:(\d+) TOS:(\S+) ID:(\d+) IpLen:(\d+) DgmLen:(\d+)/) { ($proto,$ttl,$tos,$id,$iplen,$dgmlen) = ($1,$2,$3,$4,$5,$6); }
	if (/(\S+) Seq: (\S+)  Ack: (\S+)  Win: (\S+)  TcpLen: (\d+)/) { ($flags,$seq,$ack,$win,$tcplen) = ($1,$2,$3,$4,$5); }

	if (/^$/ )  {

		if ($output eq "full") {

			#print "$timestamp $sourcemac $destmac $sip $dip $sport $dport $flags $len $proto $ttl $id $offset $tos $ipflags\n";
			print "$timestamp,$sid,$name,$sip,$dip,$sport,$dport,$proto,$classification,$priority,$ttl,$tos,$id,$iplen,$dgmlen,$flags,$seq,$ack,$win,$tcplen\n";

		} else {
			my @tokens = split / /,$output;
			print ${shift(@tokens)};
			for my $token (@tokens) {
				print ','.$$token;
			}
			print "\n";
		}

		next;

	}


}


