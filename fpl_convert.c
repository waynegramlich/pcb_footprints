// Copyright (c) 2011 by Wayne C. Gramlich.  All rights reserved.

// This code is to be released using an open source license (e.g
// GPL, ...)  I really do not care which one.

// Include files in alphabetical order:
#include <assert.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// All types are capitalized:

// Scalar types:
typedef char Character;			// {Character} is 8-bits
typedef int Integer;			// {Integer} is signed 32-bits
typedef int Logical;			// {Logical} is 32 bits
typedef long long Long;			// {Long} is 64-bits
typedef double Double;			// {Double} is 64-bits
typedef unsigned int Unsigned;		// {Unsigned} is unsigned 32-bits

// Pointer types:
typedef void *Memory;			// {Memory} pointer
typedef void *Element;			// {Array} element
typedef Element *Elements;		// Vector of array {Element}'s
typedef Character *String;		// A standard null terminated {String}

// Data types from header files:
typedef DIR* Directory;			// Directory scanning structure
typedef FILE* File;			// Buffered File I/O structure
typedef struct dirent *Directory_Entry;	// Directory entry

// Record types:
typedef struct Array___struct *Array;		// Dynamically extendible array
typedef struct Corner___struct *Corner;		// Polyline corner
typedef struct Footprint___struct *Footprint;	// A full IC footprint
typedef struct Pad___struct *Pad;		// One pad of footprint
typedef struct Parse___struct *Parse;		// A parsing structure
typedef struct Pin___struct *Pin;		// One pin of IC footprint
typedef struct Polyline___struct *Polyline;	// A full polyline
typedef struct Rectangle___struct *Rectangle;	// A rectangle
typedef struct Text___struct *Text;		// A text structure

// An Array is a dynamically extendible array that is bounds checked:
struct Array___struct {
    Unsigned available;		// Total number of availble elements
    Unsigned size;		// Total number of  in use
    Elements elements;		// Pointer to memory
};

// A Corner corresponds to one corner of a polyline:
struct Corner___struct {
    Long x;			// Next x
    Long y;			// Next y
    Long side_style;		// Side style
};

// A Footprint is an IC footprint:
struct Footprint___struct {
    String name;		// Name of footprint
    String author;		// Author of footprint
    String source;		// Footprint source
    String description;		// Footprint description 
    String units;		// Units for footpring
    Rectangle selection_rectangle; // Selection rectangle
    Text reference_text;	// Reference Text
    Text value_text;		// Value Text
    Rectangle centroid;		// Centroid (whatever that is)
    Unsigned number_of_pins;	// Number of Pins
    Array polylines;		// Polylines
    Array pins;			// Pins for footprint
};

// A Pad is one surface of a pin:
struct Pad___struct {
    Long shape;			// Pad shape
    Long width;			// Pad width
    Long length1;		// Pad length1
    Long length2;		// Pad length2
    Long corner_radius;		// Corner radius
};

// A Parse is used to parse input:
struct Parse___struct {
    String contents;		// File contents
    String file_name;		// File name
    Unsigned line_number;	// Current line number
    Unsigned offset;		// Offset into {string}
    Unsigned size;		// Size of string
};

// A Pin is one pin of a footprint:
struct Pin___struct {
    String name;		// Pin name
    Long hole_diameter;		// Hole diameter
    Long x;			// X coordinate
    Long y;			// Y coordinate
    Long angle;			// Angle (units?)
    Pad top;			// Top pad (or null)
    Pad inner;			// Inner pad (or null)
    Pad bottom;			// Bottom pad (or null)
};

// A Polyline is a sequence of connected line segments:
struct Polyline___struct {
    Long line_width;		// Line width
    Long start_x;		// Starting X
    Long start_y;		// Starting Y
    Logical close_polyline;	// Close the polyline
    Long close_style;		// Close style
    Array corners;		// Corners of polyline
};

// A Rectangle specifies a region of space:
struct Rectangle___struct {
    Long left;			// Left coordinate
    Long bottom;		// Bottom coordinate
    Long right;			// Right coordinate
    Long top;			// Top coordinate
};

// A Text specifies some text:
struct Text___struct {
    Long height;		// Height
    Long left;			// Left
    Long bottom;		// Bottom
    Long angle;			// Angle
    Long line_width;		// Line Width
};

// Routine types:
typedef Integer (*Compare_Routine)(Element, Element);

// Macros go here.  Macros are kept to a minimum:
#define new(Type) ((Type)Memory__allocate(sizeof(*((Type)0))))

// Routine definitions grouped alphabetically by type and operation:
Element Array__append(Array array,  Element element);
Array Array__create(Unsigned initial_size);
Element Array__fetch(Array array, Unsigned index);
Unsigned Array__size(Array array);
Element Array__store(Array array, Unsigned index, Element element);
void Array__trim(Array array, Unsigned new_size);

