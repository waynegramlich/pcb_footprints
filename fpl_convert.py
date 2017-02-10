#!/usr/bin/env python

import glob
import os

def main():
    # Read in the footprints libraries:
    ipc7351_least =   Footprints_Library.directory_read("IPC7351-Least")
    ipc7351_nominal = Footprints_Library.directory_read("IPC7351-Nominal")
    ipc7351_most =    Footprints_Library.directory_read("IPC7351-Most")
    
    # Write them out in KiCAD format:
    ipc7351_least.kicad_mod_write("IPC7351-Least")
    ipc7351_nominal.kicad_mod_write("IPC7351-Nominal")
    ipc7351_most.kicad_mod_write("IPC7351-Most")

def integer_mils(micro_meter):
    # This routine will return *micro_meter* converted to tenth mils.

    # 1inch = 1000tmil (tmil = tenth mil)
    # 1inch = 25.4mm = 25400um
    # 1um * (10000tmil/25400um) * (10000tmil/1in)

    # inch_to_micro_meter = 25400000;
    # inch_to_mil = 1000;
    # micro_meter_to_mil = inch_to_mil / inch_to_micro_meter =
    #                    = 25400000 / 1000
    #                    = 25400
    # Since we want tenth mil, we use 2540:

    # Division with negative numbers in C and python are different.  For now we want to
    # emulate C.  This means we round towards zero when dividing a negative number by a
    # positive one:
    if micro_meter < 0:
	# Make it C like rather than Python like:
        return -((-micro_meter) // 2540)
    return micro_meter // 2540

class Corner():
    def __init__(self, x, y, side_style):
        """ *Corner*: Initialize the *Corner* object (i.e. *self*) to contain *x*, *y*,
	    and *side_style*.
	"""

	# Verify argument types:
	assert isinstance(x, int)
	assert isinstance(y, int)
	assert isinstance(side_style, int)

	# Use *corner* instead of *self*:
	corner = self

	# Fill in *corner*:
	corner.x = x
        corner.y = y
        corner.side_style = side_style

    @staticmethod
    def parse(parse):
        """ *Corner*: Parse the "next_corner" tag using *parse* and return the resulting
	    *Corner* object.  If there is no "next_corner" tag, *None* is returned.
	"""

	# See whether we have "next_corner:
	corner = None
	if parse.tag_match("next_corner:"):
	    # Parse the rest of "next_corner:"
	    x = parse.long_parse()
	    y = parse.long_parse()
	    side_style = parse.long_parse()
	    parse.end_of_line()

	    # Create *corner* and fill it in:
	    corner = Corner(x, y, side_style);

	return corner;

class Footprint():
    def __init__(self, name, author, source, description, units, selection_rectangle,
      reference_text, value_text, centroid, polylines, pins):
	""" *Footprint*: Initialize the *Footprint* object to contain *name*, *author*,
	    *source*, *description*, units, *selection_rectangle*, *reference_text*,
	    *value_text*, *centroid*, *polylines*, and *pins*.
	"""
	
	# Verify argument types:
        assert isinstance(name, str)
        assert isinstance(author, str) or author == None
        assert isinstance(source, str) or source == None
        assert isinstance(description, str) or description == None
        assert isinstance(units, str) or units == None
        assert isinstance(selection_rectangle, Rectangle) or selection == None
        assert isinstance(reference_text, Text) or reference_text == None
        assert isinstance(value_text, Text) or value_text == None
        assert isinstance(centroid, Rectangle) or centroid == None
        assert isinstance(polylines, list)
        assert isinstance(pins, list)

	# Use *footprint* instead of *self*:
	footprint = self

	# Load up *footprint*:
        footprint.name = name
        footprint.author = author
        footprint.source = source
        footprint.description = description
        footprint.units = units
        footprint.selection_rectangle = selection_rectangle
        footprint.reference_text = reference_text
        footprint.value_text = value_text
        footprint.centroid = centroid
        footprint.polylines = polylines
        footprint.pins = pins

    def kicad_module_write(self, mod_file):
	""" *Footprint*: Write the *Footprint* object (i.e. *self*) to *mod_file* in the
	    old KiCAD .mod file format.	
	"""

	# Verify argument types:
	assert isinstance(mod_file, file)

        # Use *footprint* instead of *self*:
	footprint = self

	# Output the header portion:
	name = footprint.name
	mod_file.write("$Module {0}\n".format(name))
	timestamp = 0
	unclear = 0
	mod_file.write("Po 0 0 0 15 {0:08x} {1:08x} ~~\n".format(timestamp, unclear))
	mod_file.write("Li {0}\n".format(name))
	mod_file.write("Cd {0}\n".format(footprint.description))
	mod_file.write("Kw CMS XXX\n")
	mod_file.write("Sc {0:08x}\n".format(timestamp))
	mod_file.write("AR {0}\n".format(name))
	mod_file.write("Op 0 0 0\n")
	mod_file.write("At SMD\n")

	# Write out the text:
	footprint.reference_text.kicad_write(0, mod_file)
	footprint.value_text.kicad_write(1, mod_file)

	# Output each *Polyline* in *polylines*:
	polylines = footprint.polylines
	for polyline in polylines:
	    # Extract some values from *polyline*:	
	    line_width = integer_mils(polyline.line_width)
	    start_x = integer_mils(polyline.start_x)
	    start_y = integer_mils(polyline.start_y)
	    close_polyline = polyline.close_polyline
	    corners = polyline.corners

	    # Output one line for each {Corner} in corners}:
	    x = start_x
	    y = start_y
	    for corner in corners:
		# Get the two line end points ready:
		previous_x = x
		previous_y = y
		x = integer_mils(corner.x)
		y = integer_mils(corner.y)

		# Output a KiCAD line:
		mod_file.write("DS {0} {1} {2} {3} {4} 21\n".format(
		  previous_x, -previous_y, x, -y, line_width))

	    # Output a closing line if needed:
	    if polyline.close_polyline:
		mod_file.write("DS {0} {1} {2} {3} {4} 21\n".format(
		  x, -y, start_x, -start_y, line_width))

	# Output each Pin} in {pins}:
	pins = footprint.pins
	for pin in pins:
	    # Grab some values from {pin}:
	    pin_name = pin.name
	    hole_diameter = integer_mils(pin.hole_diameter)
	    x = integer_mils(pin.x)
	    y = integer_mils(pin.y)
	    angle = pin.angle
	    top = pin.top
	    inner = pin.inner
	    bottom = pin.bottom

	    mod_file.write("$PAD\n")
	    if True:
		# Surface mount:
		shape = top.shape
		width = top.width
		length1 = top.length1
		length2 = top.length2
		corner_radius = top.corner_radius

		dx = integer_mils(width)
		dy = integer_mils(length1 + length2)

		if angle == 0:
		    mod_file.write("Sh \"{0}\" R {1} {2} 0 0 0\n".format(pin_name, dy, dx))
		elif angle == 90:
		    mod_file.write("Sh \"{0}\" R {1} {2} 0 0 0\n".format(pin_name, dx, dy))
		else:
		    mod_file.write("Pad Angle={0}\n".format(angle))
		mod_file.write("Dr 0 0 0\n")
		layer_mask = 0x888000;
		mod_file.write("At SMD N {0:08x}\n".format(layer_mask))
		mod_file.write("Ne 0 \"\"\n")
		mod_file.write("Po {0} {1}\n".format(x, -y))
	    mod_file.write("$EndPAD\n")

	# End the module:
	mod_file.write("$EndMODULE  {0}\n".format(name))

    @staticmethod
    def parse(parse):
	""" *Footprint*: Parse one *Footprint* object using *parse*.  *None* is returned
	    if there is no *Footprint* object was successfully parsed.
	"""

	#print("=>Footprint.parse()")

	# Verify argument types:
	assert isinstance(parse, Parse)

	# Make sure we start with a *name*:
	footprint = None
	if parse.tag_match("name:"):
	    # Parse the *name*:
	    name = parse.string_parse()
	    parse.end_of_line()

	    # Parse the *author*
	    author = None
	    if parse.tag_match("author:"):
		author = parse.string_parse()
		parse.end_of_line()

	    # Parse the *source*:
	    source = None
	    if parse.tag_match("source:"):
		source = parse.string_parse()
		parse.end_of_line()

	    # Parse *description*:
	    description = None
	    if parse.tag_match("description:"):
		description = parse.string_parse()
		parse.end_of_line()

	    # Parse *units*:
	    units = None
	    if parse.tag_match("units:"):
		units = parse.string_parse()
		parse.end_of_line()

	    # Parse *selection_rectangle*:
	    selection_rectangle = None
	    if (parse.tag_match("sel_rect:")):
		selection_rectangle = Rectangle.parse(parse)
		parse.end_of_line()

	    # Parse *reference_text*:
	    reference_text = None
	    if parse.tag_match("ref_text:"):
		reference_text = Text.parse(parse)
		parse.end_of_line()

	    # Parse *value_text*:
	    value_text = None
	    if parse.tag_match("value_text:"):
		value_text = Text.parse(parse)
	        parse.end_of_line()

	    # Parse *centroid*:
	    centroid = None
	    if parse.tag_match( "centroid:"):
		centroid = Rectangle.parse(parse)
		parse.end_of_line()

	    # Now parse any *polylines*:
	    polylines = []
	    while True:
		polyline = Polyline.parse(parse)
		if polyline == None:
		    # No more polylines:
		    break

		# We got a *polyline*:
		polylines.append(polyline)

	    # Parse the number of *n_pins* and ignore it:
	    n_pins = 0
	    if parse.tag_match("n_pins:"):
		n_pins = parse.long_parse()
		parse.end_of_line()

	    # Parse the pins:
	    pins = []
 	    while True:
		pin = Pin.parse(parse)
		if pin == None:
		    # No more {Pin} objects:
		    break

		# We have a {pin}:
		pins.append(pin)

	    # Slurp off any blank lines:
	    parse.new_lines_skip()

	    # Create the *footprint*:
	    footprint = Footprint(name, author, source, description, units, selection_rectangle,
              reference_text, value_text, centroid, polylines, pins)

	#print("<=Footprint.parse()")

	return footprint

    @staticmethod
    def directory_read(directory, footprint_file_name):
	""" *Footprint*: Read in all the *Footprint* objects associated with the
	    *footprint_file_name* in *directory* and return it as list.
	"""

        # Check argument types:
	assert isinstance(directory, str)
        assert isinstance(footprint_file_name, str)

	# Read in *file_contents*:
	with open(footprint_file_name, 'r') as footprint_file:
	    file_contents = footprint_file.read()

        # Use *footprint* instead of *self*:
	parse = Parse(file_contents, footprint_file_name)
	
	footprints = []
	while True:
	    footprint = Footprint.parse(parse)
	    if footprint == None:
                break
            footprints.append(footprint)
	
	return footprints

class Footprints_Library():
    def __init__(self, footprints):
	""" *Footprints_Library*: Initialize the *Footprints_Library* object (i.e. *self*)
	    to contain an empty list of footprints:
	"""

	# Verify argument types:
        assert isinstance(footprints, list)
        for footprint in footprints:
	    assert isinstance(footprint, Footprint)

	# Use *footprints_library* inestead of *self*:
        footprints_library = self

	# Load up *footprints_library*:
        footprints_library.footprints = footprints

    @staticmethod
    def directory_read(directory):
	""" *Footprint_Libraries*: Read the files that end with ".fpl' suffix from *directory*
	    into a newly created *Footprints_Library* object and return it.
	"""

	# Verify argument types:
        assert isinstance(directory, str)

	#print("Read directory '{0}'".format(directory))

	# Use the Python glob libary to to read all the *file_names* from *directory*:
	file_names = glob.glob(os.path.join(directory, "*"))

	# Read in the appropriate footprints:
        footprints = []
	for file_name in file_names:
	    #print("file_name='{0}'".format(file_name))
	    if file_name.endswith(".fpl"):
		#print("Read in footprint file '{0}'".format(file_name))
		file_footprints = Footprint.directory_read(directory, file_name)
		assert isinstance(footprints, list)
		footprints.extend(file_footprints)

	print("Read in {0} footprints from '{1}'".format(len(footprints), directory))

	# Create and return *footprints_library*:
	footprints_library = Footprints_Library(footprints)
	return footprints_library

    def kicad_mod_write(self, mod_file_name):
	""" *Footprint_Libraries*: Write out the *Footprint_Libraries* object (i.e. *self*)
	    to *mod_file_name* in KiCAD .mod file format.
	"""

	# For now just write to /tmp:
	mod_file_name = "/tmp/" + mod_file_name

	# Verify argument types:
        assert isinstance(mod_file_name, str)

	# Use *footprints_library* instead of *self*:
        footprints_library = self

        # Grab the *footprints*:
        footprints = footprints_library.footprints

	sorted_footprints = sorted(footprints, key = lambda footprint: footprint.name)

	# Open {mod_file_name}:
	mod_file = open(mod_file_name, "w")
	assert mod_file != None

	# Output header lines to *mod_file*:
	mod_file.write("PCBNEW-LibModule-V1  Sat 01 Jan 2000 00:00:00 PM PDT\n")
	mod_file.write("# encoding utf-8\n")

	# Output index to *mod_file*:
	mod_file.write("$INDEX\n")
	for footprint in sorted_footprints:
	    mod_file.write("{0}\n".format(footprint.name))
	mod_file.write("$EndINDEX\n")

	# Now output each of the *footprint*:
	for footprint in sorted_footprints:
	    footprint.kicad_module_write(mod_file)
	# End the library and close *mod_file*:
	mod_file.write("$EndLIBRARY\n")
	mod_file.close()

class Pad():
    def __init__(self, shape, width, length1, length2, corner_radius):
	""" *Pad*: Initialize the *Pad* object (i.e. *self*) to contain *shape*, *width*,
	    *length1*, *length2*, and *corner_radius*.
	"""

	# Verify argument types:
	assert isinstance(shape, int)
	assert isinstance(width, int)
	assert isinstance(length1, int)
	assert isinstance(length2, int)
	assert isinstance(corner_radius, int)

	# Use *pad* instead *self*:
	pad = self

	# A Pad is one surface of a pin:
	pad.shape = shape
	pad.width = width
        pad.length1 = length1
        pad.length2 = length2
	pad.corner_radius = corner_radius

    @staticmethod
    def parse(parse, tag_name):
	""" *Pad*: """
	# Verify argument types:
        assert isinstance(parse, Parse)
        assert isinstance(tag_name, str)

	pad = None
	if parse.tag_match(tag_name):
	    shape = parse.long_parse()
	    width = parse.long_parse()
	    length1 = parse.long_parse()
	    length2 = parse.long_parse()
	    corner_radius = parse.long_parse()
	    parse.end_of_line()
	    pad = Pad(shape, width, length1, length2, corner_radius)
        return pad

class Parse():

    def __init__(self, contents, file_name):
	""" *Parse*: Initialize the *Parse* object (i.e. *self*) to contain *contents* and
	    *file_name*.
	"""

	# Verify argument types:
	assert isinstance(contents, str)
	assert isinstance(file_name, str)
	
	# Use *parse* instead of *self*:
	parse = self
	
	# Load up *parse* with *contents*:
	parse.contents = contents	# File contents
	parse.file_name = file_name	# File name
        parse.line_number = 1		# Current line number
	parse.offset = 0		# Offset into *contents*
	parse.size = len(contents)	# Size of *contents*
        
    def end_of_line(self):
	""" *Parse*  This routine will parse an end-of-line using a the *Parse* object
	    (i.e. *self*).
	"""

	# Use *parse* instead of *self*:
	parse = self

	# Skip over any white space:
	self.white_space_skip()

	# Grab some values from {parse}:
	contents = parse.contents
	offset = parse.offset
	size = parse.size

	# Search until we find an end-of-line:
	error = False
	while offset < size:
	    # Grab next character:
	    character = contents[offset]
	    offset += 1

	    # Check {character}:
	    if character == '\n':
		# We found the end; bump line number:
		parse.line_number += 1
		break
	    elif character == '\r':
		# Ignore carriage returns:
		pass
	    else:
		# We have a bogus character; keep looking:
		error = True	    
    
	# Print any errors:
	if error:
	    parse.error("Garbage at end of line")

	# Restore *offset* to to point after end-of-line:
	parse.offset = offset

    def error(self, error_message):
	""" *Parse*: Output *error_message* using the *Parse* object (i.e* *self* to
	    to provide the file name and line number.
	"""

	# Use *parse* instead of *self*:
	parse = self

	# Output *error_message*:
	print("{0}:{1} {2}".format(parse.file_name, parse.line_number, error_message))
    
    def is_empty(self):
	""" *Parse*: Return True if the *Parse* object (i.e. *self8) is empty
	    and False otherwise.
	"""

	# Use *parse* instead of *self*:
	parse = self

	# Return *True* if there no more characters to parse:
	return parse.offset >= parse.size

    def long_parse(self):
	""" *Parse*: Return the next long from the *Parse* object (i.e. *self*): """

	# Use *parse* instead of *self*:
	parse = self

	# Skip over any white space:
	parse.white_space_skip()

	# Grab some values from {parse}
	contents = parse.contents
	offset = parse.offset
	size = parse.size

	# Check for minus sign:
	negative = False
	if offset < size and contents[offset] == '-':
	    offset += 1
	    negative = True

	# Process digits of number:
	result = 0
	error = True
	while offset < size:
	    character = contents[offset]
	    if character.isdigit():
		result = result * 10 + int(character)
		offset += 1
		error = False
	    else:
		break

	# Indicate any errors:
	if error:
	    parse.error("Bad number")

	# Deal with minus sign:
	if negative:
	    result = -result

	# Restore *offset* back into *parse*:
	parse.offset = offset

	return result

    def new_lines_skip(self):
	""" *Parse*: Skip over any empty lines in the *Parse* object (i.e. *self*). """

	# Use *parse* instead of *self*:
	parse = self

	# Grab some values out of {parse}:
	contents = parse.contents
	offset = parse.offset
	size = parse.size

	# Iterate over white space and new-lines:
	while (offset < size):
	    character = contents[offset]
	    if character == '\r' or character == ' ' or character == '\t':
		# White space or carraige return:
		offset += 1
	    elif character == '\n':
		# End of line:
		offset += 1
		parse.line_number += 1
		break
	    else:
		# Something other that whitespace or end of line:
		break

	# Restore *offset*
	parse.offset = offset


    def string_parse(self):
	""" *Parse*: Return a string from the *Parse* object (i.e. *self*). """

	# Use *parse* instead of *self*:
	parse = self

	# Skip over any white space:
	parse.white_space_skip()

	# Grab some values from {parse}:
	contents = parse.contents
	offset = parse.offset
	size = parse.size

	string = None
	if offset < size:
	    # Keep track of beginning and end of string in *contents*:
	    start_index = offset
	    end_index = offset

	    # Read first character:
	    character = contents[offset]
	    offset += 1

	    # Check for double quoted string
	    if character == '"':
		# We have a string enclosed in double quotes:
		start_index = offset

		# Look for closing double quote:
		while offset < size:
		    # Read next *character* without advancing *offset*:
		    character = contents[offset]

		    # Check for double quote:
		    if character == '"':
			# We found the closing double quote:
			end_index = offset

			# Advance past the double quote:
			offset += 1
			
			# Create *string*:
			#print("start_index={0} end_index={1}".format(start_index, end_index))
			string = contents[start_index:end_index]
			break
		    elif character == '\n':
			# Unterminated string:
			parse.error("Missing closing double quote in string")
		    else:
			# Keep looking for the end of string:
			offset += 1
		
	    else:
		# We have a white space terminated string:
		while offset < size:
		    # Read next *character* without advancing *offset*::
		    character = contents[offset]

		    # Look for the end:
		    if character == ' ' or character == '\n' or character == '\r':
			# We found the last character of the string:
			end_index = offset

			# Create *string*:			
			string = contents[start_index:end_index]
			break
		    else:
			# Keep looking for the end of the stringt:
              		offset += 1

	else:
	    # We are at end of file and are missing a string:
	    Parse__error(parse, "Missing string")

	# Restore *offset* and return *string*:
 	parse.offset = offset
	return string

    def tag_match(self, tag):
	""" *Parse*: Return *True* if *tag* matches the next batch of in the *Parse* 
	    (i.e. *self*).  *tag* should be terminated by a colon.  When a match occurs,
	    the tag is removed from *parse*.
	"""

	#print("=>Parse.tag_matach(*, '{0}')".format(tag))

	# Verify argument types:
	assert isinstance(tag, str)

	# Use *parse* instead of *self*:
	parse = self

	# Skip over any white space:
	parse.white_space_skip()

	# Compute length of {tag}:
	tag_size = len(tag)

	# Grab some values from {parse}:
	size = parse.size
	offset = parse.offset
	contents = parse.contents

	# See if we have a matching tag:
	result = False
	remaining = size - offset

	#tag_to_match = contents[offset:offset + tag_size]
	#print("remaining={0} tag_to_match='{1}'".format(remaining, tag_to_match))

	if tag_size <= remaining and contents[offset:offset + tag_size] == tag:
	    # We have a match; push {offset} forward:
	    #print("match")
	    parse.offset = offset + tag_size
	    result = True

	#print("<=Parse.tag_match(*, '{0}')=>{1}".format(tag, result))

	return result

    def white_space_skip(self):
	""" *Parse*: Advance the *Parse* object (i.e. *self*)  over any white space. """

	# Use *parse* instead of *self*:
	parse = self

	# Grab some values out of {parse}:
	contents = parse.contents
	offset = parse.offset
	size = parse.size

	# Iterate across {contents} starting at {offset} until the end
	# reached or until there are no more white space characters:
	while offset < size:
	    character = contents[offset]
	    if character == ' ' or character == '\t':
		# Got some white space; keep going:
		offset += 1
	    else:
		# Not white space; quit:
		break

	# Restore {offset} back into {parse}:
	parse.offset = offset

class Pin():
    def __init__(self, name, hole_diameter, x, y, angle, top, inner, bottom):
	""" *Pin*: Initialize the *Pin* object (i.e. *self*) with *name*, *hole_diameter*,
	    *x*, *y*, *angle*, *top*, *inner* and *bottom*.
	"""

	# Verify argument types:
        assert isinstance(name, str)
	assert isinstance(hole_diameter, int)
	assert isinstance(x, int)
	assert isinstance(y, int)
	assert isinstance(angle, int)
	assert isinstance(top, Pad) or top == None
	assert isinstance(inner, Pad) or inner == None
	assert isinstance(bottom, Pad) or bottom == None

	# Use *pin* instead of *self*:
	pin = self

        # Fill in *pin*:
	pin.name = name
	pin.hole_diameter = hole_diameter
	pin.x = x
	pin.y = y
	pin.angle = angle
	pin.top = top
	pin.inner = inner
	pin.bottom = bottom

    @staticmethod
    def parse(parse):
        """ *Pin*: Parse and return a *Pin* object using *parse*.  *None* is returned if no
	    *Pin* is found.
	"""

	pin = None
	if parse.tag_match("pin:"):
	    name = parse.string_parse()
	    hole_diameter = parse.long_parse()
	    x = parse.long_parse()
	    y = parse.long_parse()
	    angle = parse.long_parse()
	    parse.end_of_line()

	    top = Pad.parse(parse, "top_pad:")
	    inner = Pad.parse(parse, "inner_pad:")
	    bottom = Pad.parse(parse, "bottom_pad:")

	    # Create *pin*:
	    pin = Pin(name, hole_diameter, x, y, angle, top, inner, bottom)
	return pin

class Polyline():
    def __init__(self, line_width, start_x, start_y, close_polyline, close_style, corners):
	""" *Polyline*: Initialize the *Polyline* object (i.e. *self*) to contain *line_width*,
	    *start_x*, *start_y*, *close_polyline*, *close_style*, and *corners*.
	"""

	# Verify argument types:
	assert isinstance(line_width, int)
	assert isinstance(start_x, int)
	assert isinstance(start_y, int)
	assert isinstance(close_polyline, bool)
	assert isinstance(close_style, int)
        assert isinstance(corners, list)

	# Use *polyline* instead of *self*:
	polyline = self

	# Fill in *polyline*:
	polyline.line_width = line_width
	polyline.start_x = start_x
	polyline.start_y = start_y
	polyline.close_polyline = close_polyline
	polyline.close_style = close_style
	polyline.corners = corners

    @staticmethod
    def parse(parse):
	""" *Polyline*: Parse a *Polyline* object using *parse* and return it. """

	# See whether we have a "outline_polyline:"
	polyline = None
	if parse.tag_match("outline_polyline:"):
	    # Parse the rest of "outline_polyline:"
	    line_width = parse.long_parse()
	    start_x = parse.long_parse()
	    start_y = parse.long_parse()
	    parse.end_of_line()

	    # Parse any "next_corner:" tags:
	    corners = []
	    while True:
		# Grab all of the "next_corner:" tags:
		corner = Corner.parse(parse)
		if corner == None:
		    # No more "next_corner:" tags:
		    break

		# Got a *corner*; append it to *corners*:
		corners.append(corner)

	    # Now see if there is a "close_polyline:" tag:
	    close_polyline = False
	    close_style = 0
	    if parse.tag_match("close_polyline:"):
		# Yes, there is:
		close_polyline = True;
		close_style = parse.long_parse()
		parse.end_of_line()

	    # Create and initialize *polyline*:
	    polyline = Polyline(line_width, start_x, start_y, close_polyline, close_style, corners)

	return polyline

class Rectangle():
    def __init__(self, left, bottom, right, top):
        """ *Rectangle*: Initialize the *Rectangle* object (i.e. *self*) to contain *left*,
	    *bottom*, *right*, and *top*.
	"""
	
	# Verify argument types:
        assert isinstance(left, int)
        assert isinstance(bottom, int)
        assert isinstance(right, int)
        assert isinstance(top, int)

	# Use *rectangle* instead of *self*:
        rectangle = self

        # Fill in *rectangle*:
        rectangle.left = left
        rectangle.bottom = bottom
        rectangle.right = right
        rectangle.top = top

    @staticmethod
    def parse(parse):
	# Parse the 4 coordinates:
	left = parse.long_parse()
	bottom = parse.long_parse()
	right = parse.long_parse()
	top = parse.long_parse()

	# Create and return the *rectangle*:
        rectangle = Rectangle(left, bottom, right, top)
	return rectangle

class Text():
    def __init__(self, height, left, bottom, angle, line_width):
	""" *Text*: Initialize the *Text* object (i.e. *self*) to contain *height*, *left*,
	    *bottom*, *angle*, and *line_width*.
	"""

	# Verify argument types:
        assert isinstance(height, int)
        assert isinstance(left, int)
        assert isinstance(bottom, int)
        assert isinstance(angle, int)
        assert isinstance(line_width, int)

	# Use *text* instead of *self*:
	text = self

        # Fill in *text*:
	text.height = height
	text.left = left
	text.bottom = bottom
	text.angle = angle
	text.line_width = line_width

    def kicad_write(self, field_number, mod_file):
	""" *Text*: """

	x_position = 0;
	y_position = 0;
	x_size = 400;
	y_size = 400;
	pen_width = 80;

	mod_file.write("T{0} {1} {2} {3} {4} 0 {5} N V 21 N {6}\n".format(
	  field_number, x_position,  y_position, x_size, y_size, pen_width, "~"))

    @staticmethod
    def parse(parse):
	# Parse the values:
	height = parse.long_parse()
	left = parse.long_parse()
	bottom = parse.long_parse()
	angle = parse.long_parse()
	line_width = parse.long_parse()

	# Create and return *text*:
	text = Text(height, left, bottom, angle, line_width)
	return text

if __name__ == "__main__":
    main()


