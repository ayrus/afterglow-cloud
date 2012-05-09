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
# Title: 	PFLog2CSV
#
# File: 	pf2csv.pl
#
# Version: 	1.1
#
# Description:	Takes a pf firewall log file and parses it into a csv output.
#
# Usage:	cat pflog | pf2csv.pl ["field list"]
#
# Possible fields:
# 		timestamp  dip  sip  sport  dport  direction  interface  action
# 		rest  rulenumber  proto  app  flags  len
#
# Known Issues:	Does not parse out the "rest"
#
# URL:		http://afterglow.sourceforge.net
#
# Changes:	
# 
# 02/26/06	Initial Version by ram
# 02/28/06	Take care of server vs. client inversion
# 		If rules are written such that they trigger on the response, the 
# 		log will contain the server to client packet, but in the reverse
# 		order, resulting in not so nice graphs!
# 04/15/06	Reversing should be optional. It messes things up per interface!
#		Need to expose via command line (later)
#		Setting the reversed flag if log entry got reversed.
#
###############################################################################/

use strict vars;

my $output=$ARGV[0] || "full";

# whether reverse should be done
my $reverse=1;

# per log entry, did it get reversed?

my $DEBUG=0;

#Oct 13 20:09:33.176578 rule 165/0(match): pass in on xl1: 212.254.110.99 > 62.245.245.139: icmp: echo reply (DF)
#Oct 13 20:09:39.747082 rule 97/0(match): pass in on xl0: 219.145.20.230.4707 > 212.254.110.98.25: S 1109305585:1109305585(0) win 16384 <mss 1414,nop,nop,sackOK> (DF)
#Oct 13 20:09:44.985281 rule 57/0(match): pass in on xl1: 195.141.69.45.1030 > 193.210.18.31.53:  59236 [1au] MX? minedu.fi. (38) (DF)

our ($rulenumber,$action,$direction,$interface,$sip,$sport,$dip,$dport,$timestamp,$rest,$proto,$app,$flags,$len,$ack,$seq,$reversed);
#$ttl,$tos,$id,$offset,$flags,$len,$sourcemac,$destmac,$ipflags

while (<STDIN>) {
	chomp;
	$flags = undef; $proto = undef; $rest = undef; $app = undef; $len = undef;
	$reversed="";

	my $input = $_;

	if ($input =~ /(.*) rule ([-\d]+\/\d+)\(.*?\): (pass|block) (in|out) on (\w+): (\d+\.\d+\.\d+\.\d+)\.?(\d*) [<>] (\d+\.\d+\.\d+\.\d+)\.?(\d*): (.*)/) {
		$input = "$1|$2|$3|$4|$5|$6|$7|$8|$9|$10";
	} else {
		$DEBUG && print STDERR "ERROR: $input\n";
		next;
	}

	my @fields = split ('\|',$input);

	# some sanitization
	
	$timestamp = $fields[0];

	$rulenumber = $fields[1];
	$action = $fields[2];
	$direction = $fields[3];
	$interface = $fields[4];

	$sip = $fields[5];
	$sport = $fields[6]; 
	$dip = $fields[7];
	$dport = $fields[8]; 

	$rest = $fields[9];

	# subparsing
	
	if ($rest =~ /icmp: echo/) {
		$proto="icmp";
		if ($rest =~ /icmp: (echo \S+)(.*)/) {
			$rest=$2;
			$dport=$1;
		}
	}

	# S 2126872070:2126872070(0) win 64240 <mss 1460,nop,nop,sackOK> (DF)
	# R 0:0(0) ack 523572492 win 0 (DF)
	if ($rest =~ /^([SFP\.RU][^ ]*) ([^ ]*) (?:(ack))?(.*)/) {
		$proto="tcp";
		$flags=$1;
		$seq=$2;
		$ack=$3;
		$rest=$4;
		# print "seq: $seq ack: $ack rest: $rest\n";
	}

	# 65488 ServFail 0/0/0 (37) (DF)
	if ($rest =~ /\d+ ServFail/) {
		$proto="udp";
		$app="dns";
	}

	if ($rest =~ /udp (\d+)/) {
		$proto="udp";
		$len=$1;
	}

	# doing some server -> client heuristics...
	if ($reverse) {
		if ( ($flags eq "S") && ($sport!=20) && (!$ack) ) {
			# this is OKAY, except for ftp data connections
		} elsif (( $flags eq "S") && ($ack)) {
#			# reverse
			($sport,$dport)=($dport,$sport);
			($sip,$dip)=($dip,$sip);
			$reversed = "R";
			$DEBUG && print STDERR "reversed $sport $dport\n";
		} elsif ( ($sport < 1024) && ($dport > 1024) ) {
			# reverse
			($sport,$dport)=($dport,$sport);
			($sip,$dip)=($dip,$sip);
			$reversed = "R";
			$DEBUG && print STDERR "reversed $sport $dport\n";
		}
	}

	if ($output eq "full") {
		print "$timestamp $rulenumber $action $direction $interface $sip $sport $dip $dport $flags $proto $app $rest\n";
	} else {
		my @tokens = split / /,$output;
		print ${shift(@tokens)};
		for my $token (@tokens) {
			if (!defined($$token)) {
				$DEBUG && print STDERR "$token is not a known field\n";
				#exit;
			} else {
				print ','.$$token;
			}
		}
		print "\n";
	}
	
	
}
