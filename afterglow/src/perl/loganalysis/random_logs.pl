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
# Written by:	Raffael Marty (ram@secviz.org)
#
# Version:	1.0
#
# URL:		http://afterglow.sourceforge.net
#
# Sample Usage:
# 		random_logs.pl -1 file1.csv -2 file2.csv -n 100
#
# Purpose:
# 		The tool takes two files and chooses entries from each
# 		to make up random combinations
#
# ChangeLog:	
#
# 1.0		Initial Version 03/20/07
#	
##############################################################

use strict;

# ------------------------------------------------------------
# Main program.
# ------------------------------------------------------------

# Program version
my $version = "1.0";

# default amount of output lines to generate
my $lines=100;

# keep array of entries
my @first;
my @second;

# The input files
my $firstFile;
my $secondFile;

# number of lines to read
my $nOfFirst;
my $nOfSecond;

# entropies
my $entropyOne = 1;
my $entropyTwo = 1;

# Process commandline options.
&init;

# Load first file

open(FILE1,"<$firstFile");
my $line=0;
while ((my $line=<FILE1>) && (($nOfFirst==0) || ($line++ <= $nOfFirst)) ) {
	chomp $line;
	#$line=~s/([^,]*).*/\1/;
	push(@first,$line);
}
close(FILE1);

$line=0;
open(FILE2,"<$secondFile");
while ((my $line=<FILE2>) && (($nOfSecond==0) || ($line++ <= $nOfSecond)) ) {
	chomp $line;
	#$line=~s/([^,]*).*/\1/;
	push(@second,$line);
}
close(FILE2);

for (my $i=1; $i<=$lines; $i++) {
	# generate random combinations;
	# print $first[int(rand($#first))].",".$second[int(rand($#second))]."\n";
	# print $first[int((rand()**$entropyOne)*$#first)].",".$second[int((rand()**$entropyTwo)*$#second)]."\n";
	use Math::Trig;
	#my $e1 = abs(sin(rand()*6))*$#first;
	my $e1 = ((rand()+0.5)**$entropyOne)*$#first;
	if (int($e1)>$#first) { $e1 = $#first; }
	print $first[int($e1)].",".$second[int((rand()**$entropyTwo)*$#second)]."\n";
}

# Command line options processing.
sub init() {
    my %opt;
    use Getopt::Std;
    getopts("hn:1:2:a:b:q:r:", \%opt ) or usage();

    usage() if ((!$opt{1}) || (!$opt{2}));

    # Help?
    usage() if $opt{h};

    # Prefix
    $lines = $opt{n} if $opt{n};

    $firstFile = $opt{1}; 
    $secondFile = $opt{2}; 

    $nOfFirst = $opt{a} if $opt{a};
    $nOfSecond = $opt{b} if $opt{b};

    $entropyOne = $opt{q} if $opt{q};
    $entropyTwo = $opt{r} if $opt{r};
}

# Message about this program and how to use it.
sub usage() {

    print STDERR << "EOF";

AfterGlow - Random Merge $version ---------------------------------------------------------------
    
A tool to merge two files by randomly picking entries from either file and combining them.
If multiple columns are in a file, only the first one will be used.
    
Usage:   random_logs.pl [-h] [-n count] [-a count] [-b count] [-q count] [-r count] -1 file1.csv -2 file2.csv 

-h           : this (help) message
-n count     : number of output lines to generate. Default 100
-1 file      : first file
-2 file	     : second file
-a count     : number of lines to read from first file
-b count     : number of lines to read from second file
-q count     : bias for first file
-r count     : bias for second file

EOF
    exit;
}

