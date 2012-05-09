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
# Version:	1.5
#
# URL:		http://afterglow.sourceforge.net
#
# Sample Usage:
# 		merge_logs.pl file1.csv file2.csv 
#
# Purpose:
# 		The tool takes two files. The first one defines a 
# 		lookup table. The second one is a CSV file. If a value
# 		from the lookup table shows up in the second file, 
# 		a third column is appended with the 'value' field
# 		from the lookup file
#
# ChangeLog:	
#
# 1.0		Initial Version 03/24/07
# 1.5		Introduce capability to either append or overwrite
# 		the looked up information
#	
##############################################################

use strict;

# ------------------------------------------------------------
# Main program.
# ------------------------------------------------------------

# Program version
my $version = "1.5";

# keep array of entries
my @lookup;

# The input files
my $lookupFile;
my $file;

# Overwrite?
my $overwrite=0;

# Process commandline options.
&init;

# Load lookup file

open(FILE1,"<$lookupFile") || die "Lookup file not found: $lookupFile\n";
my %lookupTable=();
while (<FILE1>) {
	chomp;
	my @junks = split /,/;
	$lookupTable{$junks[0]} = $junks[1];
}
close(FILE1);

open(FILE2,"<$file") || die "File not found: $lookupFile\n";;
while (<FILE2>) {
	chomp;
	my @junks = split /,/;
	my $i=0;
	# Quinton Jones says efficient code is good.
	for my $junk (@junks) {
		if ($lookupTable{$junk}) {
			if ($overwrite) {
				# overwrite
				$junks[$i]=$lookupTable{$junk};
			} else {
				# append
				$junks[$#junks+1]=$lookupTable{$junk};
			}
		} 
		$i++;	
	}

	print join (",",@junks),"\n";
}
close(FILE2);

# Command line options processing.
sub init() {
    my %opt;
    use Getopt::Std;
    getopts("ho", \%opt ) or usage();

    $lookupFile=$ARGV[0];
    $file=$ARGV[1];

    usage() if ((!$lookupFile) || (!$file));

    # Help?
    usage() if $opt{h};

    # Overwrite?
    $overwrite = 1 if $opt{o};

}

# Message about this program and how to use it.
sub usage() {

    print STDERR << "EOF";

AfterGlow - Log Merge $version ---------------------------------------------------------------
    
A tool to merge two files by using the first file as the lookup table. If entries show up in 
the second file, the lookup table is used to add an extra column with the 'value'
    
Usage:   merge_logs.pl [-ho] lookup file

-h           : this (help) message
-o	     : overwrites the entry which was looked up instead of appending it as a separate column

EOF
    exit;
}

