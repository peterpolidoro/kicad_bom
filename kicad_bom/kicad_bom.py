#
# Python script to generate BOM in multiple formats from a KiCad generic netlist.
#
import kicad_netlist_reader
import os
import csv


class KicadBom:
    def __init__(self,netlist_path=None):
        self._netlist_ext = '.xml'
        self._netlist_path = None
        self._netlist = None
        self._grouped_components = None
        self._column_names = None
        self._no_part_number = 'NO_PART_NUMBER'

        self._update_netlist(netlist_path)
        if self._netlist_path is None:
            return

        self._output_dir = os.path.join(os.path.dirname(self._netlist_path),'bom')
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

    def _update_netlist(self,netlist_path=None):
        if (self._netlist_path is None) or (netlist_path is not None):
            self._read_netlist(netlist_path)

    def _find_netlist_path(self,netlist_path=None):
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
        self._netlist_path = self._find_netlist_path(netlist_path)
        if self._netlist_path is None:
            raise RuntimeError('Cannot find netlist!')

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

    def _get_bom(self):
        # Create header row
        row = []
        for c in self._column_names:
            row.append(c)

        # Create bom
        bom = []
        bom.append(row)

        parts_by_manufacturer_part_number = self._get_parts_by_manufacturer_part_number()

        item = 0
        row_of_parts_without_number = None
        for part_number, part_info in parts_by_manufacturer_part_number.items():
            if part_number is not self._no_part_number:
                item += 1
            row = self._get_bom_row_from_part(item,part_number,part_info)
            if part_number is not self._no_part_number:
                bom.append(row)
            else:
                row_of_parts_without_number = row
        if row_of_parts_without_number:
            bom.append(row_of_parts_without_number)

        return bom

    def _get_bom_row_from_part(self,item,part_number,part_info):
            ref_string = self._refs_to_string(part_info['refs'])
            quantity = part_info['quantity']
            group = part_info['group']

            row = []
            if part_number is not self._no_part_number:
                row.append(item)
            else:
                row.append('')
            row.append(ref_string);
            row.append(quantity)

            for field in self._column_names[self._base_column_length:]:
                value = self._netlist.getGroupField(group, field)
                row.append(value)
            return row

    def _get_parts_by_manufacturer_part_number(self):
        parts = {}
        for group in self._grouped_components:
            try:
                part_number = self._netlist.getGroupField(group,'Manufacturer Part Number')
                if not part_number:
                    part_number = self._no_part_number
            except ValueError:
                part_number = self._no_part_number

            refs = []
            for component in group:
                refs.append(component.getRef())
            quantity = self._get_quantity_from_group(group)

            if part_number in parts:
                parts[part_number]['refs'].extend(refs)
                parts[part_number]['quantity'] += quantity
            else:
                parts[part_number] = {'refs':refs, 'quantity':quantity, 'group':group}
        return parts

    def _refs_to_string(self,refs):
        ref_string = ''
        for ref in refs:
            if len(ref_string) > 0:
                ref_string += " "
            ref_string += ref
        return ref_string

    def _get_quantity_from_group(self,group):
        count = len(group)
        try:
            quantity = int(self._netlist.getGroupField(group,'Quantity'))
        except ValueError:
            quantity = 1
        quantity *= count
        return quantity

    def get_parts_by_vendor(self):
        # Create vendor set
        vendor_set = set()
        for group in self._grouped_components:
            try:
                vendor = self._netlist.getGroupField(group,'Vendor')
                if vendor:
                    vendor_set.add(vendor)
            except:
                pass

        parts_by_vendor = {}
        for vendor in vendor_set:
            parts = {}
            for group in self._grouped_components:
                part_number = None
                try:
                    if vendor == self._netlist.getGroupField(group,'Vendor'):
                        part_number = self._netlist.getGroupField(group,'Vendor Part Number')
                except ValueError:
                    pass

                if part_number:
                    quantity = self._get_quantity_from_group(group)
                    if part_number in parts:
                        parts[part_number]['quantity'] += quantity
                    else:
                        parts[part_number] = {'quantity':quantity}

            parts_by_vendor[vendor] = parts
        return parts_by_vendor

    def _get_vendor_row_from_part(self,part_number,part_info):
            row = []
            row.append(part_number)
            row.append(part_info['quantity'])
            return row

    def _save_bom_csv_file(self):
        bom = self._get_bom()
        bom_filename = 'bom.csv'
        bom_output_path = os.path.join(self._output_dir,bom_filename)
        with open(bom_output_path,'w') as f:
            bom_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
            for row in bom:
               bom_writer.writerow(row)

    def _save_vendor_parts_csv_files(self):
        parts_by_vendor = self.get_parts_by_vendor()
        for vendor in parts_by_vendor:
            vendor_parts_filename = str(vendor) + '_parts.csv'
            vendor_parts_output_path = os.path.join(self._output_dir,vendor_parts_filename)
            with open(vendor_parts_output_path,'w') as f:
                vendor_parts_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
                parts = parts_by_vendor[vendor]
                for part_number, part_info in parts.items():
                    row = self._get_vendor_row_from_part(part_number,part_info)
                    vendor_parts_writer.writerow(row)

    def save_all_csv_files(self):
        self._save_bom_csv_file()
        self._save_vendor_parts_csv_files()


def save_all_csv_files():
    kb = KicadBom()
    kb.save_all_csv_files()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    save_all_csv_files()
