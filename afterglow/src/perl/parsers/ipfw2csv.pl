#!/usr/bin/perl
#
# Copyright (c) 2007 by Raffael Marty
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
# Title: 	IPFW2CSV
#
# File: 	ipfw2csv.pl
#
# Version: 	1.0
#
# Description:	Takes an ipfw firewall log from Mac OSX and parses it into a csv output.
#
# Usage:	cat /var/log/ipfw.log | ./ipfw2csv.pl ["field list"]
#
# Possible fields:
# 		timestamp  sip  dip  sport  dport  direction  interface  action
# 		rest  rulenumber proto  app (contains ICMP type and code)
#
# URL:		http://afterglow.sourceforge.net
#
# Changes:	
# 
# 08/04/07	Initial Version by ram, writte during DefCon 0x0f
#
###############################################################################/

use strict vars;

my $output=$ARGV[0] || "full";

# whether reverse should be done
my $reverse=0;

my $DEBUG=1;

# Aug  2 18:59:38 ram ipfw: Stealth Mode connection attempt to TCP 70.165.138.163:56266 from 89.139.144.18:80
# Aug  2 19:00:14 ram ipfw:  35000 Deny UDP 218.175.227.60:35319 70.165.138.163:55118 in via en0

our ($rulenumber,$action,$direction,$interface,$sip,$sport,$dip,$dport,$timestamp,$rest,$proto,$app,$len,$ack,$seq,$reversed);

while (<STDIN>) {
	chomp;
	$proto = undef; $rest = undef; 
	$reversed="";

	my $input = $_;

	($timestamp, $rulenumber, $action, $proto, $dip, $dport, $sip, $sport, $direction, $interface, $rest) = 
		$input =~ /^(.* \d{2}:\d{2}:\d{2}).*? (\d+) (Deny|Allow) (UDP|TCP) ([^:]*):(\d+) ([^:]*):(\d+) (in|out) via ([^\s]+)(.*)/;
		
	if (!$timestamp) {
		($timestamp, $action, $proto, $sip, $sport, $dip, $dport,$rest) = 
			$input =~ /^(.* \d{2}:\d{2}:\d{2}).*? Stealth Mode connection (attempt) to (UDP|TCP) ([^:]*):(\d+) from ([^:]*):(\d+)(.*)/;
	}

	if (!$timestamp) {
		($timestamp, $rulenumber, $action, $proto, $app,$sip, $dip, $direction, $interface ,$rest) = 
			$input =~ /^(.* \d{2}:\d{2}:\d{2}).*? (\d+) (Deny|Allow) (ICMP):([^ ]*) ([^ ]*) ([^ ]*) (out|in) via ([^\s])*\s*(.*)/;
	}

	if (!$timestamp) {
		$DEBUG && print STDERR "ERROR: $input\n";
		next;
	}

	# subparsing
	
	# doing some server -> client heuristics...
	if ($reverse) {
		if ( ($sport < 1024) && ($dport > 1024) ) {
			# reverse
			($sport,$dport)=($dport,$sport);
			($sip,$dip)=($dip,$sip);
			$reversed = "R";
			$DEBUG && print STDERR "reversed $sport $dport\n";
		}
	}

	if ($output eq "full") {
		print "$timestamp,$rulenumber,$action,$direction,$interface,$sip,$sport,$dip,$dport,$proto,$app,$direction,$rest\n";
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
