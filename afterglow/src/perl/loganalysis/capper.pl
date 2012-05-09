#!/usr/bin/perl
#
# Copyright (c) 2008 by Raffael Marty
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
# Written by:	Raffael Marty (ram@secviz.org)
#
# Version:	1.0
#
##############################################################

use strict;

# Program version
my $version = "1.0";

# The input files
my $precursors;
my $user_activity;
my $watchlist;

my $adjust=0;

# Process commandline options.
&init;

# Load lookup file

open(FILE,"<$user_activity") || die "User activity file not found: $user_activity\n";
my %user_activity=();
while (<FILE>) {
	chomp;
	my @junks = split /,/;
	# user,precursor
	my $temp="";
	if (defined($user_activity{$junks[0]})) {
		$temp = $user_activity{$junks[0]}.",";
	}
	$user_activity{$junks[0]} = $temp.$junks[1];
}
close(FILE);

open(FILE,"<$precursors") || die "Precursor file not found: $precursors\n";;
my %precursor_bucket=(); 
my %precursor_score=();
while (<FILE>) {
	chomp;
	my @junks = split /,/;
	# precursor,bucket,score
	$precursor_bucket{$junks[0]} = $junks[1];
	$precursor_score{$junks[0]} = $junks[2];
}
close(FILE);

# watchlists

my %watch=(); 
if ($watchlist) {
	open(FILE,"<$watchlist") || die "Watchlist file not found: $precursors\n";;
	while (<FILE>) {
		chomp;
		my @junks = split /,/;
		$watch{$junks[0]}=$junks[1];	
	}
}

# Processing

# determine score for user first
my %buckets;
my %score;
foreach my $user (keys %user_activity) {
	my $all_activity=$user_activity{$user};
	my @all_activity=split/,/, $all_activity;
	foreach my $precursor (@all_activity) {
		$score{$user.",".$precursor_bucket{$precursor}}+=$precursor_score{$precursor};
		$buckets{$precursor_bucket{$precursor}}=1;
	}
}
		
# print all entries
foreach my $user (keys %user_activity) {
	my $all_activity=$user_activity{$user};
	my @all_activity=split/,/, $all_activity;
	foreach my $precursor (@all_activity) {
		my $total=0;
		my $fulltotal=0;
		for my $bucket (keys %buckets) {
			$fulltotal+=$score{$user.",".$bucket};
			if ($score{$user.",".$bucket}>20) {
				$score{$user.",".$bucket}=20;
			}
			$total+=$score{$user.",".$bucket};
		}
		my $pscore=$precursor_score{$precursor};
		# divide by the number of things this user did for the treemaps
		if ($adjust) {
			$total=($fulltotal / $total) * $pscore;
		}
		print "$user,$precursor,$total,$pscore,".$precursor_bucket{$precursor};

		if ($watchlist) {
			print ",".$watch{$user};
		}

		print "\n";
	}
}

# Command line options processing.
sub init() {
    my %opt;
    use Getopt::Std;
    getopts("ahu:p:w:", \%opt ) or usage();

    $user_activity=$opt{u} if $opt{u};
    $precursors=$opt{p} if $opt{p};
    $watchlist=$opt{w} if $opt{w};
    usage() if ((!$user_activity) || (!$precursors));

    # Help?
    usage() if $opt{h};

    # Help?
    $adjust=1 if $opt{a};

}

# Message about this program and how to use it.
sub usage() {

    print STDERR << "EOF";

Cap $version ---------------------------------------------------------------
    
Usage:   capper.pl [-ha] user_activity_file precursor_file 

-a           : adjust the total user score (divide by number of precursors)
-h           : this (help) message
-p           : list o the precursors, their score, and their buckets
-w	     : list of users and their watchlist

EOF
    exit;
}

