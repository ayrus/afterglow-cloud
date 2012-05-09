# IP::Anonymous - Perl port of Crypto-PAn to provide anonymous IP addresses
#
# Copyright (c) 2005 John Kristoff <jtk@northwestern.edu>.  All rights
# reserved.  This program is free software; you can redistribute it and/or
# modify it under the same terms as Perl itself.

package IP::Anonymous;
$VERSION = '0.04';
require 5.001;

# base extensions and modules
use strict;                 # force us to code defensively
use warnings;               # do not let laziness go unnoticed
use vars qw($VERSION);      # package scope global vars
use Carp;                   # make errors the caller's problem
use Socket;                 # for convenient dotted quad handling routines

# additional modules
use Crypt::Rijndael;        # the Rijndael crypto magic

# module scope vars
my $m_pad;                  # 2nd 128 bits of user key used for secret padding
my $ecb;                    # electronic codebook mode (default) object
my $first4bytes_pad;        # 1st 4 bytes of secret pad in "network" order

# initialize
sub new {
    my $package = shift;
    my @key = @_;           # expected key is 32 8-bit unsigned ints
    my $m_key;              # 1st 128 bits of user key used for cipher

    # 1st 128 bits of key used as secret key for Rijndael cipher
    $m_key = pack("C16", @key[0..15]);
    # 2nd 128 bits of key used for secret padding
    $m_pad = pack("C16", @key[16..31]);

    # init the key
    $ecb = new Crypt::Rijndael $m_key;
    # encrypt the 128-bit secret pad
    $m_pad = $ecb->encrypt($m_pad);

    # first four bytes of secret pad in "network" (big-endian) order
    $first4bytes_pad = unpack("N", $m_pad);

    return bless({}, $package);
}

# generate a bit using the Rijndael cipher for each of the 32 bit address
# msb bits taken from original address, remaining bits are from m_pad
sub anonymize {
    my $package = shift;
    my $address = shift;    # expect dotted quad string
    my $first4bytes_input;  # used to handle the byte ordering problem
    my @rin_input = ();     # psuedorandom Rijndael cipher used each round
    my $rin_output;         # encrypted byte result at each round
    my $result = 0;         # initialize psuedorandom one time pad

    # rudimentary check for correctly formatted dotted quad
    if($address !~ /^\d{1,3}(?:\.\d{1,3}){3}$/) {
        croak("ERROR [".__LINE__."]: invalid IP address format\n");
        return;
    }

    # convert dotted quad to long in "network" (big-endian) order
    $address = unpack("N", pack("C4", split /\./, $address));

    # Rijndael cipher used to obtain each of the 32 anonymized bits
    @rin_input = unpack("C16", $m_pad);

    # init input with encrypted pad 
    $rin_input[0] = ($first4bytes_pad >> 24);
    # mask off excess bits for 64-bit systems in left shift
    $rin_input[1] = (($first4bytes_pad << 8 & 0xffffffff) >> 24);
    $rin_input[2] = (($first4bytes_pad << 16 & 0xffffffff) >> 24);
    $rin_input[3] = (($first4bytes_pad << 24 & 0xffffffff) >> 24);

    # get an 8-bit byte
    $rin_output = unpack("C", $ecb->encrypt(pack("C16", @rin_input)));
    # only the first bit of rin_output is used for each round
    $result |= ($rin_output >> 7) << 31;

    # loop through remaining 31 bits
    for (my $position=1; $position <= 31; $position++) {
        $first4bytes_input = (($address >> (32-$position)) <<
                             (32-$position)) |
                             # mask off excess bits for 64-bit systems
                             (($first4bytes_pad << $position & 0xffffffff) >>
                              $position);

        $rin_input[0] = ($first4bytes_input >> 24);
        # mask off excess bits for 64-bit systems in left shift
        $rin_input[1] = (($first4bytes_input << 8 & 0xffffffff) >> 24);
        $rin_input[2] = (($first4bytes_input << 16 & 0xffffffff) >> 24);
        $rin_input[3] = (($first4bytes_input << 24 & 0xffffffff) >> 24);

        # get an 8-bit byte
        $rin_output = unpack("C", $ecb->encrypt(pack("C16", @rin_input)));
        # only the first bit of rin_output is used for each round
        $result |= ($rin_output >> 7) << (31-$position);
    }
    # return anonymized, prefix-preserved address as a dotted quad string
    return inet_ntoa(pack("N", $result ^ $address))
}

