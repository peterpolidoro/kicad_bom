#
# Python script to generate BOM in multiple formats from a KiCad generic netlist.
#
import kicad_netlist_reader
from pathlib import Path
from os import walk
import csv


class KicadBom:
    def __init__(self, netlist_path=None):
        self._netlist_suffix = '.xml'
        self._netlist_path = None
        self._netlist = None
        self._grouped_components = None
        self._no_part_number = 'NO_PART_NUMBER'

        netlist_path = self._find_netlist_path(netlist_path)
        self._read_netlist(netlist_path)

    def _find_netlist_path(self, netlist_path):
        try:
            netlist_path = Path(netlist_path)
        except TypeError:
            netlist_path = Path.cwd()

        if netlist_path.suffix == self._netlist_suffix:
            return netlist_path

        if netlist_path.exists() and netlist_path.is_dir():
            for root, dirs, files in walk(netlist_path):
                for f in files:
                    if f.endswith(self._netlist_suffix):
                        return Path(root) / Path(f)

        raise RuntimeError('Cannot find netlist!')

    def _find_or_create_output_path(self, output_path):
        try:
            output_path = Path(output_path)
        except TypeError:
            output_path = Path.cwd()

        if not output_path.parent.exists():
            Path.mkdir(output_path.parent, parents=True)

        return output_path

    def _read_netlist(self, netlist_path):
        # Generate an instance of a generic netlist and load the netlist tree.
        self._netlist = kicad_netlist_reader.netlist(netlist_path)

        # subset the components to those wanted in the BOM, controlled
        # by <configure> block in kicad_netlist_reader.py
        components = self._netlist.getInterestingComponents()

        compfields = self._netlist.gatherComponentFieldUnion(components)
        partfields = self._netlist.gatherLibPartFieldUnion()

        self._fields = compfields | partfields

        # Get all of the components in groups of matching parts + values
        # (see kicad_netlist_reader.py)
        self._grouped_components = self._netlist.groupComponents(components)

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

    def _get_parts_by_vendor(self):
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

    def _get_bom_row_from_part(self, item, part_number, part_info, fields):
            ref_string = self._refs_to_string(part_info['refs'])
            quantity = part_info['quantity']
            group = part_info['group']

            row = []
            for field in fields:
                if 'Item' == field:
                    if part_number is not self._no_part_number:
                        row.append(item)
                    else:
                        row.append('')
                elif 'Reference' in field:
                    row.append(ref_string)
                elif 'Quantity' == field:
                    row.append(quantity)
                else:
                    value = self._netlist.getGroupField(group, field)
                    row.append(value)
            return row

    def get_bom(self, input_fields=None, output_fields=None, format_for_org_table=False):
        if input_fields is None:
            input_fields = self._fields
        if output_fields is None:
            output_fields = input_fields

        if len(input_fields) != len(output_fields):
            raise RuntimeError("len(input_fields) must equal len(output_fields)")

        # Create header row
        row = []
        for c in output_fields:
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
            row = self._get_bom_row_from_part(item, part_number, part_info, input_fields)
            if part_number is not self._no_part_number:
                bom.append(row)
            else:
                row_of_parts_without_number = row
        if row_of_parts_without_number:
            bom.append(row_of_parts_without_number)

        if format_for_org_table:
            bom.insert(1, None)

        return bom

    def save_bom_csv_file(self, output_path=None, input_fields=None, output_fields=None):
        output_path = self._find_or_create_output_path(output_path)
        bom = self.get_bom(input_fields, output_fields)
        if output_path.is_dir():
            bom_output_path = output_path.parent / Path('bom.csv')
        elif output_path.suffix != '.csv':
            bom_output_path = output_path.with_suffix('.csv')
        else:
            bom_output_path = output_path
        with open(bom_output_path,'w') as f:
            bom_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
            for row in bom:
               bom_writer.writerow(row)

    def save_vendor_parts_csv_files(self, output_path=None):
        output_path = self._find_or_create_output_path(output_path).parent
        parts_by_vendor = self._get_parts_by_vendor()
        for vendor in parts_by_vendor:
            vendor_parts_filename = str(vendor) + '_parts.csv'
            vendor_parts_output_path = output_path / Path(vendor_parts_filename)
            with open(vendor_parts_output_path,'w') as f:
                vendor_parts_writer = csv.writer(f,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
                parts = parts_by_vendor[vendor]
                for part_number, part_info in parts.items():
                    row = self._get_vendor_row_from_part(part_number,part_info)
                    vendor_parts_writer.writerow(row)

    def save_all_csv_files(self, output_path=None, input_field_names=None, output_field_names=None):
        self.save_bom_csv_file(output_path, input_field_names, output_field_names)
        self.save_vendor_parts_csv_files(output_path)


def save_all_csv_files():
    kb = KicadBom()
    kb.save_all_csv_files()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    save_all_csv_files()
