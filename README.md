
# SpaceBattlesCrawler
This script can be used to crawl a single story on [forums.spacebattles.com](forums.spacebattles.com) and extract all the posts.
The main purpose for me to write the script was to mainly sort posts by likes to see what people were engaging with.
## Requirements
1. Pyhton3
2. BeautifulSoup4
	```
	pip install beautifulsoup4
	```
## Usage
 1. Change story URL
	 Change the URL in `main.py` near the top of the file.
	**Example:**
    ```
    url = 'https://forums.spacebattles.com/threads/i-want-to-help-worm-mcu-post-gm.992435'
    ```
	> ⚠️Do not add a '/' at the end of the URL.
3. Run Program
	* Story statistics are extracted, printed and stored in the `story_stats.json` file and are available with the **story_stats** global variable.
	* All posts and their statistics are extracted and stored in `posts.json` file and are available with the **posts_list** global variable.
	* The program will then print the top 2 posts, sorted by likes, made after each threadmark.
4. Customize Program
	See the commented out lines in the main function at the bottom of the `main.py` file to see some examples of how the script might be used.
## Data Formats
### Story Stats
```
{
  "title": "I want to help [WORM/MCU][Post-GM] | SpaceBattles",
  "author": "LiveSparks",
  "start_date": "29/01/2022 15:29",
  "watchers": "3,323",
  "recent_readers": "2,603",
  "threadmarks": 11,
  "word_count": "35k",
  "pages": 36
}
```
### Post Stats
Posts are stored in a list sorted by post number.
```
{
    "author": "LiveSparks",
    "id": "post-81869918",
    "is_threadmark": true,
    "content": "Threadmarks:: Chapter 01",
    "date": "29/01/2022 15:29",
    "post_number": 1,
    "likes": 991
}
```
#### Threadmarks vs Non-Threadmark posts
The only difference between the two is the **content** stat.
In case of a Threadmark, it will have a format of: 
```
"Threadmarks:: <Threadmark_Title>"
```
In case of a normal post, it will contain the actual contents of the post.

> Currently there is no distinction made between the different types of threadmarks.

## Built-in Functions
1. ***Loading Functions***
 * **load_posts_from_web(url)**
	Forces the script to load posts from the web. Uses 8 threads to scrape the story.
* **load_posts_from_file(filename)**
	Forces the script to load posts from a life. Internet will not be used.
* **check_for_new_updates()**
	Scrapes the first and last page of the story. If no new posts have been made, loads from file. Else loads from file.
2. ***Utility Functions***
* **get_posts_by_threadmark(posts, threadmark)**
If *threadmark* is True, get all the threadmarked posts and vice-versa.
* **get_posts_after_number(posts, post_number)**
Get all posts after a particular post number.
* **sort_posts_by_likes(posts)**
Return the posts sorted by likes.
3. ***Print Functions***
* **print_post_details(post)**
* **print_story_stats()**
* **print_top_posts_by_likes(posts, num_replies)**
Print the top posts sorted by likes where num_replies is the number of posts to print.
* **print_top_replies_by_likes_for_latest_threadmark(num_replies)**
* **print_top_replies_by_likes_for_each_threadmark(num_replies)**
## Contribution
Pull requests, issues and suggestions are welcome.
