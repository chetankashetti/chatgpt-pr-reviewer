import json
import os

from all_pr_review_bot import review_pr
from pr_review_util import fetch_pr_diff, post_review_comment


def main():
    # Main function to run the bot
    # Get the repository from the environment
    repo = os.getenv("GITHUB_REPOSITORY")
    # Get the path to the event payload
    pr_number = os.getenv("GITHUB_EVENT_PATH")
    with open(pr_number, "r") as event_file:
        event_data = json.load(event_file)
    pr = event_data["pull_request"]

    diff_content = fetch_pr_diff(repo, pr['number'])
    review = review_pr(pr, diff_content)
    comment = post_review_comment(repo, pr, review)
    print(f"Posted review for PR #{pr['number']}: {review}")


if __name__ == "__main__":
    main()
