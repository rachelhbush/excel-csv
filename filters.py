# PROGRAM ID: filters.py / Filters
# Authors: Rachel Bush. Date initiated: Project initiated Dec. 2, 2017.
# INSTALLATION: See project dependencies list.
# REMARKS: These are functions which filter dictionary records in various ways. They can be used by ExcelCSV's filter()
# or Python's built-in filter.

# Given a dictionary record and a dictionary of field-value pairs, return True if all the record's matching fields have matching values.
# Otherwise, return False. In place of a single value for a field-value pair, you can also use a list or tuple of qualifying values.
def matches_fields(record, fields_dict):
    # fields_dict must be a dictionary, rather than a set of keyword arguments, because a set of keyword arguments would require the field
    # names to be valid Python identifiers. Field names at the top of Excel spreadsheets typically contain a space.
    for field in fields_dict:
        if isinstance(fields_dict[field], list) or isinstance(fields_dict[field], tuple):
            if record[field] not in fields_dict[field]:
                return False
        else:
            if record[field] != fields_dict[field]:
                return False
    return True
