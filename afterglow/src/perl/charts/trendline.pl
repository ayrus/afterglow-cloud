#!/usr/bin/perl
use perlchartdir;
#use strict;

my $filename="trend.png";
my $title="";
my $print=0;
my $logScale=0;
my $trendLine=0;
my $seriesLabel=0;
my $confidence=0;
my $bar=0;

&init;

my @labels;
my @series;
my $max;
# input: label,series1,...,seriesn
while (<STDIN>) {
	chomp;
	my @input=split/,/;
	push @labels,shift @input;
	my $i=0;
	foreach my $in (@input) {
		my $var = "series$i";
		push @$var, $in;	
		$i++;
	}
	if ($max<$i) { $max = $i; }

}

if ($print) {
	print join("\n",@labels);
}

my $c = new XYChart(600, 300);
$c->setPlotArea(45, 45, 500, 200, 0xffffff, -1, 0xffffff, $perlchartdir::Transparent, $perlchartdir::Transparent);
$c->addTitle($title, "arialb.ttf", 14);
$c->xAxis()->setWidth(1);
$c->yAxis()->setWidth(1);
if ($logScale) {$c->yAxis()->setLogScale();}
$c->xAxis()->setLabels(\@labels);
if ($seriesLabel) {
	$c->addLegend(50, 30, 0, "arialbd.ttf", 9)->setBackground($perlchartdir::Transparent);
}

my $layer;
if ($bar) {
	$layer = $c->addBarLayer();
	$layer->setBorderColor($perlchartdir::Transparent);
	$layer->setBarGap(0.1);
} else { 
	$layer = $c->addLineLayer();
	$layer->setLineWidth(1);
}
for (my $n=0; $n<$max; $n++) {
	my $var = "series$n";
#	print STDERR join "/",@$var;

	# for some reason the array is overwritten, so need a copy
	my @series=@$var;
	my $label1="Line ".$n; 
	my $trendLabel="Trend ".$n;
	if ($trendLine) { 
		my $layer = $c->addTrendLayer(\@$var, 0xcccccc, $trendLabel);
		$layer->setLineWidth(1); 
		if ($confidence) {
			$layer->addConfidenceBand(0.95, 0x80666666); 
		}
	}
	$layer->addDataSet(\@series, 0xcccccc, $label1)->setDataSymbol($perlchartdir::SquareSymbol, 7);
}

$c->makeChart($filename);

exit;

sub init() {
    my %opt;
    use Getopt::Std;
    getopts("abchlpsf:t:", \%opt ) or usage();

    # Help?
    usage() if $opt{h};
    
    $filename = $opt{f} if $opt{f};
    $title = $opt{t} if $opt{t};
    $print = 1 if $opt{p};
    $logScale = 1 if $opt{l};
    $trendLine = 1 if $opt{a};
    $confidence = 1 if $opt{c};
    $seriesLabel = 1 if $opt{s};
    $bar = 1 if $opt{b};
}

sub usage() {

    print STDERR << "EOF";

Usage: cat file.csv | trendline.pl [-abchlps] -f outputfile [-t title]");

-a	     : show trend line
-b	     : use a bar chart instead of a line chart
-c	     : plot confidence band
-f	     : output file name, ending in .PNG
-h           : this (help) message
-l	     : use log scale on y-axis
-p           : print the labels
-s	     : show series label
-t	     : chart title

EOF
    exit;
}
    


