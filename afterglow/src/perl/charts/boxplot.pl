#!/usr/bin/perl
use perlchartdir;
use strict;

my $filename;
my $title;
my $smaller=0;
my $print=0;
my $logScale=0;

&init;

my %labels;
my (@max,@min,@avg,@firstQ,@thirdQ);
while (<STDIN>) {
	my ($k,$v);
	chomp;
	($k,$v)=split/,/;
	if (($smaller>0) && ($smaller>$v)) { next; }
	my @temp;
	if (defined($labels{$k})){ @temp=@{$labels{$k}};}
	push @temp,$v;
	$labels{$k}=[ @temp ];
}

# calculate min,max,avg
my @labelsA = sort {$a <=> $b} keys %labels;
for my $key (@labelsA) {
	my @values = @{$labels{$key}};		
	my $i=1;
	my $sum=0;
	#print "key: $key\n";
	for my $value (sort {$a <=> $b} @values) {
		#print "value: ".$value."\n";
		$sum+=$value;
		if ($i==1) {
			#print STDERR "$value\n";
			push (@min,$value);
		}
		if ($i==int($#values/4)+1) {
			#print "$value\n";
			push (@firstQ,$value);
		}
		if ($i==int($#values/4*3)+1) {
			#print "$value\n";
			push (@thirdQ,$value);
		}
		if ($i==int($#values/2)+1) {
			#print "$value\n";
			push (@avg,$value);
		}
		if ($i==$#values+1) {
			#print STDERR "$value\n";
			push (@max,$value);
		}
		$i++
	}
	my $avg=$sum/$i;
	#print STDERR "$avg\n";

}

#if ($topN>0) {
#@twoD = @twoD[0..$topN-1];
#}

#my @data = map $_->[ 1 ], @twoD;

if ($print) {
	print join("\n",@labelsA);
}

my $c = new XYChart(800, 800,0xffffff,-1,-1);
$c->swapXY(1);
$c->setPlotArea(200, 45, 650, 700, 0xffffff, -1, 0xffffff, $perlchartdir::Transparent, $perlchartdir::Transparent);
$c->addTitle($title, "arialb.ttf", 14);
$c->xAxis()->setLabels(\@labelsA); 
if ($logScale) {$c->yAxis()->setLogScale();}
$c->xAxis()->setColors($perlchartdir::Transparent, 0);

$c->addBoxWhiskerLayer(\@firstQ, \@thirdQ, \@max, \@min, \@avg, 0xAAAAAA,0x222222)->setLineWidth(2);

#$layer->setBorderColor($perlchartdir::Transparent);
#$layer->setBarGap(0.1);

$c->makeChart($filename);

exit;

sub init() {
    my %opt;
    use Getopt::Std;
    getopts("hlpf:n:t:", \%opt ) or usage();

    # Help?
    usage() if $opt{h};
    $filename="boxplot.png";
    
    $filename = $opt{f} if $opt{f};
    $title = $opt{t} if $opt{t};
    $smaller = $opt{n} if $opt{n};
    $print = 1 if $opt{p};
    $logScale = 1 if $opt{l};
}

sub usage() {

    print STDERR << "EOF";

Usage: cat file.csv | boxplot.pl [-hlp] -f outputfile [-t title] [-n value]");

-f	     : output file name, ending in .PNG
-h           : this (help) message
-l	     : use log scale on y-axis
-n           : only show the entries with x values smaller than x
-p           : print the labels
-t	     : chart title

EOF
    exit;
}
    

