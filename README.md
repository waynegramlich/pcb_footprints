# pcb_footprints

Some code supporting IPC-7351 footprints.

If you are not familiar with IPC-7351 footprint specifications,
you should start with:

>    [IPC-7351B Naming Conventions](http://landpatterns.ipc.org/IPC-7351BNamingConvention.pdf)

This document provides a terse "cheat sheet" for the various
IPC footprint names.

Next, there is a document that I found on the net written
by Tom Hausher:

>    [The CAD Library of the Future](http://www.dnu.no/arkiv1/The%20CAD%20Library%20of%20the%20Future.pdf)

that talks about PCB footprints, standards, etc.

There is another much larger document written by Tom Hausher,

>    [The CAD Library](http://www.frontdoor.biz/HowToPCB/HowToPCB-extra/CADlib.pdf)

that goes into much greater detail about PCB footprints.

It looks like Tom is now CEO of:

>    [PCBLibraries](http://www.pcblibraries.com/)

which looks like they are selling a very comprehensive
component library solution for professionals.


## FPL Convert


FPL Convert takes some IPC-7351 footprint libraries
from the [FreePCB Project](http://freepcb.com/)
and converts them to modules that can be read into
[KiCAD](kicad.sourceforge.net).

To build from scratch, download the following compressed file:

>    [fpl_convert.zip](fpl_convert.zip)

that contains a makefile and the C source code.  The Makefile
downloads the libraries, compiles the code and converts
everything into the correct format.

If you do not want to do that you can download the appropriate
library for KiCAD:

* [LPC7351-Least.mod](LPC7351-Least.mod)

* [LPC7351-Nominal.mod](LPC7351-Nominal.mod)

* [LPC7351-Most.mod](LPC7351-Most.mod)

Most people should go with LPC7351-Nominal.






