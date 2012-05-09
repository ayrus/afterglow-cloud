#!/usr/bin/perl
#
# Copyright (c) 2006 by Raffael Marty and Chrisitan Beedgen
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
# Version:	1.1
#
# URL:		http://afterglow.sourceforge.net
#
# Sample Usage:
# 		cat log.csv | anonymize.pl -c 2 -p user 	
#
# Requirements:
# 		Crypto::Rijnadal
# 			sudo apt-get install libcrypt-rijndael-perl
#
# ChangeLog:	
#
# 1.0		Initial Version 02/04/07
# 1.1		Fixes to not require prefix input
#		Parsing was totally broken too
#	
##############################################################

use strict;

# ------------------------------------------------------------
# Main program.
# ------------------------------------------------------------

# Program version
my $version = "1.1";

use Text::CSV;
my $csvline = Text::CSV->new();

my $prefix = "";
my $column = 0;

# keep hash of fields
my %value;

# Process commandline options.
&init;

my $currentVal = 1;

my $firstline = 1; 
my $obj;

# Read each line from the file.
while (my $line = <STDIN>) {
    
    $csvline->parse($line);
    my @fields = $csvline->fields;

    # Auto detect IP Addrsses
    if ($fields[$column] =~ /^\d{1,3}(?:\.\d{1,3}){3}$/) {

	if ($firstline) {
	    use IP::Anonymous;
	    # initialize IP::Anonymous
	    my @key = (2,3,30,31,43,5,6,7,8,9,10,11,12,13,14,15, 16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31); 
	    $obj = new IP::Anonymous(@key);
	} 
	
	$fields[$column] = $obj->anonymize($fields[$column]);

    } else {

	    my $number = $value{$fields[$column]} || $currentVal;
	    # add only if it was not there yet
	    if ($number eq $currentVal) {$value{$fields[$column]}=$currentVal++;}

	    $fields[$column] = $prefix.$number;
    }

    $firstline = 0;

    $csvline->combine(@fields); 
    print $csvline->string()."\n";

}

# Command line options processing.
sub init() {
    my %opt;
    use Getopt::Std;
    getopts("hc:p:", \%opt ) or usage();

    # Help?
    usage() if $opt{h};

    # check required params
    usage() if (!$opt{c});
    
    # Prefix
    $prefix = $opt{p} if $opt{p};

    # Column
    $column = $opt{c} - 1 if $opt{c};

}

# Message about this program and how to use it.
sub usage() {

    print STDERR << "EOF";

AfterGlow - Anonymize $version ---------------------------------------------------------------
    
A tool to anonymize columns in a CSV file.
    
Usage:   anonymize.pl -c column [-p prefix] [-h]

-h           : this (help) message
-c column    : indicate the column that should be anonymized [starting with one!]
-p prefix    : prefix to use for anonymization

Example: cat log.csv | anonymize.pl -c 2 -p user 

This will replace all the values in the second column with usernames of the form: "userX".

EOF
    exit;
}