Corner Corner__parse(Parse parse);

Array Footprint__directory_read(Array footprints, String directory_name);
void Footprint__kicad_module_write(Footprint footprint, File mod_stream);	
void Footprint__kicad_write(Array footprints, String mod_file_name);
Footprint Footprint__parse(Parse parse);
Integer Footprint__name_compare(Footprint footprint1, Footprint footprint2);

Integer Integer__mils(Long micro_meter);

Memory Memory__allocate(Unsigned size);
Memory Memory__reallocate(Memory memory, Unsigned new_size);

Pad Pad__parse(Parse parse, String tag_name);

Parse Parse__create(String string, Unsigned size, String file_name);
void Parse__end_of_line(Parse parse);
void Parse__error(Parse parse, String error_message);
Long Parse__long(Parse parse);
Logical Parse__is_empty(Parse parse);
void Parse__new_lines(Parse parse);
String Parse__string(Parse parse);
Logical Parse__tag_match(Parse parse, String tag);
void Parse__white_space_skip(Parse parse);

Pin Pin__parse(Parse parse);

Polyline Polyline__parse(Parse parse);

Rectangle Rectangle__parse(Parse parse);

String String__create(Unsigned size);

void Text__kicad_write(Text text, Unsigned field_number, File mod_stream);
Text Text__parse(Parse parse);

// Main routine:
Integer main(
  Integer arguments_count,
  String *arguments)
{
    // Make sure that Long is 64 bits:
    assert (sizeof(Long) == 8);

    // Read in the libraries:
    Array least = Footprint__directory_read((Array)0, "IPC7351-Least");
    (void)fprintf(stderr, "least.size=%d\n", Array__size(least));
    Array nominal = Footprint__directory_read((Array)0, "IPC7351-Nominal");
    Array most = Footprint__directory_read((Array)0, "IPC7351-Most");

    // Write out KiCAD modules:
    Footprint__kicad_write(least, "IPC7351-Least.mod");
    Footprint__kicad_write(nominal, "IPC7351-Nominal.mod");
    Footprint__kicad_write(most, "IPC7351-Most.mod");

    // Select single footprint and write it out:
    Array test = Array__create(1);
    Unsigned index = 0;
    Unsigned nominal_size = Array__size(nominal);
    for (; index < nominal_size; index++) {
	Footprint footprint = (Footprint)Array__fetch(nominal, index);
	String name = footprint->name;
	if (strcmp(name, "QFP80P1200X1200X120-44N") == 0) {
	    Array__append(test, footprint);
	}
    }
    Footprint__kicad_write(test, "test.mod");

    return 0;
}


// {Array} routines:

Element Array__append(
  Array array,
  Element element)
{
    // This routine will append {element} to the end of {array}.
    // {element} is returned.

    // Pull some values out of {array}:
    Unsigned available = array->available;
    Unsigned size = array->size;
    Elements elements = array->elements;

    // Make sure we have enough space:
    if (size >= available) {
	// Double the size of {elements}:
        available = 2 * size;
	Element empty = (Element)0;
	elements =
	  (Elements)Memory__reallocate(elements, available * sizeof(empty));
	array->available = available;
	array->elements = elements;
    }
    
    // Stuff {element} onto the end of {array}:
    elements[size] = element;
    array->size = size + 1;

    return element;
}

Array Array__create(
  Unsigned initial_size)
{
    // This routine will create and return a new {Array} object that
    // can contain at least {initial_size}.

    // Make sure we allocate at least 1 element:
    if (initial_size == 0) {
	// Minimum {initial_size} is 1:
	initial_size = 1;
    }

    // Allocate the {Array} elements:
    Element empty = (Element)0;
    Elements elements =
      (Elements)Memory__allocate(sizeof(empty) * initial_size);
    
    // Zero out {elements}:
    Unsigned index = 0;
    for (; index < initial_size; index++) {
	elements[index] = empty;
    }

    // Create {array} and fill it in:
    Array array = new(Array);
    array->available = initial_size;
    array->size = 0;
    array->elements = elements;

    return array;
}

Element Array__fetch(
  Array array,
  Unsigned index)
{
    // This routine will return the {index}'th slot of {array}.

    assert(index < array->size);
    return array->elements[index];
}

Unsigned Array__size(
  Array array)
{
    // This routine will return the current size of {array}.

    return array->size;
}

