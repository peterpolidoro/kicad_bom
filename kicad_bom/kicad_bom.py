#
# Python script to generate BOM in multiple formats from a KiCad generic netlist.
#

from __future__ import print_function

import kicad_netlist_reader
import sys
import csv
import os
import shutil
# import PyOrgMode
# use PyOrgMode someday, but not developed enough at the moment.

def generate_boms():
    if len(sys.argv) != 2:
        print("Usage ", __file__, "<netlist.xml>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]

    # Generate an instance of a generic netlist, and load the netlist tree from
    # the command line option. If the file doesn't exist, execution will stop
    net = kicad_netlist_reader.netlist(input_path)

    # Open a file to write to, if the file cannot be opened output to stdout
    # instead
    try:
        output_dir = os.path.join(os.path.dirname(input_path),'bom')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir,'bom_pcb.csv')
        # if os.path.exists(output_path):
        #     shutil.copyfile(output_path,output_path+'.bck')
        f = open(output_path, 'w')
    except IOError:
        e = "Can't open output file for writing: " + output_path
        print(__file__,":",e,sys.stderr)
        f = sys.stdout

    # subset the components to those wanted in the BOM, controlled
    # by <configure> block in kicad_netlist_reader.py
    components = net.getInterestingComponents()

    # Header providing general information
    # source = os.path.basename(net.getSource())
    # f.write('Source: ' + source + '\n')
    # f.write('Date: ' + str(net.getDate()) + '\n')
    # f.write('Tool: ' + str(net.getTool()) + '\n')
    # f.write('Component Count: ' + str(len(components)) + '\n')
    # f.write('\n')

    compfields = net.gatherComponentFieldUnion(components)
    partfields = net.gatherLibPartFieldUnion()

    # remove Reference, Value, Datasheet, and Footprint, they will come from 'columns' below
    partfields -= set(['Reference','Value','Datasheet','Footprint'])

    columnset = compfields | partfields     # union

    # prepend an initial 'hard coded' list and put the enchillada into list 'columns'
    columns = ['Item','Reference(s)','Value','Footprint','Quantity'] + sorted(list(columnset))

    # Create a new csv writer object to use as the output formatter
    out = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL )

    # override csv.writer's writerow() to support utf8 encoding:
    def writerow(acsvwriter,columns):
        utf8row = []
        for col in columns:
            utf8row.append(str(col).encode('utf8'))
        acsvwriter.writerow(utf8row)

    # Get all of the components in groups of matching parts + values
    # (see kicad_netlist_reader.py)
    grouped = net.groupComponents(components)


    # Output component information organized by group, aka as collated:
    row = []
    for c in columns:
        row.append(c)
    writerow(out,row)

    item = 0
    for group in grouped:
        del row[:]
        refs = ""

        # Add the reference of every component in the group and keep a reference
        # to the component so that the other data can be filled in once per group
        for component in group:
            if len(refs) > 0:
                refs += " "
            refs += component.getRef()
            c = component

        # Fill in the component groups common data
        # columns = ['Item','Reference(s)','Value','Footprint','Quantity'] + sorted(list(columnset))
        item += 1
        row.append(item)
        row.append(refs);
        row.append(c.getValue())
        row.append(c.getFootprint())
        row.append(len(group))

        # from column 4 upwards, use the fieldnames to grab the data
        for field in columns[4:]:
            row.append( net.getGroupField(group, field) );

        writerow(out,row)

    f.close()

    # Create vendor set
    vendor_set = set()
    for group in grouped:
        try:
            vendor = net.getGroupField(group,'Vendor')
            vendor_set |= set([vendor])
        except:
            pass

    # Make order csv file for each vendor
    for vendor in vendor_set:
        # Open a file to write to, if the file cannot be opened output to stdout
        # instead
        try:
            output_dir = os.path.join(os.path.dirname(input_path),'bom')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename = str(vendor) + '_order_pcb.csv'
            output_path = os.path.join(output_dir,filename)
            f = open(output_path, 'w')
            # Create a new csv writer object to use as the output formatter
            out = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL )
        except IOError:
            e = "Can't open output file for writing: " + output_path
            print(__file__,":",e,sys.stderr)
            f = sys.stdout

        for group in grouped:
            del row[:]
            try:
                if vendor == net.getGroupField(group,'Vendor'):
                    row.append(len(group))
                    row.append(net.getGroupField(group,'PartNumber'))
            except:
                pass

            writerow(out,row)

        f.close()

