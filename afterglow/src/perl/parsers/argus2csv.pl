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
# Title: 	Argus 2 CSV
#
# File: 	argus2csv.pl
#
# Version: 	1.1
#
# Description:	Takes a argus output and parses it into a csv output.
#
# Usage:	ragator -r file.argus -nn -A -s +dur -s +sttl -s +dttl | ./argus2csv.pl ["field list"]
#
# Possible fields:
# 		time  proto  src  dir  count  status  dur  
# 		dst  sport  dport  sttl  dttl  bytes  pkts
#
# Known Issues:
#
# URL:		http://afterglow.sourceforge.net
#
# Changes:	
# 
# 04/10/06	Initial Version by ram
# 06/06/07	Fixed parsing. Probably a new version of argus change output
#
###############################################################################/

use strict vars;

# 10 Apr 06 10:55:46  *        tcp  217.118.195.58.22     ?>     65.219.2.99.37065 1280     1550      309440       23952       RST    10762    64    255
# 10 Apr 06 10:55:47             0 0:d0:58:fb:81:8 0x4    ->     1:80:c2:0:0:0 0x4 30       0         1290         0           INT       58     0      0

# Rest is really optional! You don't need to run it with the -s options!
# 10 Apr 06 10:55:46  *        tcp  217.118.195.58.22     ?>     65.219.2.99.37065 1280     1550      309440       23952       RST
# 10 Apr 06 10:55:47             0 0:d0:58:fb:81:8 0x4    ->     1:80:c2:0:0:0 0x4 30       0         1290         0           INT
# 05-26-04 13:20:47.193178          2054                 192.12.5.171          who-has                 192.12.5.192          1        0         18           0           INT        0.000000     0      0


my $output=$ARGV[0] || "full";

my $DEBUG=1;

our ($timestamp,$foo,$dip,$sip,$sttl,$dttl,$proto,$dir,$spkts,$dpkts,$sbytes,$dbytes,$sport,$dport,$duration,$status,$smac,$dmac);

while (<STDIN>) {
	chomp;
	my $input = $_;

	if ($input =~ /^(\d+ \S+ \d+ \d+:\d+:\d+|\d+-\d+-\d+ \d+:\d+:\d+.\d+) \s*(.*?)(?:\s*(\S+))? \s*(\d+\.\d+\.\d+\.\d+)(?:.(\d+))? \s*(\S+)\s* (\d+\.\d+\.\d+\.\d+)(?:.(\d+))?\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\S+)\s*(\S+)\s*(\d+)\s*(\d+)/) {
		# normal packet
		$timestamp = $1;
		$foo=$2;
		$proto=$3;
		$sip=$4;
		$sport=$5 || "";
		$dir=$6;
		$dip=$7;
		$dport=$8 || "";
		$spkts=$9;
		$dpkts=$10;
		$sbytes=$11;
		$dbytes=$12;
		$status=$13;
		$duration=$14;
		$sttl=$15;
		$dttl=$16;
	} elsif ($input =~ /^(\d+ \S+ \d+ \d+:\d+:\d+|\d+-\d+-\d+ \d+:\d+:\d+.\d+) \s*(.*?)(?:\s*(\S+))? \s*(\S+:\S+:\S+:\S+:\S+:\S+)(?: \s*(\S+))? \s*(\S+)\s* (\S+:\S+:\S+:\S+:\S+:\S+) \s*(\S+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\S+)\s*(\S+)\s*(\d+)\s*(\d+)/) {
		$timestamp = $1;
		$foo=$2;
		$proto=$3;
		$smac=$4;
		# what is this? $=$5;
		$dir=$6;
		$dmac=$7;
		# what is this? $=$8;
		$spkts=$9;
		$dpkts=$10;
		$sbytes=$11;
		$dbytes=$12;
		$status=$13;
		$duration=$14;
		$sttl=$15;
		$dttl=$16;
	} else {
		$DEBUG && print STDERR "ERROR: $input\n";
		next;
	}

	# some sanitization
	
	if ($output eq "full") {
		print "$timestamp $sip $dip $sport $dport $proto $sttl $dttl \n";
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

