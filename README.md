# Jira_git_linker

The script automates traceability between Jira tickets and Git merge requests by extracting and grouping relationships, then reporting gaps through readable tables and exportable data.

## Run with ASCII output (default): 
python jira_git_linker.py

## Run with CSV export: 
python jira_git_linker.py --csv-output summary.csv

## Example ASCII table

=== Jira Tickets with Merge Requests ===

Ticket     | Status       | Assignee   | MR ID | MR State | Author   | Title
----------------------------------------------------------------------------
MBUX-123   | In Progress  | alice      | 1     | merged   | dave     | MBUX-123: Fix NLU crash when navigating home
MBUX-789   | Done         | carol      | 2     | open     | erin     | Improve logging for test failures

=== Jira Tickets WITHOUT any Merge Request ===

Ticket     | Status       | Assignee   | Summary
------------------------------------------------------------
MBUX-456   | To Do        | bob        | Improve ASR latency

=== Merge Requests WITHOUT linked Jira Ticket ===

MR ID | State    | Author   | Title
------------------------------------------------------------
------------------------------------------------------------
3     | open     | frank    | WIP: experiment with audio pipeline
