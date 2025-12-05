# Jira_git_linker

The script automates traceability between Jira tickets and Git merge requests by extracting and grouping relationships, then reporting gaps through readable tables and exportable data.

Run with ASCII output (default)
python jira_git_linker.py

Run with CSV export
python jira_git_linker.py --csv-output summary.csv

After execution, your terminal will show:

=== Jira Tickets with Merge Requests ===
...
=== Jira Tickets WITHOUT any Merge Request ===
...
=== Merge Requests WITHOUT linked Jira Ticket ===
...


And the CSV file will appear in the current directory.