Array Array__sort(
  Array array,
  Compare_Routine compare_routine)
{
    // This routine will sort the contents of {array} using {compare_routine}
    // to compare elements in {array}.  This algorithm takes O(N log N).

    // This code was written a long time ago and seems to work.  The
    // comments need some improvment...:

    Unsigned size = Array__size(array);
    Unsigned power = 0;
    Unsigned temp = 1;
    while (temp < size) {
	power++;
	temp <<= 1;
    }

    // We need a temporary area, so stash them on the end.
    Unsigned index = 0;
    while (index < size) {
	Element element = Array__fetch(array, index);
	(void)Array__append(array, element);
	index++;
    }

    // Figure out where to start sorting:
    Unsigned element1 = 0;
    Unsigned element2 = 0;
    if ((power & 1) == 1) {
	element1 = size;
	element2 = 0;
    } else {
	element1 = 0;
	element2 = size;
    }

    // Now sort pairs, then quads, then octettes, etc.:
    Unsigned step1 = 1;
    Unsigned step2 = 2;
    index = power;
    while (index != 0) {
	Unsigned index2 = element2;
	Unsigned index1a = element1;
	Unsigned index1b = element1 + step1;
	Unsigned offset = 0;
	while (offset < size) {
	    Unsigned count1a = step1;
	    Unsigned count1b = step1;
	    temp = size - offset;
	    if (temp < step1) {
		count1a = temp;
		count1b = 0;
	    } else {
		temp = temp - step1;
		if (temp < step1) {
		    count1b = temp;
		}
	    }

	    while (count1a != 0 && count1b != 0) {
		Element element1a = Array__fetch(array, index1a);
		Element element1b = Array__fetch(array, index1b);
		if (compare_routine(element1a, element1b) < 0) {
		    (void)Array__store(array, index2, element1a);
		    index1a++;
		    count1a--;
		} else {
		    (void)Array__store(array, index2, element1b);
		    index1b++;
		    count1b--;
		}
		index2++;
	    }

	    while (count1a != 0) {
		Array__store(array, index2, Array__fetch(array, index1a));
		index1a++;
		count1a--;
		index2++;
	    }
	    while (count1b != 0) {
		Array__store(array, index2, Array__fetch(array, index1b));
		index1b++;
		count1b--;
		index2++;
	    }
	    index1a += step1;
	    index1b += step1;
	    offset += step2;
	}
	Unsigned element_temp = element1;
	element1 = element2;
	element2 = element_temp;
	step1 <<= 1;
	step2 <<= 1;
	index--;
    }

    Array__trim(array, size);
 
    // Verify that we are properly sorted:
    for (index = 1; index < size; index++) {
	Element element_before = Array__fetch(array, index - 1);
	Element element_after = Array__fetch(array, index);
	assert (compare_routine(element_before, element_after) <= 0);
    }
}

Element Array__store(
  Array array,
  Unsigned index,
  Element element)
{
    // This routine will store {element} into the {index}'th slot of {array}.
    // {element} is returned.

    assert(index < array->size);
    array->elements[index] = element;
    return element;
}

void Array__trim(
  Array array,
  Unsigned new_size)
{
    // This routine will reduce the size of {array} to {new_size}.

    assert(new_size <= array->size);
    array->size = new_size;
}

// {Corner} routines:

Corner Corner__parse(
  Parse parse)
{
    // This routine will parse a "next_corner:" tag and return the resulting
    // {Corner} object.  If there is no "next_corner:" tag, null is returned.

    // See whether we have "next_corner:"
    Corner corner = (Corner)0;
    if (Parse__tag_match(parse, "next_corner:")) {
	// Parse the rest of "next_corner:"
	corner = new(Corner);
	corner->x = Parse__long(parse);
	corner->y = Parse__long(parse);
	corner->side_style = Parse__long(parse);
	Parse__end_of_line(parse);
    }

    return corner;
}

// {Footprint} routines:

