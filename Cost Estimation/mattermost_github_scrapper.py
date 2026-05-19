import csv
import os
import requests
from datetime import datetime, timezone

GITHUB_API_URL = "https://api.github.com"
OUTPUT_FIELDNAMES = [
    "number",
    "title",
    "labels",
    "created_at",
    "merged_at",

    "additions",
    "deletions",
    "changed_lines",
    "number_of_files",
    "commits",
    "issue_comments",
    "review_comments",
    "number_of_comments",

    "open_duration_seconds",
    "open_duration_hours",
    "open_duration_days",
    "url",
]

def parse_github_datetime(value):
    if value is None or value == "":
        return None
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value)

def make_headers(token):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def get_pull_request_details(owner, repo, pull_number, token):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = make_headers(token)

    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        print(f"403 for token. Remaining={remaining}, Reset={reset}")

    response.raise_for_status()
    return response.json()

def read_source_pull_requests(input_file):
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)

def get_processed_pr_numbers(output_file):
    if not os.path.exists(output_file):
        return set()
    processed = set()
    with open(output_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("number"):
                processed.add(str(row["number"]))
    return processed

def append_rows_to_csv(rows, output_file):
    if not rows:
        return
    file_exists = os.path.exists(output_file)
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_file}")


def process_pull_requests_from_csv(owner, repo, input_file, output_file, start_index, end_index, tokens, requests_per_token=5000,):
    source_pull_requests = read_source_pull_requests(input_file)
    selected_pull_requests = source_pull_requests[start_index:end_index]

    processed_pr_numbers = get_processed_pr_numbers(output_file)

    token_index = 0
    requests_used_with_current_token = 0

    processed_count = 0
    skipped_count = 0
    rows_to_write = []

    for index, pr in enumerate(selected_pull_requests, start=start_index):
        pull_number = str(pr["number"])

        if pull_number in processed_pr_numbers:
            print(f"Skipping PR #{pull_number} at index {index}: already processed.")
            skipped_count += 1
            continue

        if requests_used_with_current_token >= requests_per_token:
            append_rows_to_csv(rows_to_write, output_file)
            rows_to_write = []
            token_index += 1
            requests_used_with_current_token = 0
            if token_index >= len(tokens):
                print("No tokens remaining. Stopping safely.")
                break
            print(f"Switching to token {token_index + 1}/{len(tokens)}.")
        created_at = parse_github_datetime(pr["created_at"])
        merged_at = parse_github_datetime(pr["merged_at"])
        if created_at is None or merged_at is None:
            print(f"Skipping PR #{pull_number} at index {index}: missing created_at or merged_at.")
            skipped_count += 1
            continue
        current_token = tokens[token_index]

        try:
            detailed_pr = get_pull_request_details(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                token=current_token,
            )
            requests_used_with_current_token += 1
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else None
            if status_code == 403:
                append_rows_to_csv(rows_to_write, output_file)
                rows_to_write = []

                token_index += 1
                requests_used_with_current_token = 0

                if token_index >= len(tokens):
                    print("Rate limit hit and no tokens remaining. Stopping safely.")
                    break

                print(f"Rate limit hit. Switching to token {token_index + 1}/{len(tokens)}.")

                detailed_pr = get_pull_request_details(
                    owner=owner,
                    repo=repo,
                    pull_number=pull_number,
                    token=tokens[token_index],
                )
                requests_used_with_current_token += 1
            else:
                raise

        duration = merged_at - created_at

        additions = detailed_pr.get("additions", 0)
        deletions = detailed_pr.get("deletions", 0)
        changed_lines = additions + deletions
        changed_files = detailed_pr.get("changed_files", 0)

        issue_comments = detailed_pr.get("comments", 0)
        review_comments = detailed_pr.get("review_comments", 0)
        number_of_comments = issue_comments + review_comments

        commits = detailed_pr.get("commits", 0)

        info = {
            "number": pull_number,
            "title": pr["title"],
            "labels": pr.get("labels", ""),
            "created_at": created_at.isoformat(),
            "merged_at": merged_at.isoformat(),

            "additions": additions,
            "deletions": deletions,
            "changed_lines": changed_lines,
            "number_of_files": changed_files,
            "commits": commits,
            "issue_comments": issue_comments,
            "review_comments": review_comments,
            "number_of_comments": number_of_comments,

            "open_duration_seconds": duration.total_seconds(),
            "open_duration_hours": duration.total_seconds() / 3600,
            "open_duration_days": duration.total_seconds() / 86400,
            "url": pr["url"],
        }

        rows_to_write.append(info)
        processed_pr_numbers.add(pull_number)

        processed_count += 1
        print(
            f"Processed PR #{pull_number} at index {index}. "
            f"Token {token_index + 1}/{len(tokens)}, "
            f"token requests used: {requests_used_with_current_token}/{requests_per_token}"
        )

    append_rows_to_csv(rows_to_write, output_file)

    print()
    print(f"Selected rows: {start_index} to {end_index - 1}")
    print(f"Processed: {processed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Final token used: {token_index + 1}/{len(tokens)}")
    print(f"Saved/appended results to {output_file}")


if __name__ == "__main__":
    owner = "mattermost"
    repo = "mattermost"

    input_file = "mattermost_pr_list_generic.csv"
    output_file = "mattermost_detailed_pr.csv"

    start_index = 5000
    end_index = 18418

    tokens = [
        os.environ['IAN_GITHUB_KEY_2'],
        os.environ['BRENDEN_GITHUB_KEY'],
        os.environ['LYDIA_GITHUB_KEY'],
        os.environ['ETHAN_GITHUB_KEY'],
    ]

    process_pull_requests_from_csv(
        owner=owner,
        repo=repo,
        input_file=input_file,
        output_file=output_file,
        start_index=start_index,
        end_index=end_index,
        tokens=tokens,
        requests_per_token=5000,
    )