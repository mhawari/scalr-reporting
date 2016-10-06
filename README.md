# scalr-reporting

This tool lists all the servers in a given environment and outputs a CSV file.

Usage scalr-reporting.py [-h] [-f field [field ...]] credentials

credentials is the path to a JSON file containing the credentials for Scalr
optional arguments:
-h, --help Show usage
-f field [field ...], --fieldsToGet field [field...] List of all the fields to get.

The following example describes the syntax of a field.
Example: 'farmRole.role.os.name' gets the field 'name' field of the 'os' object of the 'role' object of the 'farmRoleObject' of the server
Available objects are Roles, Farm Roles and OS. Please consult the API documentation for more information about the available fields in these objects.
