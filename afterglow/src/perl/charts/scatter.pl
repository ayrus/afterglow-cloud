#!/usr/bin/perl
use perlchartdir;
use strict;

my $file=$ARGV[0];
print STDERR "Opening file: $file\n";
open(F,$file) || die ("error opening file $file");

my @data;
my @data2;
my @color;
my @shape;
#my $jitter=1;
my $maxcolor;
my $maxx;
while (<F>) {
	chomp;
	split/,/; 
	push @data,$_[0];
	push @data2,$_[1];
	push @color,$_[2];
	push @shape,$_[3];
	#print STDERR $_[0]."  ".$_[1]."\n";
	if ($_[2]>$maxcolor) { $maxcolor = $_[2]; }
	if ($_[0]>$maxx) { $maxx = $_[0]; }
}
close F;

#if ($jitter) {
#for (my $i=0; $i<=$#data; $i++) {
#print "from: $data[$i] to: ";
#my $rand= int ((rand($maxx/10) - $maxx/20) * 100) / 100;
#$data[$i] += $rand; 	
#print "$data[$i]\n";
#}
#}

my $c = new XYChart(600, 300);
$c->setPlotArea(45, 45, 500, 200, 0xffffff, -1, $perlchartdir::Transparent, $perlchartdir::Transparent, $perlchartdir::Transparent);
$c->addTitle("Risk", "arialb.ttf", 14);
$c->xAxis()->setWidth(1);
$c->yAxis()->setWidth(1);
$c->xAxis()->setTitle("Exposure", "arialbi.ttf", 10); 
$c->yAxis()->setTitle("Impact", "arialbi.ttf", 10); 
$c->yAxis()->setLinearScale(0,10);
$c->xAxis()->setLinearScale(0,10);

my $i=0;
foreach (@data) {
	my @one = @data[$i]; 
	my @two = @data2[$i];
	my $color = int 256 - ($color[$i] * ( 256 / $maxcolor )) ;       
	$color = ($color * 256 * 256) + ($color * 256) + $color;
	if ($shape[$i] % 3 == 0) {
		$c->addScatterLayer(\@one,\@two,"",$perlchartdir::TriangleSymbol,10,$color);
	} elsif ($i %3 == 1) {
		$c->addScatterLayer(\@one,\@two,"",$perlchartdir::DiamondSymbol,10,$color);
	} else {
		$c->addScatterLayer(\@one,\@two,"",$perlchartdir::CircleSymbol,10,$color);
	}
	$i++;
}

$c->makeChart("exposureXimpact.png");

