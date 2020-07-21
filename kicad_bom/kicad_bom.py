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
        partfields = self._netlist.gatherLibPartFieldUnion()
        partfields -= set(['Reference','Value','Datasheet','Footprint'])

        additional_columns = compfields | partfields     # union

        self._column_names = ['Item','Reference(s)','Quantity']
        self._base_column_length = len(self._column_names)
        if 'Manufacturer' in additional_columns:
            self._column_names.append('Manufacturer')
        if 'Manufacturer Part Number' in additional_columns:
            self._column_names.append('Manufacturer Part Number')
        if 'Vendor' in additional_columns:
            self._column_names.append('Vendor')
        if 'Vendor Part Number' in additional_columns:
            self._column_names.append('Vendor Part Number')
        if 'Description' in additional_columns:
            self._column_names.append('Description')
        if 'Package' in additional_columns:
            self._column_names.append('Package')

        # Get all of the components in groups of matching parts + values
        # (see kicad_netlist_reader.py)
        self._grouped_components = self._netlist.groupComponents(components)

    def _update_netlist(self,netlist_path=None):
        if (self._netlist_path is None) or (netlist_path is not None):
            self._read_netlist(netlist_path)

    def get_bom_from_netlist(self,netlist_path=None):
        self._update_netlist(netlist_path)
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

            group_with_part_number = False
            for field in self._column_names[self._base_column_length:]:
                value = self._netlist.getGroupField(group, field)
                if ('Part Number' in field) and value:
                    group_with_part_number = True

            if not group_with_part_number:
                continue

            # Add the reference of every component in the group and keep a reference
            # to the component so that the other data can be filled in once per group
            for component in group:
                if len(refs) > 0:
                    refs += " "
                refs += component.getRef()
                c = component

            # Fill in the component groups common data
            item += 1
            row.append(item)
            row.append(refs);
            row.append(self._get_quantity_from_group(group))

            for field in self._column_names[self._base_column_length:]:
                value = self._netlist.getGroupField(group, field)
                row.append(value)

            bom.append(row)

        return bom

    def _get_quantity_from_group(self,group):
        count = len(group)
        try:
            quantity = int(self._netlist.getGroupField(group,'Quantity'))
        except ValueError:
            quantity = 1
        quantity *= count
        print('quantity =', quantity)
        return quantity



    def get_vendors_parts_from_netlist(self,netlist_path=None):
        self._update_netlist(netlist_path)
        if self._netlist_path is None:
            return {}

        # Create vendor set
        vendor_set = set()
        for group in self._grouped_components:
            try:
                vendor = self._netlist.getGroupField(group,'Vendor')
                if vendor:
                    vendor_set |= set([vendor])
            except:
                pass

        vendors_parts = {}
        for vendor in vendor_set:
            vendor_parts = []
            for group in self._grouped_components:
                try:
                    if vendor == self._netlist.getGroupField(group,'Vendor'):
                        row = []
                        row.append(self._get_quantity_from_group(group))
                        row.append(self._netlist.getGroupField(group,'Vendor Part Number'))
                        vendor_parts.append(row)
                except ValueError:
                    pass
            vendors_parts[vendor] = vendor_parts
        return vendors_parts

    def save_bom_csv_file(self,netlist_path=None):
        self._update_netlist(netlist_path)
        if self._netlist_path is None:
            return

        output_dir = os.path.join(os.path.dirname(self._netlist_path),'bom')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        bom = self.get_bom_from_netlist()
        bom_filename = 'bom.csv'
        bom_output_path = os.path.join(output_dir,bom_filename)
        with open(bom_output_path,'w') as f:
            bom_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
            for row in bom:
               bom_writer.writerow(row)

    def save_vendor_parts_csv_files(self,netlist_path=None):
        self._update_netlist(netlist_path)
        if self._netlist_path is None:
            return

        output_dir = os.path.join(os.path.dirname(self._netlist_path),'bom')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        vendors_parts = self.get_vendors_parts_from_netlist()
        for vendor in vendors_parts:
            vendor_parts_filename = str(vendor) + '_parts.csv'
            vendor_parts_output_path = os.path.join(output_dir,vendor_parts_filename)
            with open(vendor_parts_output_path,'w') as f:
                vendor_parts_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
                vendor_parts = vendors_parts[vendor]
                for row in vendor_parts:
                   vendor_parts_writer.writerow(row)

    def save_all_csv_files(self,netlist_path=None):
        self.save_bom_csv_file(netlist_path)
        self.save_vendor_parts_csv_files(netlist_path)


def save_all_csv_files():
    kb = KicadBom()
    kb.save_all_csv_files()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    save_all_csv_files()
