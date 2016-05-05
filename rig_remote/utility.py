#!/usr/bin/env python

"""
Remote application that interacts with rigs using rigctl protocol.

Please refer to:
http://gqrx.dk/
http://gqrx.dk/doc/remote-control
http://sourceforge.net/apps/mediawiki/hamlib/index.php?title=Documentation

Author: Rafael Marmelo
Author: Simone Marzona

License: MIT License

Copyright (c) 2014 Rafael Marmelo
Copyright (c) 2015 Simone Marzona
Copyright (c) 2016 Tim Sweeney

TAS - Tim Sweeney - mainetim@gmail.com

2016/05/04 - TAS - Moved frequency_pp and frequency_pp_parse here.

"""


import re

def frequency_pp(frequency):
    """Filter invalid chars and add thousands separator.

    :param frequency: frequency value
    :type frequency: string
    :return: frequency with separator
    :return type: string
    """

    return '{:,}'.format(int(re.sub("[^0-9]", '', frequency)))


def frequency_pp_parse(frequency):
    """Remove thousands separator and check for invalid chars.

    :param frequency: frequency value
    :type frequency: string
    :return: frequency without separator or None if invalid chars present
    :return type: string or None
    """

    nocommas = frequency.replace(',', '')
    results = re.search("[^0-9]", nocommas)
    if results == None:
        return (nocommas)
    else:
        return (None)
