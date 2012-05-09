#!/usr/bin/perl -w 
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
# Title: 	Sendmail Parser for Graphing
#
# File: 	sendmail_parser.pl logfile [outputformat]
#
# Version: 	1.2
#
# Usage:	cat maillog | sendmail_parser.pl "from to" | perl afterglow.pl -t | neato -Tgif -o mailgraph.gif
#
# Known limitations:	
# 		- multiple recipients or senders are not split up into individual messages
#
# Changes:	
# 
# 06/03/05	Initial Version by ram
# 02/03/07	Version 1.2
# 		- File is not an argument anymore. Reading from STDIN
#		
###############################################################################/

# parsing lines
my $from_regex=".*? (\\S+?): from=<?(.*?)>?, size=(.*?), class=(.*?),(?: pri=(.*?),)? nrcpts=(.*?),(?: msgid=<?(.*?)>?,)? (?:bodytype=(.*?), )?(?:proto=(.*?), )?(?:daemon=(.*?), )?relay=(.*?)(?: \\[(.*?)\\])?.*?";
my $to_regex=".*? (\\S+?): to=<?(.*?)>?,(?: ctladdr=<?(.*?)>? [^,]*,)? delay=(.*?),(?: xdelay=(.*?),)? mailer=(.*?),(?: pri=(.*?),)?(?: relay=(.*?) \\[(.*?)\\],)?(?: dsn=(.*?),)? stat=([^ ]*)(?: .*)?";

($#ARGV >= 0) or die ("Wrong number of arguments!\nUsage: ./sendmail_parser.pl logfile");

my $output=$ARGV[0] || "full";

our ($to, $from, $size, $class, $pri, $msgid, $nrcpts, $bodytype, $proto, $daemon, $relay, $ctladdr, $delay);
our ($xdelay, $mailer, $pri2, $relay2, $relay2_1, $dsn, $stat);

my %messages;

while (<STDIN>) {
	chomp();
	if (my @from_array = /$from_regex/) {
		$messages{$1}=\@from_array;
	}
	elsif (/$to_regex/) {
		if ($messages{$1}) {
			my $f_array=$messages{$1};

			$from = @$f_array[1] || "";
			$to = $2 || "";
			$size = @$f_array[2] || "";
			$class = @$f_array[3] || "";
			$pri = @$f_array[4] || "";
			$nrcpts = @$f_array[5] || "";
			$msgid = @$f_array[6] || ""; 
			$bodytype = @$f_array[7] || "";
			$proto = @$f_array[8] || "";
			$daemon = @$f_array[9] || ""; 
			$relay = @$f_array[10] || "";
			$ctladdr = $3 || "";
			$delay = $4 || "";
			$xdelay = $5 || "";
			$mailer = $6 || "";
			$pri2 = $7 || "";
			$relay2 = $8 || "";
			$relay2_1 = $9 || "";
			$dsn = $10 || "";
			$stat = $11 || "";
			
			if ($output eq "full") {
				printf ("| From: %30s ",$from);
				printf ("| To: %28s ",$to);
				printf ("| relay: %5s",$relay);
				print ("\n");
				printf ("| msgid: %35s ",$msgid);
				printf ("| externalID: %10s ",$1);
				print ("\n");
				printf ("| size: %5s ",$size);
				printf ("| class: %5s ", $class);
				printf ("| pri: %5s ", $pri);
				printf ("| nrcpts: %5s ",$nrcpts);
				printf ("| bodytype: %5s ",$bodytype);
				printf ("| proto: %5s ",$proto);
				printf ("| daemon: %5s ",$daemon);
				print ("\n");
				printf ("| ctladdr: %15s ",$ctladdr);
				printf ("| delay: %15s ",$delay);
				printf ("| xdelay: %15s ",$xdelay);
				printf ("| mailer: %15s ",$mailer);
				printf ("| pri2: %15s ",$pri2);
				print ("\n");
				printf ("| relay2: %15s %15s",$relay2,$relay2_1);
				printf ("| dsn: %15s ",$dsn);
				printf ("| stat: %15s ",$stat);
				print ("\n\n");
			} else {
				my @tokens = split / /,$output;
				print ${shift(@tokens)};
				for my $token (@tokens) {
					if (!defined($$token)) {
						print STDERR "$token not a known field\n";
						exit;
					}
					print ','.$$token;
				}
				print "\n";
			}
		}

	}
	else {
		#print "mismatch: $_\n";
	}

}

