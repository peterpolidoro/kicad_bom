#
# Python script to generate BOM in multiple formats from a KiCad generic netlist.
#
import kicad_netlist_reader
import os
import csv


class KicadBom:
    def __init__(self):
        self._netlist_ext = '.xml'
        self._netlist_path = None
        self._netlist = None
        self._grouped_components = None
        self._column_names = None

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

    def _read_netlist(self,netlist_path=None):
        self._netlist_path = self.find_netlist_path(netlist_path)
        if self._netlist_path is None:
            return None

        # Generate an instance of a generic netlist and load the netlist tree.
        self._netlist = kicad_netlist_reader.netlist(self._netlist_path)

        # subset the components to those wanted in the BOM, controlled
        # by <configure> block in kicad_netlist_reader.py
        components = self._netlist.getInterestingComponents()

        compfields = self._netlist.gatherComponentFieldUnion(components)
        compfields -= set(['PartCount'])
        partfields = self._netlist.gatherLibPartFieldUnion()
        # remove Reference, Value, Datasheet, and Footprint, they will come from 'columns' below
        partfields -= set(['Reference','Value','Datasheet','Footprint','PartCount'])

        columnset = compfields | partfields     # union

        # prepend an initial 'hard coded' list and put the enchillada into list 'columns'
        self._column_names = ['Item','Reference(s)','Value','Quantity'] + sorted(list(columnset))

        # Get all of the components in groups of matching parts + values
        # (see kicad_netlist_reader.py)
        self._grouped_components = self._netlist.groupComponents(components)

    def get_bom_from_netlist(self,netlist_path=None):
        if (self._netlist_path is None) or (netlist_path is not None):
            self._read_netlist(netlist_path)
            if self._netlist_path is None:
                return []

        # Create header row
        row = []
        for c in self._column_names:
            row.append(c)

        # Create bom
        bom = []
        bom.append(row)

        item = 0
        for group in self._grouped_components:
            row = []
            refs = ""

            # Add the reference of every component in the group and keep a reference
            # to the component so that the other data can be filled in once per group
            for component in group:
                if len(refs) > 0:
                    refs += " "
                refs += component.getRef()
                c = component

            # Fill in the component groups common data
            # self._column_names = ['Item','Reference(s)','Value','Quantity'] + sorted(list(columnset))
            item += 1
            row.append(item)
            row.append(refs);
            row.append(c.getValue())
            part_count = 1
            try:
                part_count = int(self._netlist.getGroupField(group,'PartCount'))
            except ValueError:
                pass
            row.append(part_count*len(group))

            # from column 4 upwards, use the fieldnames to grab the data
            for field in self._column_names[4:]:
                row.append( self._netlist.getGroupField(group, field) );
            bom.append(row)

        return bom

    def get_vendor_orders_from_netlist(self,netlist_path=None):
        if (self._netlist_path is None) or (netlist_path is not None):
            self._read_netlist(netlist_path)
            if self._netlist_path is None:
                return []

        # Create vendor set
        vendor_set = set()
        for group in self._grouped_components:
            try:
                vendor = self._netlist.getGroupField(group,'Vendor')
                vendor_set |= set([vendor])
            except:
                pass

        vendor_orders = {}
        for vendor in vendor_set:
            order = []
            for group in self._grouped_components:
                try:
                    if vendor == self._netlist.getGroupField(group,'Vendor'):
                        part_count = 1
                        try:
                            part_count = int(self._netlist.getGroupField(group,'PartCount'))
                        except ValueError:
                            pass
                        row = []
                        row.append(part_count*len(group))
                        row.append(self._netlist.getGroupField(group,'PartNumber'))
                        order.append(row)
                except ValueError:
                    pass
            vendor_orders[vendor] = order
        return vendor_orders

    def save_boms_to_files(self,netlist_path=None):
        if (self._netlist_path is None) or (netlist_path is not None):
            self._read_netlist(netlist_path)
            if self._netlist_path is None:
                return []

        output_dir = os.path.join(os.path.dirname(self._netlist_path),'bom')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        bom = self.get_bom_from_netlist()
        bom_filename = 'bom_pcb.csv'
        bom_output_path = os.path.join(output_dir,bom_filename)
        with open(bom_output_path,'w') as f:
            bom_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
            for row in bom:
               bom_writer.writerow(row)

        vendor_orders = self.get_vendor_orders_from_netlist()
        for vendor in vendor_orders:
            vendor_order_filename = str(vendor) + '_order_pcb.csv'
            vendor_order_output_path = os.path.join(output_dir,vendor_order_filename)
            with open(vendor_order_output_path,'w') as f:
                vendor_order_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
                vendor_order = vendor_orders[vendor]
                for row in vendor_order:
                   vendor_order_writer.writerow(row)


def save_boms_to_files():
    kb = KicadBom()
    kb.save_boms_to_files()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    save_boms_to_files()