Array Footprint__directory_read(
  Array footprints,
  String directory_name)
{
    // This routine will read all of the footprint files in {directory_name}
    // and append all of the {Footprint} objects in to an {Array} and
    // return it.  If {footprints} is non-null, is as the {Array} is
    // returned.
    
    // Make sure we a non-null {footprints}:
    if (footprints == (Array)0) {
	footprints = Array__create(0);
    }

    // We are only interested in files that end in ".fpl":
    String suffix = ".fpl";
    Unsigned suffix_size = strlen(suffix);

    // Open {directory_name}:
    Unsigned directory_name_size = strlen(directory_name);
    Directory directory = opendir(directory_name);
    assert (directory != (Directory)0);

    // Scan through {directory}:
    while (1) {
	// Read next {directory_entry}:
	Directory_Entry directory_entry = readdir(directory);
	if (directory_entry == (Directory_Entry)0) {
	    // Null {directory_entry} means we are done:
	    break;
	}	    

	// See whether {file_name} ends in {suffix}:				
	String file_name = directory_entry->d_name;
	Unsigned file_name_size = strlen(file_name);
	if (file_name_size > suffix_size &&
	  strcmp(file_name + file_name_size - suffix_size, suffix) == 0) {
	    // We have a file name that ends in {suffix}:

	    // Create {full_file_name} from {directory_name} and {file_name}:
	    Unsigned full_file_name_size =
	      directory_name_size + 1 + file_name_size;
	    String full_file_name = (String)malloc(full_file_name_size + 1);
	    assert (full_file_name != (String)0);
	    assert (sprintf(full_file_name, "%s/%s",
	      directory_name, file_name) == full_file_name_size);

	    // For debugging:
	    (void)printf("%s\n", full_file_name);

	    // Read in the whole file as a string:

	    // First open {full_file_name}:
	    File file = fopen(full_file_name, "r");
	    assert (file != (File)0);

	    // Get the file size by seeking to end, reading position
	    // and rewinding:
	    assert (fseek(file, 0, SEEK_END) == 0);
	    Unsigned file_size = ftell(file);
	    rewind(file);

	    // Allocate a string to read file contents into:
	    String file_contents = (String)String__create(file_size);

	    // Read in the entire file and terminate with a null:
	    assert (fread(file_contents, 1, file_size, file) == file_size);
	    file_contents[file_size] = '\0';

	    // Close {file}:
	    assert (fclose(file) == 0);

	    // Now parse {file_contents}:
	    Parse parse =
	      Parse__create(file_contents, file_size, full_file_name);

	    // Read in {Footprint}'s until there are no more:
	    while (1) {
		// Parse a {Footprint}:
		Footprint footprint = Footprint__parse(parse);

		// Null is returned if there are no more to be parsed:
		if (footprint == (Footprint)0) {
		    if (!Parse__is_empty(parse)) {
			// Remaining characters in {parse} mean problems:
			Parse__error(parse, "Footprint parse problem");
		    }
		    break;
		}

		// Append {footprint} to {footprints}:
		(void)Array__append(footprints, footprint);
	    }
	}  
    }

    // Close {directory}:
    assert (closedir(directory) == 0);

    return footprints;
}

void Footprint__kicad_write(
  Array footprints,
  String mod_file_name)
{
    // Sort {footprints} alphabetically by name:
    Array__sort(footprints, (Compare_Routine)Footprint__name_compare);

    // Open {mod_file_name}:
    File mod_stream = fopen(mod_file_name, "w");
    assert (mod_stream != (File)0);

    // Output header lines to {mod_stream}:
    (void)fprintf(mod_stream,
      "PCBNEW-LibModule-V1  Sat 01 Jan 2000 00:00:00 PM PDT\n");
    (void)fprintf(mod_stream, "# encoding utf-8\n");

    // Output index to {mod_stream}:
    (void)fprintf(mod_stream, "$INDEX\n");
    Unsigned size = Array__size(footprints);
    //FIXME: for now just write out one:
    Unsigned index = 0;
    for (index = 0; index < size; index++) {
        Footprint footprint = (Footprint)Array__fetch(footprints, index);
	(void)fprintf(mod_stream, "%s\n", footprint->name);
    }
    (void)fprintf(mod_stream, "$EndINDEX\n");

    // Now output each of the {footprints}:
    for (index = 0; index < size; index++) {
        Footprint footprint = (Footprint)Array__fetch(footprints, index);
	Footprint__kicad_module_write(footprint, mod_stream);	
    }

    // Close {mod_stream}:
    (void)fprintf(mod_stream, "$EndLIBRARY\n");    
    assert (fclose(mod_stream) == 0);
}

