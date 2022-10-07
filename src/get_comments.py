from asyncio.log import logger
import vk_api
import click
import datetime
from pytz import timezone
import re
from dotenv import load_dotenv
import os
import logging
import csv

REMOVE_LINEBREAKS = re.compile("[\n\r]+")


def init(id: str, password: str) -> vk_api.VkApi:
    """Initializes VK session"""
    vk_session = vk_api.VkApi(id, password)
    vk_session.auth()

    return vk_session.get_api()


def setup_logging(logfile: str = "log.txt", loglevel: str = "DEBUG") -> None:
    """
    Sets up logging handlers and a format

    :param logfile:
    :param loglevel:
    """
    loglevel = getattr(logging, loglevel)

    logger = logging.getLogger()
    logger.setLevel(loglevel)
    fmt = (
        "%(asctime)s: %(levelname)s: %(filename)s: "
        + "%(funcName)s(): %(lineno)d: %(message)s"
    )
    formatter = logging.Formatter(fmt)

    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

def save_to_csv(data: list, column_names: list, file_path: str) -> None:
    try:
        with open(file_path, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(column_names)
            for row in data:
                writer.writerow(row)
    except Exception as e:
        logging.error(f"Can't save data to {file_path}", e)

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

    logging.info(
        f"Exporting time frame is {export_term_start_time} – "
        + f"{export_term_end_time}."
    )

    posts = []
    queue = []

    try:
        response = vk.wall.get(owner_id=-club_id, count=100, filter="owner")

        exported_posts_count = 0
        for item in response["items"]:
            if filter and filter not in item["text"]:
                logging.info(f"post {item['id']} doesn't contain '{filter}'")
            elif item["date"] < post_time_limit:
                logging.info(f"All posts up to {export_term_end_time} has been exported")
                break
            else:
                posts.append([
                    item["id"],
                    f"https://vk.com/club{club_id}?w=wall-{club_id}_{item['id']}",
                    datetime.datetime.fromtimestamp(item["date"], tz=tz),
                    REMOVE_LINEBREAKS.sub(" ", item["text"]),
                    item["comments"]["count"]
                ])

                queue.append((item["id"], item["comments"]["count"]))
                exported_posts_count += 1
    except Exception as e:
        logging.error("Got an error during posts export ", e)

    logging.info(f"{exported_posts_count} posts have been exported")
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
    logging.info(f"Looking for {number} comments of {post_id} post")

    comments = []

    def append_comment(item, parent_comment_id=0):
        comments.append([
            item["id"],
            post_id,
            f"https://vk.com/wall-{club_id}_{post_id}?reply={parent_comment_id if parent_comment_id else item['id']}",
            datetime.datetime.fromtimestamp(item["date"], tz=tz),
            REMOVE_LINEBREAKS.sub(" ", item["text"]),
            item["likes"]["count"],
            parent_comment_id
        ])

    try:
        response = vk.wall.getComments(
            owner_id=-club_id, post_id=post_id, count=max(100, number), need_likes=1, 
            thread_items_count=10
        ) 

        for item in response["items"]:
            append_comment(item)
            
            if "thread" in item and item["thread"]["count"]:
                for thread_item in item['thread']['items']:
                    append_comment(thread_item, parent_comment_id=item["id"])

        logging.info(
            f"Exported {len(comments)} of {response['count']} comments"
        )
    except Exception as e:
        logging.error("Got an error during comments export ", e)

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

    setup_logging(logfile="data/log.txt", loglevel="INFO")
    logging.info(
        f"Get posts and comments of {club_id} for {depth} days from now. "
        + f"Filter is {filter if filter else 'not given'}"
    )

    load_dotenv()
    VK_ID = os.getenv("VK_ID")
    VK_PASSWORD = os.getenv("VK_PASSWORD")
    TIMEZONE = timezone(os.getenv("TIMEZONE"))

    vk = init(VK_ID, VK_PASSWORD)

    posts, queue = export_posts(
        vk, club_id=club_id, depth=depth, tz=TIMEZONE, filter=filter
    )

    if len(queue) == 0:
        logging.info("No comments to export")
        return

    save_to_csv(data=posts, 
        column_names=["id", "url", "datetime", "text", "comments_number"],  
        file_path="data/posts.csv"
    )

    comments_data = []
    for item in queue:
        comments_data.extend(
            export_comments(vk, club_id=club_id, post_id=item[0], number=item[1], tz=TIMEZONE)
        )

    if len(comments_data) > 0:
        save_to_csv(data=comments_data, 
                    column_names=["id", "post_id", "url", "datetime", "text", "likes_number", "parent_comment_id"], 
                    file_path="data/comments.csv")

    logging.info(f"Exported {len(comments_data)} comments total")


if __name__ == "__main__":
    get_comments()