1;

__END__

=head1 NAME

IP::Anonymous - Perl port of Crypto-PAn to provide anonymous IP addresses

=head1 SYNOPSIS

  use IP::Anonymous;
  @key = (0..31);
  my $object = new IP::Anonymous(@key);
  print $object->anonymize("192.0.2.0")."\n";

=head1 DESCRIPTION

This is a Perl port of Crypto-PAn.  Crypto-PAn is a cryptography-based
sanitization tool for network trace or log data.  The tool has the
following properties:

=over 4

=item * One-to-one

The mapping from original IP addresses to anonymized IP addresses is
one-to-one.

=item * Prefix-preserving

The IP address anonymization is prefix-preserving.  That is, if two
original IP addresses share a k-bit  prefix, their anonymized mappings
will also share a k-bit prefix.

=item * Consistent across traces

Multiple traces can be sanitized in a consistent way, over time and
across locations, even though the traces might be sanitized separately at
different time and/or at different locations.

=item * Cryptography-based

To sanitize traces, trace owners provide a secret key.  Anonymization
consistency across multiple traces is achieved by the use of the same
key.  The construction of IP::Anonymous preserves the secrecy of the
key and the (pseudo)randomness of the mapping from an original IP
address to its anonymized counterpart.

=back

This Perl port of Crypto-PAn uses similar logic to that found in
Crypto-PAn 1.0, but most importantly maintains consistency in the
process so that regardless of implementation, using the same key
in each will give consistent results.

=head1 REQUIRES

Crypt::Rijndael - XS-based implementation of the Advanced Encryption
Standard (AES) algorithm Rijndael by Joan Daemen and Vincent Rijmen.

=head1 USAGE

=over 4

=item $object = new IP::Anonymous(@key)

Initializes the electronic codebook object with a 32 8-bit decimal
array.   This array, consisting of 32 decimals between 0 and 255
inclusive, is the user defined private key for this anonymization
session.  This 256 bit key should be kept private.  The key can be
used across sessions to maintain consistent mappings between the
original and the anonymized IP addresses.

=item $object->anonymize($address)

Called with a dotted quad IP address string (e.g. 192.0.2.0).  Returns
an anonymized version of that IP address as a dotted quad string.

=back

=head1 BUGS

The Crypt::Rijndael module as of version 0.05 contains at least one
fatal flaw for users of 64-bit systems.  rijndael.h specifies a
32 bit integer as an unsigned long.  This works on 32-bit systems,
but not 64-bit systems.   This is easily circumvented by changing
the definition for UINT32 from a unsigned long to an unsigned int
for platforms the author has tested on.

The Crypt::Rijndael module on CPAN tested with IP::Anonymous has
as it's package version number 0.05, but in the Rijndael.pm module
file itself, VERSION is set to 0.04.  IP::Anonymous specifies that
at least 0.04 of Crypt::Rijndael is required, but the original 0.04
version has not been tested.  It is presumed to work, but you should
use the module whose package version number is 0.05 or later if
possible.

IP::Anonymous only provides support for IPv4 addresses.

=head1 AUTHOR

Original Crypto-PAn C++ implementation was done by Jinliang Fan.  The
Perl module port is by John Kristoff.  Thanks to Stephen Gill for
initial testing and suggesting changes in the beginning stages of the
module implementation process.

=head1 COPYRIGHT

This library is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.

=head1 SEE ALSO

This module is based on the original Crypto-PAn project tool
designed and implemented in C++ by Jinliang Fan.  The Crypto-PAn
project web page is located at:

=over 4

http://www.cc.gatech.edu/computing/Telecomm/cryptopan/

=back

=head1 SECURITY

Even though this module uses strong cryptography to anonymize IP
addresses there may still be a number of avenues of attack that can
be successful in discovering underlying information.  For a good
description of this problem see the paper I<The Devil and Packet Trace
Anonymization> by Mark Allman, et al., which can be found at:

=over 4

http://www.icir.org/enterprise-tracing/papers.html

=back

=head1 AVAILABILITY

IP::Anonymous is available on the Comprehensive Perl Archive Network
(CPAN) and also off the author's homepage (as of this writing) at:

=over 4

http://aharp.ittns.northwestern.edu/software/

=back
The module author intends to maintain software signatures (PGP and/or
message digest hash) on his pages to help you verify that what you have
gotten elsewhere is what he expected you to have.

=cut
