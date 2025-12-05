# Jira_git_linker

The script automates traceability between Jira tickets and Git merge requests by extracting and grouping relationships, then reporting gaps through readable tables and exportable data. The result shows Jira Tickets with Merge Requests and without MR and Merge Requests without a linked Jira Ticket

## Run with ASCII output (default): 
python jira_git_linker.py

## Run with CSV export: 
python jira_git_linker.py --csv-output summary.csv


