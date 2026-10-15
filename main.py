from datetime import date
from functools import cache

from instagrapi import Client
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()  # Load environment variables from .env file

def main():
    cl = Client()

    try:
        cl.load_settings("session.json")
    except:
        pass

    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    
    cl.login(username, password)

    cl.dump_settings("session.json")
    print("Logged in successfully!")

    user_id = cl.user_id_from_username("f1")
    # print(cl.user_info(user_id))
    test_date = {date(2026, 3, 18)}
    dates = {
            # 2023 nov 16-19
            date(2023, 11, 16), 
            date(2023, 11, 17), 
            date(2023, 11, 18), 
            date(2023, 11, 19),
            #2024 nov 21-24
            date(2024, 11, 21),
            date(2024, 11, 22),
            date(2024, 11, 23),
            date(2024, 11, 24),
            #2025 may 22-25
            date(2025, 5, 22),
            date(2025, 5, 23),
            date(2025, 5, 24),
            date(2025, 5, 25),
            #2025 nov 20-23
            date(2025, 11, 20),
            date(2025, 11, 21),
            date(2025, 11, 22),
            date(2025, 11, 23)}
    posts = get_posts_for_dates(cl, user_id, dates)
    print(f"Posts: {len(posts)}")
    # print(posts[0].dict().keys())  # Print the date of the first post to verify
    save_posts_to_file(posts)

# @cache
def get_posts_for_dates(cl: Client, user_id: int, dates: set):
    filtered_posts = []
    end_cursor = None
    with tqdm(desc="Fetching posts") as pbar:
        while True:
            posts, end_cursor = cl.user_medias_paginated(user_id, amount=50, end_cursor=end_cursor)
            for post in posts:
                # print(f"Checking post taken at: {post.taken_at.date()}")
                if post.taken_at.date() in dates:
                    filtered_posts.append(post)
                pbar.update(1)
            # stop fetching once we see a post older than the target date
            if not end_cursor or all(post.taken_at.date() < min(dates) for post in posts):
                break
    return filtered_posts

def save_posts_to_file(posts, filename="posts.csv"):
    with open(filename, "w") as f:
        f.write("Date; URL; Likes; Comments; Media Type; Num Images; Num Videos\n")
        for post in posts:
            num_images, num_videos = 0, 0
            if post.media_type == 8:  # Carousel
                for resource in post.resources:
                    if resource.media_type == 1:
                        num_images += 1
                    elif resource.media_type == 2:
                        num_videos += 1
            f.write(f"{post.taken_at.date()}; https://www.instagram.com/p/{post.code}/; {post.like_count}; {post.comment_count}; {'photo' if post.media_type == 1 else 'video' if post.media_type == 2 else 'carousel'}; {num_images}; {num_videos}\n")

if __name__ == "__main__":
    main()
