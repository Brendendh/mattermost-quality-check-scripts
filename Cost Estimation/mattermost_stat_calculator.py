import csv

UTILIZATION_RATE = 0.3
HOURLY_WAGE = 57.07

INPUT_FILE = "mattermost_detailed_pr.csv"
OUTPUT_FILE = "mattermost_detailed_pr_with_effort.csv"

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

    "effort_hours",

    "url",
]

def changed_lines_complexity(changed_lines):
    if changed_lines <= 50:
        return 0
    elif 51 <= changed_lines <= 400:
        return 0.1
    else:
        return 0.25

def files_changed_complexity(files_changed):
    if 1 <= files_changed <= 3:
        return 0
    elif 4 <= files_changed <= 10:
        return 0.1
    else:
        return 0.2

def comments_complexity(comments):
    if comments <= 2:
        return 0
    elif 3 <= comments <= 10:
        return 0.1
    else:
        return 0.25

def calculate_effort_hours(pr_line):
    changed_lines = int(pr_line["changed_lines"])
    number_of_files = int(pr_line["number_of_files"])
    number_of_comments = int(pr_line["number_of_comments"])
    open_duration_hours = float(pr_line["open_duration_hours"])
    complexity_multiplier = (1 + comments_complexity(number_of_comments) + changed_lines_complexity(changed_lines) + files_changed_complexity(number_of_files))

    return open_duration_hours * complexity_multiplier * UTILIZATION_RATE


def main():
    total_effort_hours = 0
    updated_rows = []

    with open(INPUT_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for pr_line in reader:
            effort_hours = calculate_effort_hours(pr_line)
            total_effort_hours += effort_hours

            pr_line["effort_hours"] = f"{effort_hours:.2f}"
            updated_rows.append(pr_line)

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(updated_rows)
    print(f"Rows processed: {len(updated_rows)}")
    print(f"Total effort hours: {total_effort_hours:.2f}")
    print(f"Total cost: {total_effort_hours * HOURLY_WAGE:.2f}")
    print(f"Saved output to {OUTPUT_FILE}")

main()