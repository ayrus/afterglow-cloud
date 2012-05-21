#!/bin/sh

###
# This shell script invokes AfterGlow [1] with the settings given as arguments
# and generates a GIF graph image of the resulting output from Afterglow; using
# neato [2]. 
#
# Usage:
# 	afterglow.sh "path_to_csv_file" "path_to_colour_property_file" "arguments"
#				"path_to_resulting_output_file"
#
# Note: Paths can be absolute or relative.
# 		For a list of 'arguments' please see [1].
#
# Example usage: ./afterglow.sh "data/firewall.csv" "sample.properties" "-d -e 1.5" "images/firewall.gif"
#
# The script returns 0 on success; 1 otherwise.
#
# References:
#	[1] http://afterglow.sourceforge.net/
# 	[2] http://www.graphviz.org/Documentation.php
###


#Path to a CSV data file.
dataFile="$1"

#Path to a colour property file (if any).
propertyFile="$2"

#Additional parameters (if any) to be passed to AfterGlow.
args="$3"

#Path to create the output file, including its name and extension.
outputFile="$4"


perl afterglow.pl -i "$dataFile" -c "$propertyFile" "$args" | neato -Tgif -o "$outputFile"

#Check if the output was successfuly rendered.
	if [ -e "$outputFile" ]
	then
		echo "0"	
	else
		echo "1"
	fi