void Footprint__kicad_module_write(
  Footprint footprint,
  File mod_stream)
{
    // This routine will write {footprint} out to {mod_stream} in KiCAD .mod
    // file format.

    String name = footprint->name;
    (void)fprintf(mod_stream, "$Module %s\n", name);
    Unsigned timestamp = 0;
    Unsigned unclear = 0;
    (void)fprintf(mod_stream, "Po 0 0 0 15 %08x %08x ~~\n", timestamp, unclear);
    (void)fprintf(mod_stream, "Li %s\n", name);
    (void)fprintf(mod_stream, "Cd %s\n", footprint->description);
    (void)fprintf(mod_stream, "Kw CMS XXX\n");
    (void)fprintf(mod_stream, "Sc %08x\n", timestamp);
    (void)fprintf(mod_stream, "AR %s\n", name);
    (void)fprintf(mod_stream, "Op 0 0 0\n");
    (void)fprintf(mod_stream, "At SMD\n");

    Text__kicad_write(footprint->reference_text, 0, mod_stream);
    Text__kicad_write(footprint->value_text, 1, mod_stream);

    // Output each {Polyline} in {polylines}:
    Array polylines = footprint->polylines;
    Unsigned polylines_size = Array__size(polylines);
    Unsigned polylines_index = 0;
    for (; polylines_index < polylines_size; polylines_index++) {
	// Grab the {polylines_index}'th {Polyline} from {polylines}:
	Polyline polyline = (Polyline)Array__fetch(polylines, polylines_index);

	// Extract some values from {polyline}:	
	Integer line_width = Integer__mils(polyline->line_width);
	Integer start_x = Integer__mils(polyline->start_x);
	Integer start_y = Integer__mils(polyline->start_y);
	Logical close_polyline = polyline->close_polyline;
	Array corners = polyline->corners;

	// Output one line for each {Corner} in corners}:
	Integer x = start_x;
	Integer y = start_y;
	Unsigned corners_size = Array__size(corners);
	Unsigned corners_index = 0;
	for (; corners_index < corners_size; corners_index++) {
	    // Grab the {corners_index}'th {Corner} from {corners}:
	    Corner corner = (Corner)Array__fetch(corners, corners_index);

	    // Get the two line end points ready:
	    Integer previous_x = x;
	    Integer previous_y = y;
	    x = Integer__mils(corner->x);
	    y = Integer__mils(corner->y);

	    // Output a KiCAD line:
	    (void)fprintf(mod_stream, "DS %d %d %d %d %d 21\n",
	      previous_x, -previous_y, x, -y, line_width);
	}

	// Output a closing line if needed:
	if (polyline->close_polyline) {
	  (void)fprintf(mod_stream, "DS %d %d %d %d %d 21\n",
	    x, -y, start_x, -start_y, line_width);
	}
    }

    // Output each {Pin} in {pins}:
    Array pins = footprint->pins;
    Unsigned pins_size = Array__size(pins);
    Unsigned pins_index = 0;
    for (; pins_index < pins_size; pins_index++) {
	// Grab the {pins_index}'th {Pin} in {pins}:
	Pin pin = (Pin)Array__fetch(pins, pins_index);

	// Grab some values from {pin}:
	String name = pin->name;
	Integer hole_diameter = Integer__mils(pin->hole_diameter);
	Integer x = Integer__mils(pin->x);
	Integer y = Integer__mils(pin->y);
	Long angle = pin->angle;
	Pad top = pin->top;
	Pad inner = pin->inner;
	Pad bottom = pin->bottom;

	(void)fprintf(mod_stream, "$PAD\n");
	if (1) {
	    // Surface mount:
	    Long shape = top->shape;
	    Long width = top->width;
	    Long length1 = top->length1;
	    Long length2 = top->length2;
	    Long corner_radius = top->corner_radius;

	    Integer dx = Integer__mils(width);
	    Integer dy = Integer__mils(length1 + length2);

	    if (angle == 0) {
		(void)fprintf(mod_stream, "Sh \"%s\" R %d %d 0 0 0\n",
		  name, dy, dx);
	    } else if (angle == 90) {
		(void)fprintf(mod_stream, "Sh \"%s\" R %d %d 0 0 0\n",
		  name, dx, dy);
	    } else {
		(void)fprintf(stderr, "Pad Angle=%d\n", (Integer)angle);
	    }
	    (void)fprintf(mod_stream, "Dr 0 0 0\n");
	    Unsigned layer_mask = 0x888000;
	    (void)fprintf(mod_stream, "At SMD N %08x\n", layer_mask);
	    (void)fprintf(mod_stream, "Ne 0 \"\"\n");
	    (void)fprintf(mod_stream, "Po %d %d\n", x, -y);
	}
	(void)fprintf(mod_stream, "$EndPAD\n");
    }

    // Close the module:
    (void)fprintf(mod_stream, "$EndMODULE  %s\n", name);
}

Integer Footprint__name_compare(
  Footprint footprint1,
  Footprint footprint2)
{
    // This routine will return -1, 0, 1 depending upon whether the name
    // {footprint1} should occure before, at, or after {footprint2}.

    return strcmp(footprint1->name, footprint2->name);
}

