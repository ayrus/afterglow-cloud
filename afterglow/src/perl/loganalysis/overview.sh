#!/bin/bash

# the capture file
capture=$1
output=$2
properties=$3

if [ -z $capture ]; then 
	echo "Usage: overview.sh capture.pcap [output_prefix] [afterglow_propertyfile]"
	exit
fi	

if [ "x$output" = "xplain" ] ; then
	output=""
else	
	date=`date "+%Y%m%d%H%M%S"`
	output=$output_$date
fi	

tcpdump -vttttnnelr $capture | ../parsers/tcpdump2csv.pl "sip"  | ../charts/bar.pl -f ${output}_sip.png

tcpdump -vttttnnelr $capture | ../parsers/tcpdump2csv.pl "dip"  | ../charts/bar.pl -f ${output}_dip.png

tcpdump -vttttnnelr $capture | ../parsers/tcpdump2csv.pl "dport"  | ../charts/bar.pl -f ${output}_dport.png

if [ $properties ]; then 
	ap="-c $properties"
fi	

tcpdump -vttttnnelr $capture | ../parsers/tcpdump2csv.pl "sip dip"  | ../graph/afterglow.pl -t $ap | neato -Tgif -o ${output}_conns.gif

tcpdump -vttttnnelr $capture | ../parsers/tcpdump2csv.pl "sip dip dport"  | ../graph/afterglow.pl $ap | neato -Tgif -o ${output}_connservice.gif


