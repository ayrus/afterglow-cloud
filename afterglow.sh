#!/bin/sh

###
# This shell script invokes AfterGlow [1] with the settings given as arguments
# and generates a GIF graph image of the resulting output from Afterglow; using
# neato [2]. 
#
# Usage:
# 	afterglow.sh "path_to_csv_file" "path_to_colour_property_file" 
#				"path_to_resulting_output_file" "path_to_afterglow.pl" "arguments"
#
# Note: Paths can be absolute or relative.
# 		For a list of 'arguments' please see [1].
#
# Example usage: ./afterglow.sh data/firewall.csv sample.properties images/firewall.gif afterglow/src/afterglow.pl -d -e 1.5
#
# Exit status:
#	0: On successful image creation.
#	1: Error creating an output image.
#	2: No valid data file supplied.
#	3: No valid property file supplied.
#	4: Perl is not installed $PATH.
#	5: Neato [2] is not installed $PATH.
#	6: Afterglow.pl [1] is not present.
#
# References:
#	[1] http://afterglow.sourceforge.net/
# 	[2] http://www.graphviz.org/Documentation.php
###

#Path to a CSV data file.
dataFile="$1"
	shift

#Path to a colour property file (if any).
propertyFile="$1"
	shift

#Path to create the output file, including its name and extension.
outputFile="$1"
	shift

#Complete path to afterglow.pl, including its name and extension.
afPath="$1"
	shift

#Additional parameters (if any) to be passed to AfterGlow.
args="$@"

#Sanitize inputs -- Check if datafile is present.
	if [ ! -e "$dataFile" ]
	then
		echo "No valid data file." >&2
		exit 2
	fi

#Check if property file is valid.
	if [ ! -e "$propertyFile" ]
	then
		echo "No valid property file." >&2
		exit 3
	fi

#Check if perl is installed anywhere on $PATH.
	out=`which perl`
	if [ $? -eq 1 ]
	then
		echo "Perl seems to be missing." >&2
		exit 4
	fi

#Check if neato is installed anywhere on $PATH.
	out=`which neato`
	if [ $? -eq 1 ]
	then
		echo "Neato seems to be missing." >&2
		exit 5
	fi
	
#Check if afterglow.pl is present.
	if [ ! -e "$afPath" ]
	then
		echo "Afterglow.pl is not present in the directory given." >&2
		exit 6
	fi

#Everything looks good for now; render the graph.
perl "$afPath" -i "$dataFile" -c "$propertyFile" $args | neato -Tgif -o "$outputFile"

#Check if the output was successfuly rendered and that the output file is
#more than 0 bytes in size.
	if [ -s "$outputFile" ]
	then
		exit 0	
	else
		echo "Error creating an output image." >&2
		exit 1
	fi