Footprint Footprint__parse(
  Parse parse)
{
    // This routine will parse one {Footprint} from {parse}.  null is
    // returned if there is now {Footprint} to be read.

    Footprint footprint = (Footprint)0;

    if (Parse__tag_match(parse, "name:")) {
	// We have a footprint:
	footprint = new(Footprint);

	// Parse the {name}:
	String name = Parse__string(parse);
	Parse__end_of_line(parse);
	footprint->name = name;

	// Parse the {author}:
	String author = (String)0;
	if (Parse__tag_match(parse, "author:")) {
	    author = Parse__string(parse);
	    Parse__end_of_line(parse);
	}
	footprint->author = author;

	// Parse the {source}:
	String source = (String)0;
	if (Parse__tag_match(parse, "source:")) {
	    source = Parse__string(parse);
	    Parse__end_of_line(parse);
	}
	footprint->source = source;

	// Parse {description}:
	String description = (String)0;
	if (Parse__tag_match(parse, "description:")) {
	    description = Parse__string(parse);
	    Parse__end_of_line(parse);
	}
	footprint->description = description;

	// Parse {units}:
	String units = (String)0;
	if (Parse__tag_match(parse, "units:")) {
	    units = Parse__string(parse);
	    Parse__end_of_line(parse);
	}
	footprint->units = units;

	// Parse {selection_rectangle}:
	Rectangle selection_rectangle = (Rectangle)0;
	if (Parse__tag_match(parse, "sel_rect:")) {
	    selection_rectangle = Rectangle__parse(parse);
	    Parse__end_of_line(parse);
	}
	footprint->selection_rectangle = selection_rectangle;

	// Parse {reference_text}:
	Text reference_text = (Text)0;
	if (Parse__tag_match(parse, "ref_text:")) {
	    reference_text = Text__parse(parse);
	    Parse__end_of_line(parse);
	}
	footprint->reference_text = reference_text;

	// Parse {value_text}:
	Text value_text = (Text)0;
	if (Parse__tag_match(parse, "value_text:")) {
	    value_text = Text__parse(parse);
	    Parse__end_of_line(parse);
	}
	footprint->value_text = value_text;

	// Parse {centroid}:
	Rectangle centroid = (Rectangle)0;
	if (Parse__tag_match(parse, "centroid:")) {
	    centroid = Rectangle__parse(parse);
	    Parse__end_of_line(parse);
	}
	footprint->centroid = centroid;

	// Now parse any polylines:
	Array polylines = Array__create(0);
	while (1) {
	    Polyline polyline = Polyline__parse(parse);
	    if (polyline == (Polyline)0) {
		// No more polylines:
		break;
	    }
	    // We got a {polyline}:
	    (void)Array__append(polylines, polyline);
	}
	footprint->polylines = polylines;

	// Parse the {n_pins}:
	Long n_pins = 0;
	if (Parse__tag_match(parse, "n_pins:")) {
	    n_pins = Parse__long(parse);
	    Parse__end_of_line(parse);
	}

        // Parse the pins:
	Array pins = Array__create(n_pins);
	while (1) {
	    Pin pin = Pin__parse(parse);
	    if (pin == (Pin)0) {
		// No more {Pin}'s:
		break;
	    }
	    // We have a {pin}:
	    (void)Array__append(pins, pin);
	}
	footprint->pins = pins;

	// Slurp off any blank lines:
	Parse__new_lines(parse);
    }

    return footprint;
}

// {Long} routines:

Integer Integer__mils(
  Long micro_meter)
{
    // This routine will return {micro_meter} converted to tenth mils.

    // 1inch = 1000tmil (tmil = tenth mil)
    // 1inch = 25.4mm = 25400um
    // 1um * (10000tmil/25400um) * (10000tmil/1in)

    // inch_to_micro_meter = 25400000;
    // inch_to_mil = 1000;
    // micro_meter_to_mil = inch_to_mil / inch_to_micro_meter =
    //                    = 25400000 / 1000
    //                    = 25400
    // Since we want tenth mil, we use 2540:
    return (Integer)(micro_meter / 2540LL);
}


// {Memory} routines:

Memory Memory__allocate(
  Unsigned size)
{
    // This routine will allocate and return a chunk of {Memory}
    // of {size} bytes.

    Memory memory = (Memory)malloc(size);
    assert(memory != (Memory)0);
    return memory;
}

Memory Memory__reallocate(
  Memory memory,
  Unsigned new_size)
{
    // This routine will return a chunk of memory that is {size} bytes
    // in length.  The previous contents of {memory} are retained.

    memory = (Memory)realloc(memory, new_size);
    assert(memory != (Memory)0);
    return memory;
}

// {Pad} routines:

Pad Pad__parse(
  Parse parse,
  String tag_name)
{
  // This routine will parse a {Pad} using {parse} that matches {tag_name}.

    Pad pad = (Pad)0;
    if (Parse__tag_match(parse, tag_name)) {
	pad = new(Pad);
	pad->shape = Parse__long(parse);
	pad->width = Parse__long(parse);
	pad->length1 = Parse__long(parse);
	pad->length2 = Parse__long(parse);
	pad->corner_radius = Parse__long(parse);
	Parse__end_of_line(parse);
    }
    return pad;
}

// {Parse} routines:

Parse Parse__create(
  String contents,
  Unsigned size,
  String file_name)
{
    // This routine will return a new {Parse} object initialized to
    // {contents} of {size} bytes.

    Parse parse = new(Parse);
    parse->contents = contents;
    parse->file_name = file_name;
    parse->line_number = 1;
    parse->offset = 0;
    parse->size = size;
    return parse;
}

void Parse__error(
  Parse parse,
  String error_message)
{
    // This routine will print {error_message} using {parse} to provide
    // the file name and line number;

  (void)fprintf(stderr, "%s:%d: %s\n",
     parse->file_name, parse->line_number, error_message);
}

