#!/usr/bin/env python

import glob
import os

def main():
    ipc7351_least =   Footprint_Library.read("IPC7351-Least")
    ipc7351_nominal = Footprint_Library.read("IPC7351-Nominal")
    ipc7351_most =    Footprint_Library.read("IPC7351-Most")
    
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

class Footprint_Library():
    def __init__(self):
	""" *Footprint_Library*: Initialize the *Footprint_Library* object (i.e. *self*)
	    to contain an empty list of footprints:
	"""

	self.footprints = []

    @staticmethod
    def read(directory):
	""" *Footprint_Libraries*: Read the files that end with ".fpl' suffix from *directory*
	    into a newly created *Footprints_Library* object and return it.
	"""

	# Verify argument types:
        assert isinstance(directory, str)

	print("Read directory '{0}'".format(directory))

	# Create *footprint_libraries*:
	footprint_library = Footprint_Library()
	
	# Use the Python glob libary to to read all the *file_names* from *directory*:
	file_names = glob.glob(os.path.join(directory, "*"))

	# Read in the appropriate footprints:
        footprints = []
	for file_name in file_names:
	    #print("file_name='{0}'".format(file_name))
	    if file_name.endswith(".fpl"):
		#print("Read in footprint file '{0}'".format(file_name))
		footprint = Footprint.read(directory, file_name)
		if footprint != None:
		    footprints.append(footprint)

	# Save *footprints*:
	footprint_library.footprints = footprints

	# Return resultant *footprint_library*:
	return footprint_library

class Footprint():

    def __init__(self, directory, file_name):
	""" *Footprint* Initialize the *Footprint* object (i.e. *self*) to contain
	    both *directory* and *file_name*:
	"""

	# Verify argument types
	assert isinstance(directory, str)
	assert isinstance(file_name, str)

	# Use *footprint instead of *self*:
	footprint = self

	# Save *full_file_name* into *footprint*
	footprint.file_name = os.path.join(directory, file_name)

    def parse(self, parse):
	""" *Footprint*: This routine will parse one *Footprint* using *parse*.  *None* is
	    returned if there is no *Footprint* to be read:
	"""

	#print("=>Footprint.parse()")

	# Verify argument types:
	assert isinstance(parse, Parse)

	# Use *footprint* instead of *self*:
	footprint = self

	# Make sure we start with a *name*:
	error = False
	if parse.tag_match("name:"):
	    # Parse the *name*:
	    name = parse.string_parse()
	    parse.end_of_line()
	    footprint.name = name

	    # Parse the *author*
	    author = None
	    if parse.tag_match("author:"):
		author = parse.string_parse()
		parse.end_of_line()
	    footprint.author = author

	    # Parse the *source*:
	    source = None
	    if parse.tag_match("source:"):
		source = parse.string_parse()
		parse.end_of_line()
	    footprint.source = source

	    # Parse *description*:
	    description = None
	    if parse.tag_match("description:"):
		description = parse.string_parse()
		parse.end_of_line()
	    footprint.description = description

	    # Parse *units*:
	    units = None
	    if parse.tag_match("units:"):
		units = parse.string_parse()
		parse.end_of_line()
	    footprint.units = units

	    # Parse *selection_rectangle*:
	    selection_rectangle = None
	    if (parse.tag_match("sel_rect:")):
		selection_rectangle = Rectangle.parse(parse)
		parse.end_of_line()
	    footprint.selection_rectangle = selection_rectangle

	    # Parse *reference_text*:
	    reference_text = None
	    if parse.tag_match("ref_text:"):
		reference_text = Text.parse(parse)
		parse.end_of_line()
	    footprint.reference_text = reference_text

	    # Parse *value_text*:
	    value_text = None
	    if parse.tag_match("value_text:"):
		value_text = Text.parse(parse)
	        parse.end_of_line()
	    footprint.value_text = value_text

	    # Parse *centroid*:
	    centroid = None
	    if parse.tag_match( "centroid:"):
		centroid = Rectangle.parse(parse)
		parse.end_of_line()
	    footprint.centroid = centroid

	    # Now parse any *polylines*:
	    polylines = []
	    while True:
		polyline = Polyline.parse(parse)
		if polyline == None:
		    # No more polylines:
		    break

		# We got a *polyline*:
		polylines.append(polyline)
	    footprint.polylines = polylines

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
	    footprint.pins = pins

	    # Slurp off any blank lines:
	    parse.new_lines_skip()
	else:
	    error = True
	    parse.error("No footprint name")

	#print("<=Footprint.parse()=>{0}".format(error))
	return error

    @staticmethod
    def read(directory, footprint_file_name):
        # Check argument types:
	assert isinstance(directory, str)
        assert isinstance(footprint_file_name, str)

	# Read in *file_contents*:
	with open(footprint_file_name, 'r') as footprint_file:
	    file_contents = footprint_file.read()

        # Use *footprint* instead of *self*:
	parse = Parse(file_contents, footprint_file_name)
	footprint = Footprint(directory, footprint_file_name)

	# We have an error:
	if footprint.parse(parse):
	    footprint = None
	
	return footprint

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


