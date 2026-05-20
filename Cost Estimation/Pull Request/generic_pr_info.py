import csv
import os

import requests
from datetime import datetime, timezone

GITHUB_API_URL = "https://api.github.com"

def parse_github_datetime(value):
    if value is None:
        return None

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def has_excluded_label(pr, excluded_labels):
    pr_labels = [
        label["name"].lower()
        for label in pr.get("labels", [])
    ]

    excluded_labels_lower = [
        label.lower()
        for label in excluded_labels
    ]
    return any(label in excluded_labels_lower for label in pr_labels)


def get_label_names(pr):
    return [
        label["name"]
        for label in pr.get("labels", [])
    ]

def get_pull_request_details(owner, repo, pull_number, headers):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_pull_requests(owner, repo, excluded_labels=None, token=None):
    if excluded_labels is None:
        excluded_labels = []

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    page = 1
    per_page = 100
    results = []

    while True:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls"

        params = {
            "state": "closed",
            "sort": "created",
            "direction": "desc",
            "per_page": per_page,
            "page": page,
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        pull_requests = response.json()

        if not pull_requests:
            break

        for pr in pull_requests:
            created_at = parse_github_datetime(pr["created_at"])

            if has_excluded_label(pr, excluded_labels):
                continue

            merged_at = parse_github_datetime(pr["merged_at"])

            if merged_at is None:
                continue

            pull_number = pr["number"]

            label_names = get_label_names(pr)

            info = {
                "number": pull_number,
                "title": pr["title"],
                "labels": ", ".join(label_names),
                "created_at": created_at.isoformat(),
                "merged_at": merged_at.isoformat(),
                "url": pr["html_url"],
            }

            print(f"PR #{pull_number} obtained: {info}")

            results.append(info)

        page += 1

    return results


def write_to_csv(pull_requests, output_file):
    fieldnames = [
        "number",
        "title",
        "labels",
        "created_at",
        "merged_at",
        "url",
    ]

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pull_requests)


if __name__ == "__main__":
    owner = "mattermost"
    repo = "mattermost"

    excluded_labels = [
        "AutomatedCherryPick",
    ]

    token = os.environ['IAN_GITHUB_KEY_1']

    pull_requests = get_pull_requests(
        owner=owner,
        repo=repo,
        excluded_labels=excluded_labels,
        token=token,
    )

    output_file = f"mattermost_pr_list_generic.csv"
    write_to_csv(pull_requests, output_file)

    print(f"Found {len(pull_requests)} merged pull requests for {owner}/{repo}.")
    print(f"Excluded labels: {', '.join(excluded_labels) if excluded_labels else 'None'}")
    print(f"Saved results to {output_file}")