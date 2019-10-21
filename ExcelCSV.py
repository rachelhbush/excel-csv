# PROGRAM ID: Conversion between list of dictionaries and Excel CSV.py / Excel CSV to & from dictionary list
# Author: Rachel Bush, Date initiated: 12/7/2017
# INSTALLATION: Python v3.6
# REMARKS: This package provides a Python API for quickly reading out a .csv file into a list of ordered dictionaries in one line. This can
# be useful under circumstances where memory usage isn't that important, and the data is not being stored in a proper database. For example,
# this package was created for a context in which the data is being sold via CSV.

# This file contains a class for reading from a CSV file written in the Excel dialect, as a list of ordered dictionaries, and
# writing back to the CSV file using ordered or unordered dictionaries. The class works the same in Python v3.5 as in v3.6, except .read()
# returns records as a list of OrderedDicts instead of a list of unordered dictionaries. You must specify a list of field names because
# dictionaries are allowed to omit key-value pairs as a way of representing null values, unless you use ordered dictionaries and make sure
# every record has the same number of fields by using None for null values.

import csv
import os
from collections import OrderedDict

# Simulate a CSV, written in the Excel dialect and containing field headers in the first row. This class supports reading as a list of dictionaries.
# Creating an instance: spreadsheet=ExcelCSV(path)
# Reading:              list_of_records = spreadsheet.read()
# Writing:              spreadsheet.write(list_of_records, output_path=None)
#                       ExcelCSV(path, list_of_records) is a shortcut for constructing and writing to the file if the dictionaries are ordered.
#                       ExcelCSV(path, list_of_records, fieldnames) is a shortcut for constructing and writing to the file if the dictionaries are unordered.
# Appending:            spreadsheet.append(list_of_records)
class ExcelCSV:
    # Construct the object using data from the file, or construct it using custom provided data and update the file to reflect the new state.
    def __init__(self, path, records=None, fieldnames=None):
        self.path = '' # These are the only two attributes.
        self.fieldnames = None
        
        self.path = path
        if records is None and fieldnames is None:
            # Read the field names from the file into the object, or use an empty list if no file exists.
            self.fieldnames = self._get_fieldnames_from_file()
        elif records is not None and fieldnames is None:
            if len(records) == 0:
                self.fieldnames = []
                # If there are no records, do not create a .csv. The class assumes in this and the previous scenario that the user intends
                # to add the records later.
            elif isinstance(records[0], OrderedDict):
                # Write to the file. All dictionaries must be ordered dictionaries and they must have the same keys, but the program doesn't validate this in
                # order to save on time spent coding. After writing the validation code, I'd need to test for the amount of time this adds
                # to the process of writing to the file.
                self.update_fieldnames_from_data(records)
                self.write(records)
            else:
                raise SyntaxError("Specify fieldnames when initializing with dict type records.")
        elif records is None and fieldnames is not None:
            self.fieldnames = fieldnames
            self._update_fieldnames_in_file()
        else:
            # records is not None and fieldnames is not None.
            self.fieldnames = fieldnames
            self.write(records)
    # This method is invoked by __init__() in order to allow skipping specifying field names when constructing.
    # If the file exists, return a list of field names. If the file doesn't exist, return an empty list.
    def _get_fieldnames_from_file(self):
        try:
            # Use UTF-8 so that scraped content, almost universally in UTF-8, which contains non-ASCII characters such as /x81, will not
            # cause an exception. The -sig suffix tells open() to add a Byte Order Marker (BOM) invented by Microsoft, consisting of three
            # unlikely characters. Microsoft Excel pre-2007 can't autodetect UTF-8, but 2007+ versions will be able to autodetect it if the
            # BOM is present. (Though other parts of the project reference 'utf-8-sig', this is the only place in the project where I
            # explain this.)
            csv_infile = open(self.path, 'r', encoding='utf-8-sig', newline='')
            reader = csv.reader(csv_infile)
            fieldnames = reader.__next__()
            csv_infile.close()
            return fieldnames
        except FileNotFoundError:
            return []

    # Update the fieldnames attribute, given a list of records of OrderedDict type or a single record. If a list is given, the function will
    # use the first record, and it will assume its fields are the same as all other records in the list. Therefore, each record should indicate
    # a missing value using None or a null string instead of omitting the key.
    def update_fieldnames_from_data(self, data):
        if isinstance(data, OrderedDict):
            self.fieldnames = list(data.keys())
        else:
            if len(data) > 0:
                self.fieldnames = list(data[0].keys())
            # If the length of the list of records is 0, then leave the field names unaltered.
            # The length of the list may be 0 for reasons external to the class, such as no
            # records being found during a search.
                
        return self

    # Prepend a field or fields to the fieldnames list. These methods are useful for adding data to an existing spreadsheet.
    def prepend_fields(self, *args):
        for x in range(len(args)-1, -1, -1):
            self.fieldnames.insert(0, args[x])
        self._update_fieldnames_in_file()

    # Append a field or fields to the fieldnames list.
    def append_fields(self, *args):
        for x in range(len(args)):
            self.fieldnames.append(args[x])
        self._update_fieldnames_in_file()

    # Insert a field or fields into the fieldnames list after a certain field name.
    def insert_fields_after(self, target_field, *args):
        index = self.fieldnames.index(target_field)
        for x in range(len(args)-1, -1, -1):
            # Iterating backward is necessary to prevent the last field from being inserted at the beginning.
            self.fieldnames.insert(index + 1, args[x])
        self._update_fieldnames_in_file()

    # Sync the fieldnames within the file with the fieldnames attribute.
    def _update_fieldnames_in_file(self):
        try:
            # Upon opening a file for writing, its contents are erased, so it has to be opened for reading as well as writing in order to
            # preserve the content aside from the fieldnames.
            csv_infile = open(self.path, 'r', encoding='utf-8-sig', newline='')
            csv_outfile = open(self.path+'_temp', 'w', encoding='utf-8-sig', newline='')
            reader = csv.reader(csv_infile)
            writer = csv.writer(csv_outfile)
            first_row = True
            for row in reader:
                if first_row:
                    # Transfer the new field names instead of the old header row.
                    writer.writerow(self.fieldnames)
                    first_row = False
                else:
                    writer.writerow(row)
            csv_infile.close()
            csv_outfile.close()
            os.remove(self.path)
            os.rename(self.path+'_temp', self.path)
        except FileNotFoundError:
            # If there is no file, the function does nothing. This allows the function to be called routinely whenever the fieldnames are
            # being altered without writing to the file.
            pass
        return self
    
    def read(self):
        try:
            csv_infile = open(self.path, 'r', encoding='utf-8-sig', newline='')
            reader = csv.DictReader(csv_infile)
            records = []
            for row in reader:
               records.append(row)
            csv_infile.close()
            return records
        except FileNotFoundError:
            return []

    # Write to the file. As a prerequisite, the fieldnames attribute must have been updated to reflect any field changes.
    def write(self, records, output_path=None):
        if output_path is not None:
            self.path = output_path
        csv_outfile = open(self.path, 'w', encoding='utf-8-sig', newline='')
        writer = csv.DictWriter(csv_outfile, self.fieldnames)
        writer.writeheader()
        writer.writerows(records)
        csv_outfile.close()
        return self

    # Append records to the file. As a prerequisite, the fieldnames attribute and the fields in the file must have been updated to reflect
    # any field changes. I haven't used this in the project yet.
    def append(self, records):
        csv_outfile = open(self.path, 'a', encoding='utf-8-sig', newline='')
        writer = csv.DictWriter(csv_outfile, self.fieldnames)
        writer.writerows(records)
        csv_outfile.close()
        return self

    # Set the path and, if the file still exists at the previously specified location, move the file. I haven't used this in the project yet.
    def set_path(self, path):
        self.path = path
        if path != self.path and os.path.is_file(path):
            os.rename(self.path, path)
        return self

    # The following methods operate on the spreadsheet while including reading and writing.

    # Remove the specified field from the CSV. I haven't used this in the project yet.
    def remove_field(self, field, output_path=None):
        input_list_of_records = self.read()
        output_list_of_records = []
        for record in input_list_of_records:
            del record[field]
            output_list_of_records.append(record)
        self.fieldnames.remove(field)
        self.write(output_list_of_records, output_path)

    # 0. Given a field with categorical data (a limited number of choices for values), or a multiple choice field, split it into several
    # boolean fields. The fields will be null boolean field only when there is no data such that all fields are NULL.
    # Input: - original_field (str).
    #        - possible_choices, a list of possible choice values. If this is omitted, the program will assume that all possible choice
    #        values have been used by the records in the CSV.
    #        - new_field_names, a list of the new field names. If this argument is omitted, the program will use the choice string with a
    #        question mark added to the end. The possible_choices and new_fields lists should be the same length with a one-to-one
    #        correspondence. If you omit possible_choices, then you must omit new_fields, because you can't manually create a list with the
    #        same order as an automatically generated one without defeating the point of automating it by doing extra work. delimiter, a
    #        string separating each choice in a multiple choice field.
    #        - checked_symbol. This is a string such as 'Y', an integer such as 1, or some other value indicating the choice applies to the
    #        record.
    #        - unchecked_symbol. This is a string such as 'N', an integer such as 0, or some other value indicating the choice doesn't apply
    #        to the record.
    #        - null_symbol is a value of the original field, such as 'No data', which indicates there is no data in any of the fields.
    #          The value should not be an empty string, or else there will be ambiguity as to whether the field is blank because all fields
    #          are false (N). If all fields are null, instead of using 'Y' or 'N', the fields will use empty strings.
    # Output: None.
    def convert_choice_field_to_boolean_field(self, original_field, possible_choices=None, new_field_names=None, delimiter=', ',
                                              checked_symbol='Y', unchecked_symbol='N', null_symbol='No data'):
        list_of_records = self.read()
        if possible_choices is None:
            possible_choices = ExcelCSV._get_possible_choices(list_of_records, original_field, delimiter)
        if new_field_names is None:
            new_field_names = ExcelCSV._get_new_fields(possible_choices)
        self.insert_fields_after(original_field, *new_field_names)
        list_of_records = ExcelCSV._add_boolean_fields_to_records(list_of_records, original_field, possible_choices, new_field_names,
                                                                  delimiter, checked_symbol, unchecked_symbol, null_symbol)
        self.write(list_of_records)

    # 1. Given a list of records and a single-choice (categorical data) field or a multiple-choice field, examine all of them to build a list of
    # possible choice values.
    def _get_possible_choices(list_of_records, original_field, delimiter):
        possible_choices = []
        for i in range(len(list_of_records)):
            list_of_choices_for_record = list_of_records[i][original_field].split(delimiter)
            for j in range(len(list_of_choices_for_record)):
                if list_of_choices_for_record[j] != '':
                    # When none of the choices have been selected, the value will be an empty string, and that should be exempted from becoming the name of a new field.
                    if list_of_choices_for_record[j] not in possible_choices:
                        possible_choices.append(list_of_choices_for_record[j])
        return possible_choices

    # 2. Generate the new field names by appending a question mark to each possible choice value.
    def _get_new_fields(possible_choices):
        new_fields = []
        for x in range(len(possible_choices)):
            new_fields.append(possible_choices[x] + '?')
        return new_fields

    # 3. Add the Boolean fields to the list of records by using the processed multiple choice field data.
    def _add_boolean_fields_to_records(list_of_records, original_field, possible_choices, new_fields, delimiter,checked_symbol,
                                       unchecked_symbol, null_symbol):
        for i in range(len(list_of_records)):
            if list_of_records[i][original_field] == null_symbol:
                for j in range(len(new_fields)):
                    list_of_records[i][new_fields[j]] = ''
            else:
                list_of_choices_for_record = list_of_records[i][original_field].split(delimiter)
                for j in range(len(new_fields)):
                    if possible_choices[j] in list_of_choices_for_record:
                        list_of_records[i][new_fields[j]] = checked_symbol
                    else:
                        list_of_records[i][new_fields[j]] = unchecked_symbol                 
        return list_of_records

    # Filter the records in the spreadsheet down to only those which make a Boolean function of the form
    # function(record, *args, **kwargs) true.
    # Input: function object, *args, **kwargs
    # Output: None
    def filter(self, function, *args, output_path=None, **kwargs):
        input_list_of_records = self.read()
        output_list_of_records = []
        for record in input_list_of_records:
            if function(record, *args, **kwargs):
                output_list_of_records.append(record)
        self.write(output_list_of_records, output_path)
