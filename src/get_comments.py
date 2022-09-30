import vk_api
import json
import click
import datetime
from pytz import timezone
import pandas
import re
from dotenv import load_dotenv
import os

REMOVE_LINEBREAKS = re.compile("[\n\r]+")


def init(id: str, password: str) -> vk_api.VkApi:
    """Initializes VK session"""
    vk_session = vk_api.VkApi(id, password)
    vk_session.auth()

    return vk_session.get_api()


def export_posts(
    vk: vk_api.VkApi, club_id: int, depth: int, tz: timezone, filter: str = ""
) -> tuple:
    """Exports posts of club_id for depth days from now.

    If a filter given exports only posts that contain filter

    Return list of posts and list of tuples post_id, comments_number as the queue
    """

    # calculate time frame for post export
    now_time = datetime.datetime.now().timestamp()
    post_time_limit = now_time - depth * 24 * 60 * 60
    export_term_start_time = datetime.datetime.fromtimestamp(now_time, tz=tz)
    export_term_end_time = datetime.datetime.fromtimestamp(post_time_limit, tz=tz)

    print(
        f"Exporting posts for {club_id} club since {export_term_start_time} "
        + f"till {export_term_end_time}."
    )

    response = vk.wall.get(owner_id=-club_id, count=100, filter="owner")

    posts = {"id": [], "url": [], "datetime": [], "text": [], "comments_number": []}
    queue = []
    exported_posts_count = 0
    for item in response["items"]:
        if filter and filter not in item["text"]:
            print(f"post {item['id']} doesn't contain '{filter}'")
        elif item["date"] < post_time_limit:
            print(f"All posts up to {export_term_end_time} has been exported")
            break
        else:
            posts["id"].append(item["id"])
            posts["url"].append(
                f"https://vk.com/club{club_id}?w=wall-{club_id}_{item['id']}"
            )
            posts["datetime"].append(
                datetime.datetime.fromtimestamp(item["date"], tz=tz)
            )
            posts["text"].append(REMOVE_LINEBREAKS.sub(" ", item["text"]))
            posts["comments_number"].append(item["comments"]["count"])

            queue.append((item["id"], item["comments"]["count"]))
            exported_posts_count += 1

    print(f"{exported_posts_count} posts have been exported")
    return posts, queue


def export_comments(
    vk: vk_api.VkApi,
    club_id: int,
    post_id: int,
    number: int,
    tz: timezone,
) -> list:
    """Exports number of comments to post_id of club_id club

    Returns list of comments
    """
    print(f"Looking for {number} comments of {post_id} post")

    comments = {
        "id": [],
        "post_id": [],
        "url": [],
        "datetime": [],
        "text": [],
        "thread_number": [],
        "likes_number": [],
    }

    response = vk.wall.getComments(
        owner_id=-club_id, post_id=post_id, count=max(100, number), need_likes=1
    )
    print(f"Exported {len(response['items'])} items for {response['count']} comments")

    for item in response["items"]:
        comments["id"].append(item["id"])
        comments["post_id"].append(post_id)
        comments["url"].append(
            f"https://vk.com/wall-{club_id}_{post_id}?reply={item['id']}"
        )
        comments["datetime"].append(
            datetime.datetime.fromtimestamp(item["date"], tz=tz)
        )
        comments["text"].append(REMOVE_LINEBREAKS.sub(" ", item["text"]))
        comments["likes_number"].append(item["likes"]["count"])
        thread_number = 0
        if "thread" in item:
            thread_number = item["thread"]["count"]
        comments["thread_number"].append(thread_number)

    return comments


@click.command()
@click.argument("club_id", type=click.INT)
@click.option(
    "-d", "--depth", default=1, type=int, help="number of days from now for post export"
)
@click.option(
    "-f",
    "--filter",
    default="",
    type=str,
    help="a string that a post must contain or empty string to not filter",
)
def get_comments(club_id: int, depth: int, filter: str) -> None:
    """Exports posts of a given by CLUB_ID VK club and its comments"""

    load_dotenv()
    VK_ID = os.getenv("VK_ID")
    VK_PASSWORD = os.getenv("VK_PASSWORD")
    TIMEZONE = timezone(os.getenv("TIMEZONE"))

    vk = init(VK_ID, VK_PASSWORD)

    posts, queue = export_posts(
        vk, club_id=club_id, depth=depth, tz=TIMEZONE, filter=filter
    )

    if len(queue) == 0:
        print("No comments to export")
        return

    posts_df = pandas.DataFrame(posts)
    posts_df.to_csv("data/posts.csv", index=False)

    comments_df = None
    for item in queue:
        post_comments = pandas.DataFrame(
            export_comments(
                vk, club_id=club_id, post_id=item[0], number=item[1], tz=TIMEZONE
            )
        )

        if comments_df is None:
            comments_df = post_comments.copy()
        else:
            comments_df = pandas.concat([comments_df, post_comments])

    if comments_df is not None:
        comments_df.to_csv("data/comments.csv")

    print(f"Exported {comments_df.shape[0]} comments total")


if __name__ == "__main__":
    get_comments()
