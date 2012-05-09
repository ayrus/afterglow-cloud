#!/usr/bin/perl
use perlchartdir;
use strict;

my $filename;
my $title;
my $topN=0;
my $print=0;

&init;

my %uniq;
while (<STDIN>) {
	chomp;
	$uniq{$_}+=1;
}

my @twoD;
my $i=0;
for my $a (keys %uniq) {
	$twoD[$i][0]=$a;
	$twoD[$i++][1]=$uniq{$a};
}


# sort by label: @labels = sort {$a <=> $b} @labels;

@twoD = reverse sort { $a->[1] <=> $b->[1] } @twoD ;

if ($topN>0) {
	@twoD = @twoD[0..$topN-1];
}

my @data = map $_->[ 1 ], @twoD;
my @labels = map $_->[ 0 ], @twoD;

if ($print) {
	print join("\n",@labels);
}

my $c = new XYChart(800, 800,0xffffff,-1,-1);
$c->swapXY(1);
$c->setPlotArea(200, 45, 650, 700, 0xffffff, -1, 0xffffff, $perlchartdir::Transparent, $perlchartdir::Transparent);
$c->addTitle($title, "arialb.ttf", 14);
$c->xAxis()->setLabels(\@labels); 
$c->xAxis()->setColors($perlchartdir::Transparent, 0);

my $layer = $c->addBarLayer(\@data,0x888888);
$layer->setBorderColor($perlchartdir::Transparent);
$layer->setBarGap(0.1);

$c->makeChart($filename);

exit;

sub init() {
    my %opt;
    use Getopt::Std;
    getopts("hpf:n:t:", \%opt ) or usage();

    # Help?
    usage() if $opt{h};
    
    $filename = $opt{f} if $opt{f};
    $title = $opt{t} if $opt{t};
    $topN = $opt{n} if $opt{n};
    $print = 1 if $opt{p};
}

sub usage() {

    print STDERR << "EOF";

Usage: cat file.csv | bar.pl [-hp] -f outputfile [-t title] [-n topN]");

-f	     : output file name, ending in .PNG
-h           : this (help) message
-n           : only show the top N entires
-p           : print the labels
-t	     : chart title

EOF
    exit;
}
    

