# excel-csv
This package provides a Python API for quickly reading out a .csv file into a list of ordered dictionaries in one line. This can be useful under circumstances where memory usage isn't that important, and the data is not being stored in a proper database. For example, this package was created for a context in which the data is being sold via CSV. Commercial licenses are available. Commits are not being accepted for copyright reasons.

Creating an instance:
spreadsheet=ExcelCSV(path)

Reading:
list_of_records = spreadsheet.read()

Writing:

spreadsheet.write(list_of_records, output_path=None)

ExcelCSV(path, list_of_records) is a shortcut for constructing and writing to the file if the dictionaries are ordered.

ExcelCSV(path, list_of_records, fieldnames) is a shortcut for constructing and writing to the file if the dictionaries are unordered.

Appending:
spreadsheet.append(list_of_records)

Filtering:
spreadsheet.filter(list_of_records, matches_fields, {'field': 'value'})