void Parse__end_of_line(
  Parse parse)
{
    // This routine will parse an end of line:

    // Skip over any white space:
    Parse__white_space_skip(parse);

    // Grab some values from {parse}:
    String contents = parse->contents;
    Unsigned offset = parse->offset;
    Unsigned size = parse->size;

    Unsigned errors = 0;
    while (offset < size) {
	// Grab next character:
	Character character = contents[offset];
	offset++;

	// Check {character}:
	if (character == '\n') {
	    // We found the end; bump line number:
	    parse->line_number++;
	    break;
	} else if (character == '\r') {
	    // Ignore carriage returns:
	} else {
	    // We have a bogus character; increment {errors}:
	    errors++;
	}
    }
    
    // Print any errors:
    if (errors != 0) {
	Parse__error(parse, "Garbage at end of line");
    }

    // Restore {offset}:
    parse->offset = offset;
}

Logical Parse__is_empty(
  Parse parse)
{
    // This routine will return 1 if {parse} is empty and 0 otherwise.

    return parse->offset >= parse->size;
}

Long Parse__long(
  Parse parse)
{
    // This routine will parse a {Long} from {parse}:

    Long result = 0;

    // Skip over any white space:
    Parse__white_space_skip(parse);

    // Grab some values from {parse}:
    String contents = parse->contents;
    Unsigned offset = parse->offset;
    Unsigned size = parse->size;

    // Check for minus sign:
    Logical negative = 0;
    if (offset < size && contents[offset] == '-') {
	offset++;
	negative = 1;
    }

    // Process digits of number:
    Logical error = 1;
    while (offset < size) {
	Character character = contents[offset];
	if ('0' <= character && character <= '9') {
	    result = result * 10 + (character - '0');
	    offset++;
	    error = 0;
	} else {
	    break;
	}
    }

    // Indicate any errors:
    if (error) {
	Parse__error(parse, "Bad number");
    }

    // Deal with minus sign:
    if (negative) {
	result = -result;
    }

    // Restore {offset} back into {parse}:
    parse->offset = offset;

    return result;
}

void Parse__new_lines(
  Parse parse)
{
    // This routine will swallow up as many blank lines as possible:

    // Grab some values out of {parse}:
    String contents = parse->contents;
    Unsigned offset = parse->offset;
    Unsigned size = parse->size;

    // Iterate over white space and new-lines:
    while (offset < size) {
	Character character = contents[offset];
	if (character == '\r' || character == ' ' || character == '\t') {
	    // White space or carraige return:
	    offset++;
	} else if (character == '\n') {
	    // End of line:
	    offset++;
	    parse->line_number++;
	    break;
	} else {
	    // Something other that whitespace or end of line:
	    break;
	}
     }

    // Restore {offset}:
    parse->offset = offset;
}

String Parse__string(
  Parse parse)
{
    // This routine will parse an end of line:

    // Skip over any white space:
    Parse__white_space_skip(parse);

    // Grab some values from {parse}:
    String contents = parse->contents;
    Unsigned offset = parse->offset;
    Unsigned size = parse->size;

    String string = (String)0;
    if (offset < size) {
	// Keep track of beginning and end of string in {contents}:
	Unsigned start_index = offset;
	Unsigned end_index = offset;

	// Read first character:
	Character character = contents[offset];
	offset++;

	// Check for double quoted string:
	if (character == '"') {
	    start_index = offset;
	    // Look for closing double quote:
	    while (offset < size) {
		Character character = contents[offset];
		if (character == '"') {
		    // We found the closing double quote:
		    end_index = offset;
		    offset++;
		    break;
		} else if (character == '\n') {
		    // Untermianted string:
		    Parse__error(parse, "Missing closing quote in string");
		} else {
		    // Keep looking:
		    offset++;
		}
	    }
	} else {
	    // We have a white space terminated string:
	    while (offset < size) {
		// Read nextf {character}:
		character = contents[offset];
		offset++;

		if (character == ' ' ||
		  character == '\n' || character == '\r') {
		    // We found the end:
		    offset--;
		    end_index = offset;
		    break;
		}
	    }
	}

	// Create the string if we have one:
	if (end_index > start_index) {
	    //  Compute the string size:
	    Unsigned string_size = end_index - start_index;

	    // Create the string:
	    string = String__create(string_size);

	    // Copy the contents in:
	    (void)strncpy(string, contents + start_index, string_size);

	    // Make sure the new string is null terminated:
	    string[string_size] = '\0';
	}
    } else {
	// We have a problem:
	Parse__error(parse, "Missing string");
    }

    // Restore {offset} back into {parse}:
    parse->offset = offset;

    return string;
}

