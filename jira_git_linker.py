#!/usr/bin/env python3

"""
Mocked Jira + Git Merge Request linker.

- Prints ASCII tables
- Optional CSV export (via --csv-output filename.csv)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re
import argparse
import csv
from pathlib import Path


# ---------------------------
# Data models
# ---------------------------

@dataclass
class JiraIssue:
    key: str
    summary: str
    status: str
    assignee: str


@dataclass
class MergeRequest:
    id: int
    title: str
    source_branch: str
    state: str
    author: str
    web_url: str


# ---------------------------
# Mocked Jira & Git Clients
# ---------------------------

class MockJiraClient:

    def __init__(self):
        self._issues: Dict[str, JiraIssue] = {
            "MBUX-123": JiraIssue(
                "MBUX-123",
                "Fix navigation crash",
                "In Progress",
                "alice",
            ),
            "MBUX-456": JiraIssue(
                "MBUX-456",
                "Improve ASR latency",
                "To Do",
                "bob",
            ),
            "MBUX-789": JiraIssue(
                "MBUX-789",
                "Add logging for HIL failures",
                "Done",
                "carol",
            ),
        }

    def get_issue(self, key: str) -> Optional[JiraIssue]:
        return self._issues.get(key)

    def list_all_issues(self) -> List[JiraIssue]:
        return list(self._issues.values())


class MockGitClient:

    def __init__(self):
        self._mrs = [
            MergeRequest(
                1,
                "MBUX-123: Fix NLU crash when navigating home",
                "feature/MBUX-123-fix-nlu-crash",
                "merged",
                "dave",
                "https://git.example.com/pr/1",
            ),
            MergeRequest(
                2,
                "Improve logging for test failures",
                "feature/MBUX-789-logging",
                "open",
                "erin",
                "https://git.example.com/pr/2",
            ),
            MergeRequest(
                3,
                "WIP: experiment with audio pipeline",
                "experiment/audio-refactor",
                "open",
                "frank",
                "https://git.example.com/pr/3",
            ),
        ]

    def list_merge_requests(self) -> List[MergeRequest]:
        return self._mrs


# ---------------------------
# Linking logic
# ---------------------------

TICKET_PATTERN = re.compile(r"(MBUX-\d+)", re.IGNORECASE)


def extract_ticket_id_from_mr(mr: MergeRequest) -> Optional[str]:
    """
    Extract a Jira ticket ID like MBUX-123 from the MR title or branch.
    """
    for text in (mr.title, mr.source_branch):
        m = TICKET_PATTERN.search(text)
        if m:
            return m.group(1).upper()
    return None


def link_jira_and_git(
    jira_client: MockJiraClient,
    git_client: MockGitClient,
) -> Tuple[List[Tuple[JiraIssue, List[MergeRequest]]], List[MergeRequest]]:
    """
    Returns:
      - list of (JiraIssue, [MRs]) pairs
      - list of MRs that have no linked Jira ticket
    """
    mrs = git_client.list_merge_requests()
    ticket_to_mrs: Dict[str, List[MergeRequest]] = {}
    mrs_without_ticket: List[MergeRequest] = []

    for mr in mrs:
        ticket_id = extract_ticket_id_from_mr(mr)
        if ticket_id:
            ticket_to_mrs.setdefault(ticket_id, []).append(mr)
        else:
            mrs_without_ticket.append(mr)

    linked: List[Tuple[JiraIssue, List[MergeRequest]]] = []
    for ticket_id, mrs_for_ticket in ticket_to_mrs.items():
        issue = jira_client.get_issue(ticket_id)
        if issue:
            linked.append((issue, mrs_for_ticket))
        else:
            # If ticket doesn't exist in Jira, treat MRs as "without ticket"
            mrs_without_ticket.extend(mrs_for_ticket)

    return linked, mrs_without_ticket


# ---------------------------
# ASCII Table output
# ---------------------------

def print_ascii_table(
    linked: List[Tuple[JiraIssue, List[MergeRequest]]],
    mrs_without_ticket: List[MergeRequest],
    jira_client: MockJiraClient,
) -> None:
    """
    Print a human-readable ASCII summary.
    """

    print("\n=== Jira Tickets with Merge Requests ===\n")
    header = (
        f"{'Ticket':<10} | {'Status':<12} | {'Assignee':<10} | "
        f"{'MR ID':<5} | {'MR State':<8} | {'Author':<8} | Title"
    )
    print(header)
    print("-" * len(header))

    for issue, mrs in linked:
        for mr in mrs:
            print(
                f"{issue.key:<10} | {issue.status:<12} | {issue.assignee:<10} | "
                f"{mr.id:<5} | {mr.state:<8} | {mr.author:<8} | {mr.title}"
            )

    all_ticket_ids = {i.key for i, _ in linked}

    print("\n=== Jira Tickets WITHOUT any Merge Request ===\n")
    print(f"{'Ticket':<10} | {'Status':<12} | {'Assignee':<10} | Summary")
    print("-" * 60)
    for issue in jira_client.list_all_issues():
        if issue.key not in all_ticket_ids:
            print(
                f"{issue.key:<10} | {issue.status:<12} | {issue.assignee:<10} | {issue.summary}"
            )

    print("\n=== Merge Requests WITHOUT linked Jira Ticket ===\n")
    print(f"{'MR ID':<5} | {'State':<8} | {'Author':<8} | Title")
    print("-" * 60)
    for mr in mrs_without_ticket:
        print(f"{mr.id:<5} | {mr.state:<8} | {mr.author:<8} | {mr.title}")


# ---------------------------
# CSV Export
# ---------------------------

def export_csv(
    linked: List[Tuple[JiraIssue, List[MergeRequest]]],
    mrs_without_ticket: List[MergeRequest],
    jira_client: MockJiraClient,
    file_path: Path,
) -> None:
    """
    Export a CSV containing:
      - Jira tickets with MRs
      - Jira tickets without MRs
      - MRs without Jira ticket
    """

    fieldnames = [
        "ticket_key",
        "ticket_status",
        "ticket_assignee",
        "mr_id",
        "mr_state",
        "mr_author",
        "mr_title",
    ]

    all_ticket_ids = {i.key for i, _ in linked}

    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 1) Jira tickets that DO have MRs
        for issue, mrs in linked:
            for mr in mrs:
                writer.writerow(
                    {
                        "ticket_key": issue.key,
                        "ticket_status": issue.status,
                        "ticket_assignee": issue.assignee,
                        "mr_id": mr.id,
                        "mr_state": mr.state,
                        "mr_author": mr.author,
                        "mr_title": mr.title,
                    }
                )

        # 2) Jira tickets WITHOUT any MR
        for issue in jira_client.list_all_issues():
            if issue.key not in all_ticket_ids:
                writer.writerow(
                    {
                        "ticket_key": issue.key,
                        "ticket_status": issue.status,
                        "ticket_assignee": issue.assignee,
                        "mr_id": None,
                        "mr_state": None,
                        "mr_author": None,
                        "mr_title": issue.summary,
                    }
                )

        # 3) MRs WITHOUT any Jira ticket (Frank will appear here)
        for mr in mrs_without_ticket:
            writer.writerow(
                {
                    "ticket_key": None,
                    "ticket_status": None,
                    "ticket_assignee": None,
                    "mr_id": mr.id,
                    "mr_state": mr.state,
                    "mr_author": mr.author,
                    "mr_title": mr.title,
                }
            )

    print(f"\n[INFO] CSV exported to: {file_path}")


# ---------------------------
# CLI + Main
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Link mocked Jira tickets and Git merge requests."
    )
    parser.add_argument(
        "--csv-output",
        "-c",
        help="Export CSV file (e.g. report.csv)",
    )
    args = parser.parse_args()

    jira_client = MockJiraClient()
    git_client = MockGitClient()

    linked, mrs_without_ticket = link_jira_and_git(jira_client, git_client)

    # Always show ASCII output
    print_ascii_table(linked, mrs_without_ticket, jira_client)

    # Optional CSV export
    if args.csv_output:
        export_csv(linked, mrs_without_ticket, jira_client, Path(args.csv_output))


if __name__ == "__main__":
    main()
