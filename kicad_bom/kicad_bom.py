#
# Python script to generate BOM in multiple formats from a KiCad generic netlist.
#
import kicad_netlist_reader
import os
import csv


class KicadBom:
    self._netlist_ext = '.xml'

    def find_netlist_path(self,netlist_path=None):
        search_path = None
        if (netlist_path is None) or (not os.path.exists(netlist_path)):
            search_path = os.getcwd()
        elif os.path.isdir(netlist_path):
            search_path = netlist_path
        else:
            (root,ext) = os.path.splitext(netlist_path)
            if ext == self._netlist_ext:
                return netlist_path
            else:
                return None
        for root, dirs, files in os.walk(search_path):
            for f in files:
                if f.endswith(self._netlist_ext):
                    return os.path.join(root,f)
        return None

    def read_netlist(self,netlist_path=None):
        netlist_path = self.find_netlist_path(netlist_path)
        if netlist_path is None:
            return None
        print("Processing: {0}".format(netlist_path))

        # Generate an instance of a generic netlist and load the netlist tree.
        netlist = kicad_netlist_reader.netlist(netlist_path)

        # subset the components to those wanted in the BOM, controlled
        # by <configure> block in kicad_netlist_reader.py
        components = netlist.getInterestingComponents()

        # Header providing general information
        # source = os.path.basename(net.getSource())
        # f.write('Source: ' + source + '\n')
        # f.write('Date: ' + str(net.getDate()) + '\n')
        # f.write('Tool: ' + str(net.getTool()) + '\n')
        # f.write('Component Count: ' + str(len(components)) + '\n')
        # f.write('\n')

        compfields = net.gatherComponentFieldUnion(components)
        compfields -= set(['PartCount'])
        partfields = net.gatherLibPartFieldUnion()
        # remove Reference, Value, Datasheet, and Footprint, they will come from 'columns' below
        partfields -= set(['Reference','Value','Datasheet','Footprint','PartCount'])

        columnset = compfields | partfields     # union

        # prepend an initial 'hard coded' list and put the enchillada into list 'columns'
        columns = ['Item','Reference(s)','Value','Quantity'] + sorted(list(columnset))

        # Get all of the components in groups of matching parts + values
        # (see kicad_netlist_reader.py)
        grouped = net.groupComponents(components)


        # Output component information organized by group, aka as collated:
        row = []
        for c in columns:
            row.append(c)
        out.writerow(row)

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
            # columns = ['Item','Reference(s)','Value','Quantity'] + sorted(list(columnset))
            item += 1
            row.append(item)
            row.append(refs);
            row.append(c.getValue())
            part_count = 1
            try:
                part_count = int(net.getGroupField(group,'PartCount'))
            except ValueError:
                pass
            row.append(part_count*len(group))

            # from column 4 upwards, use the fieldnames to grab the data
            for field in columns[4:]:
                row.append( net.getGroupField(group, field) );

            out.writerow(row)

        f.close()

    def generate_boms(self,xml_path=None):
        # Open a file to write to, if the file cannot be opened output to stdout
        # instead
        try:
            output_dir = os.path.join(os.path.dirname(input_path),'bom')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir,'bom_pcb.csv')
            print('Creating: {0}'.format(output_path))
            f = open(output_path,'w',newline='\n')
        except IOError:
            e = "Can't open output file for writing: " + output_path
            print(__file__,":",e,sys.stderr)
            f = sys.stdout

        # Create a new csv writer object to use as the output formatter
        out = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL )

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
                print('Creating: {0}'.format(filename))
                output_path = os.path.join(output_dir,filename)
                f = open(output_path,'w',newline='\n')
                # Create a new csv writer object to use as the output formatter
                out = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL )
            except IOError:
                e = "Can't open output file for writing: " + output_path
                print(__file__,":",e,sys.stderr)
                f = sys.stdout

            for group in grouped:
                try:
                    if vendor == net.getGroupField(group,'Vendor'):
                        part_count = 1
                        try:
                            part_count = int(net.getGroupField(group,'PartCount'))
                        except ValueError:
                            pass
                        del row[:]
                        row.append(part_count*len(group))
                        row.append(net.getGroupField(group,'PartNumber'))
                        out.writerow(row)
                except:
                    pass


            f.close()

def generate_boms():
    kb = KicadBom()
    kb.generate_boms()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    generate_boms()