Logical Parse__tag_match(
  Parse parse,
  String tag)
{
    // This routine will return 1 if {tag} matches the next batch of
    // text in {parse}.  {tag} should be terminated by a colon.
    // When a match occurs, the tage is removed from {parse}.

    // Skip over any white space:
    Parse__white_space_skip(parse);

    // Compute length of {tag}:
    Unsigned tag_size = strlen(tag);

    // Grab some values from {parse}:
    Unsigned size = parse->size;
    Unsigned offset = parse->offset;
    String contents = parse->contents;

    // See if we have a matching tag:
    Logical result = 0;
    Unsigned remaining = offset - size;
    if (tag_size <= remaining) {
	if (strncmp(contents + offset, tag, tag_size) == 0) {
	    // We have a match; push {offset} forward:
	    parse->offset = offset + tag_size;
	    result = 1;
	}
    }

    return result;
}

void Parse__white_space_skip(
  Parse parse)
{
    // This routine will advance {parse} over any white space.

    // Grab some values out of {parse}:
    String contents = parse->contents;
    Unsigned offset = parse->offset;
    Unsigned size = parse->size;

    // Iterate across {contents} starting at {offset} until the end
    // reached or until there are no more white space characters:
    while (offset < size) {
	Character character = contents[offset];
	if (character == ' ' || character == '\t') {
	    // Got some white space; keep going:
	    offset++;
	} else {
	    // Not white space; quit:
	    break;
	}
    }

    // Restore {offset} back into {parse}:
    parse->offset = offset;
}

// {Pin} routines:

Pin Pin__parse(
  Parse parse)
{
    // This routine will parse a "pin:" tag:

    Pin pin = (Pin)0;
    if (Parse__tag_match(parse, "pin:")) {
	pin = new(Pin);
	pin->name = Parse__string(parse);
	pin->hole_diameter = Parse__long(parse);
	pin->x = Parse__long(parse);
	pin->y = Parse__long(parse);
	pin->angle = Parse__long(parse);
	Parse__end_of_line(parse);

	pin->top = Pad__parse(parse, "top_pad:");
	pin->inner = Pad__parse(parse, "inner_pad:");
	pin->bottom = Pad__parse(parse, "bottom_pad:");
    }

    return pin;
}

// {Polyline} routines:

Polyline Polyline__parse(
  Parse parse)
{
    // This routine will parse an "outline_polyline:" tag from {parse}:
    // If there is no "outline_polyline:", null is returned.

    // See whether we have a "outline_polyline:"
    Polyline polyline = (Polyline)0;
    if (Parse__tag_match(parse, "outline_polyline:")) {
	// Parse the rest of "outline_polyline:"
	polyline = new(Polyline);
	polyline->line_width = Parse__long(parse);
	polyline->start_x = Parse__long(parse);
	polyline->start_y = Parse__long(parse);
	Parse__end_of_line(parse);

	// Parse any "next_corner:" tags:
	Array corners = Array__create(0);
	while (1) {
	    // Grab all of the "next_corner:" tags:
	    Corner corner = Corner__parse(parse);
	    if (corner == (Corner)0) {
		// No more "next_corner:" tags:
		break;
	    }

	    // Got one; append it to {corners}:
	    (void)Array__append(corners, corner);
	}
	polyline->corners = corners;

	// Now see if there is a "close_polyline:" tag:
        polyline->close_polyline = 0;
        polyline->close_style = 0;
	if (Parse__tag_match(parse, "close_polyline:")) {
	    // Yes, there is:
	    polyline->close_polyline = 1;
	    polyline->close_style = Parse__long(parse);
	    Parse__end_of_line(parse);
	}
    }

    return polyline;
}

// {Rectangle} routines:

Rectangle Rectangle__parse(
  Parse parse)
{
    // This routine will parse and return a {Rectangle} from {parse}.

    // Create {rectangle}:
    Rectangle rectangle = new(Rectangle);

    // Parse the values:
    rectangle->left = Parse__long(parse);
    rectangle->bottom = Parse__long(parse);
    rectangle->right = Parse__long(parse);
    rectangle->top = Parse__long(parse);

    return rectangle;
}

// {String} routines:

String String__create(
  Unsigned size)
{
    // This routine will create a string that can contain {size} characters:

    // Allocate the string:
    String string = (String)Memory__allocate(size + 1);

    // Terminate the string:
    string[size] = '\0';

    return string;
}

// {Text} routines:

void Text__kicad_write(
  Text text,
  Unsigned field_number,
  File mod_stream)
{
    // This routine ...

    Unsigned x_position = 0;
    Unsigned y_position = 0;
    Unsigned x_size = 400;
    Unsigned y_size = 400;
    Unsigned pen_width = 80;

    (void)fprintf(mod_stream, "T%d %d %d %d %d 0 %d N V 21 N %s\n",
      field_number, x_position,  y_position,
      x_size, y_size, pen_width, "~");
}

Text Text__parse(
  Parse parse)
{
    Text text = new(Text);
    text->height = Parse__long(parse);
    text->left = Parse__long(parse);
    text->bottom = Parse__long(parse);
    text->angle = Parse__long(parse);
    text->line_width = Parse__long(parse);

    return text;
}
