import requests, threading, queue, datetime, json, os
from bs4 import BeautifulSoup

posts_list = []
story_stats = {}
link_queue = queue.Queue()
num_threads = 8

url = 'https://forums.spacebattles.com/threads/i-want-to-help-worm-mcu-post-gm.992435'

def extract_post_stats(post):
    # Get the author
    # Get the value of the attribute: data-author
    post_author = post['data-author']    

    # Get the post id
    # Find the value of the attribute: id
    # Then get the text
    post_id = post.find(attrs={'id': True})['id']

    # Get if the post is a threadmark
    # Check if class attribute contains: hasThreadmark
    is_threadmark = 'hasThreadmark' in post['class']

    # If the post is a threadmark, get the threadmark title
    if is_threadmark:
        # Find the label tag
        # Then get the next tag
        # Then get the text
        post_label = post.find('label')
        post_content = post_label.get_text() + ":: "
        post_content += post_label.find_next().get_text()

    # If the post is not a threadmark, get the post content
    else:
        # Find the div tag that has the attribute: class="bbWrapper"
        # Then get the text
        post_content = post.find(attrs={'class': 'bbWrapper'}).get_text()

        # Replace 'Click to expand...' and 'Click to shrink...'
        post_content = post_content.replace('Click to expand...', '')
        post_content = post_content.replace('Click to shrink...', '[End Quote]')

        # Clean up the post contents such that there are no more that two consecutive newlines and no more than two consecutive \t
        # Find all instances of \t\t\t and replace with \t\t
        while '\t\t\t' in post_content:
            post_content = post_content.replace('\t\t\t', '\t\t')
        
        # Find all instances of \n\n\n and replace with \n\n
        while '\n\n\n' in post_content:
            post_content = post_content.replace('\n\n\n', '\n\n')

    # Get the date and time
    # Find the header tag
    # Find the time tag
    # Then get the datetime attribute
    post_date = post.find('header').find('time')['datetime']
    # Format the date from 2021-08-31T18:00:00+00:00 to DD/MM/YYYY HH:MM
    post_date = datetime.datetime.strptime(post_date, '%Y-%m-%dT%H:%M:%S%z')
    post_date = post_date.strftime('%d/%m/%Y %H:%M')

    # Get the post number
    # Find the header tag
    # Find the last child tag
    # Find the last child tag
    # Find the a tag
    # Get the text
    post_number = post.find('header').findChildren(recursive=False)[-1].findChildren(recursive=False)[-1].find('a').get_text()
    post_number = post_number.strip()
    # Remove the # from the post number
    post_number = post_number[1:]
    # Convert the post number to an integer
    post_number = int(post_number)

    # Get the number of likes
    # Find the tag that has the attribute: class="sv-rating__count"
    # Then get the text
    post_likes = post.find(attrs={'class': 'sv-rating__count'})
    if post_likes is None:
        post_likes = 0
    else:
        post_likes = post_likes.get_text()
        post_likes = int(post_likes)

    # post_likes = post.find(attrs={'class': 'sv-rating__count'}).get_text()
    # post_likes = int(post_likes)

    # Store the stats in a dictionary
    post_stats = {
        'author': post_author,
        'id': post_id,
        'is_threadmark': is_threadmark,
        'content': post_content,
        'date': post_date,
        'post_number': post_number,
        'likes': post_likes
    }
    # print(post_stats)
    return post_stats

# Only works for the first page
def extract_story_stats(content):
    global story_stats
    # Extract the main stats for the story
    print("Extracting main stats...")
    soup = BeautifulSoup(content, 'html.parser')

    # Get the title
    title = soup.find('title').get_text()

    # Get the author
    # Find the tag that has the text: Thread starter
    # Then get the next tag
    # Then get the text
    author = soup.find(string='Thread starter').find_next().get_text()

    # Get the start date and time
    # Find the tag that has the text: Created at
    # Then get the next tag
    # Then get the datetime attribute
    start_date = soup.find(string='Created at').find_next().time['datetime']
    # Format the date from 2021-08-31T18:00:00+00:00 to DD/MM/YYYY HH:MM
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S%z')
    start_date = start_date.strftime('%d/%m/%Y %H:%M')

    # Get the number of watchers
    # Find the tag that has the text: Watchers
    # Then get the next tag
    # Then get the text
    watchers = soup.find(string='Watchers').find_next().get_text()

    # Get the number of Recent readers
    # Find the tag that has the text: Recent readers
    # Then get the next tag
    # Then get the text
    recent_readers = soup.find(string='Recent readers').find_next().get_text()

    # Get the Threadmark stats
    # Find the tag that has the atribute: data-xf-init="threadmarks-toggle-storage"
    # Then get the child tag
    # Then get the text
    threadmark_stats = soup.find(attrs={'data-xf-init': 'threadmarks-toggle-storage'}).findChild().get_text()
    # Convert the text Statistics (8 threadmarks, 20k words) to threadmarks = 8 and words = 20k
    threadmarks = threadmark_stats.split(',')[0].split()[1]
    threadmarks = threadmarks.split(' ')[0][1:]
    threadmarks = int(threadmarks)

    word_count = threadmark_stats.split(',')[1].split()[0]
    word_count = word_count.split(' ')[0]

    # Get the number of pages
    # Find the tags that has the atribute: calss="pageNavSimple-el pageNavSimple-el--current"
    # Select the first tag
    # Then get the text
    pages = soup.find(attrs={'class': 'pageNavSimple-el pageNavSimple-el--current'}).get_text()
    # Convert the text 1 of 17 to 17
    pages = pages.split()[-1]
    pages = int(pages)

    story_stats = {
        'title': title,
        'author': author,
        'start_date': start_date,
        'watchers': watchers,
        'recent_readers': recent_readers,
        'threadmarks': threadmarks,
        'word_count': word_count,
        'pages': pages
    }

    # Save the story stats to a file
    with open('story_stats.json', 'w') as f:
        json.dump(story_stats, f)

def print_story_stats():
    global story_stats
    print("\n=============STORY STATS================")
    print(f"Title: {story_stats['title']}")
    print(f"Author: {story_stats['author']}")
    print(f"Start date: {story_stats['start_date']}")
    print(f"Watchers: {story_stats['watchers']}")
    print(f"Recent readers: {story_stats['recent_readers']}")
    print(f"Threadmarks: {story_stats['threadmarks']}")
    print(f"Words: {story_stats['word_count']}")
    print(f"Pages: {story_stats['pages']}")
    print("========================================\n")

def extract_content_from_link(link):
    print(f"Getting {link}...")
    r = requests.get(link)
    if r.status_code != 200:
        print(f"Failed to get {link} :: Error: {r.status_code}")
        exit()
    # contents.append(r.text)
    return r.text

def extract_posts_from_content(content, page_num = -1):
    print("Extracting posts from page", page_num, "...", end=' ')
    soup = BeautifulSoup(content, 'html.parser')

    # Get all the posts
    # page_posts = soup.find_all('article', class_=lambda x: x and 'message--post' in x)
    # Find the tag with the class="block-body js-replyNewMessageContainer"
    # Get all its children, which are the posts
    # Store the posts in a list
    parent_tag = soup.find(attrs={'class': 'block-body js-replyNewMessageContainer'})
    page_posts = parent_tag.findChildren('article', recursive=False)

    posts = []

    # For each post, extract the stats
    for post in page_posts:
        post_stats = extract_post_stats(post)

        # Add the stats to the list
        posts.append(post_stats)
    
    print("Done")

    return posts

def store_content_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# Given a story url and the number of pages, generate a list of links to each page
def generate_links(story_url, num_pages, start_page = 1):
    links = []
    for i in range(start_page, num_pages + 1):
        link = story_url + f'/page-{i}'
        links.append(link)
    return links

# Worker thread function that given a queue of links, extracts the posts from each link and adds them to the global list
def post_extraction_worker_thread(link_queue):
    global posts_list

    while True:
        # Get the next link from the queue
        link = link_queue.get()

        # If the link is None, exit the loop
        if link is None:
            break

        # Get the contents of the link
        content = extract_content_from_link(link)

        # Extract page number from the link
        # Find the last instance of 'page-' in the link
        # Then get the text after that
        page_num = link.rsplit('page-', 1)[-1]

        # Extract the posts from the contents
        posts = extract_posts_from_content(content, page_num)

        # Add the posts to the global list
        posts_list.extend(posts)

        # Mark the task as done
        link_queue.task_done()

    # Mark the task as done
    link_queue.task_done()

    # Exit the thread
    return

def load_posts_from_web(url):
    # Get the contents of the url
    contents = extract_content_from_link(url)

    # Store the contents in a file
    # store_content_to_file(contents, 'spacebattles.html')

    # Extract the story stats from the contents
    extract_story_stats(contents)
    print_story_stats()

    # Generate the links for all the pages
    links = generate_links(url, story_stats['pages'], 1)

    # Add all the links to the link_queue
    for link in links:
        link_queue.put(link)

    # Clear the posts_list
    posts_list.clear()

    # Create the worker threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=post_extraction_worker_thread, args=(link_queue,))
        t.start()
        threads.append(t)

    # Wait for all the tasks to be done
    link_queue.join()

    # Add None to the queue to signal the threads to exit
    for i in range(num_threads):
        link_queue.put(None)

    # Wait for all the threads to exit
    for t in threads:
        t.join()

    # Sort the list by post_number
    posts_list.sort(key=lambda x: x['post_number'])

    # Save the list to a file
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_list, f, ensure_ascii=False, indent=4)

def load_posts_from_file(filename):
    global posts_list
    # Check if the file exists
    if not os.path.isfile(filename):
        print(f"File {filename} does not exist")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        posts_list = json.load(f)

def load_story_stats_from_file(filename):
    global story_stats
    # Check if the file exists
    if not os.path.isfile(filename):
        print(f"File {filename} does not exist")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        story_stats = json.load(f)

def print_post_details(post):
    print(f"Author: {post['author']}")
    print(f"Threadmark: {post['is_threadmark']}")
    print(f"Post id: {post['id']}")
    print(f"Post number: {post['post_number']}")
    print(f"Date: {post['date']}")
    print(f"Likes: {post['likes']}")
    print(f"Content: {post['content']}")
    print("\n---- ---- ----\n")

def get_posts_by_author(posts, author):
    return list(filter(lambda x: x['author'] == author, posts))

def get_posts_by_threadmark(posts, threadmark):
    return list(filter(lambda x: x['is_threadmark'] == threadmark, posts))

def get_latest_post(posts):
    return max(posts, key=lambda x: x['post_number'])

def get_posts_after_number(posts, post_number):
    return list(filter(lambda x: x['post_number'] > post_number, posts))

def sort_posts_by_likes(posts):
    return sorted(posts, key=lambda x: x['likes'], reverse=True)

def check_for_new_updates():
    # Check if the file exists
    if not os.path.isfile('posts.json'):
        print("File posts.json does not exist. Getting posts from the web.")
        load_posts_from_web(url)
        return
    
    # Get story stats from the web
    # Get the contents of the url
    contents = extract_content_from_link(url)

    # Extract the story stats from the contents
    extract_story_stats(contents)

    # Get the number of pages
    num_pages = story_stats['pages']

    # Generate the link for the latest page
    latest_page_link = url + f'/page-{num_pages}'
    print(f"Latest page link: {latest_page_link}")

    # Get the contents of the latest page
    latest_page_contents = extract_content_from_link(latest_page_link)

    # Extract the posts from the latest page
    latest_page_posts = extract_posts_from_content(latest_page_contents, num_pages)

    # Get the latest post
    latest_post = get_latest_post(latest_page_posts)

    # Get the latest post number
    latest_post_number = latest_post['post_number']

    # load the posts from the file
    load_posts_from_file('posts.json')

    # Get the post number of the latest post in the file
    latest_post_in_file = get_latest_post(posts_list)
    latest_post_in_file_number = latest_post_in_file['post_number']

    # Check if there are any new posts
    if latest_post_number > latest_post_in_file_number:
        print("There are new posts!")
        print(f"Number of new posts: {latest_post_number - latest_post_in_file_number}")

        # Reload the posts from the web
        load_posts_from_web(url)

        # Get the new posts
        new_posts = get_posts_after_number(posts_list, latest_post_in_file_number)

        # Print story stats
        print_story_stats()

        # Print the new posts
        for post in new_posts:
            print_post_details(post)

    else:
        print("No new posts")

def print_top_posts_by_likes(posts, num_replies):
    # Get the top replies by likes
    top_replies = sort_posts_by_likes(posts)[:num_replies]

    # Print the top replies
    for reply in top_replies:
        print_post_details(reply)

def print_top_replies_by_likes_for_latest_threadmark(num_replies):
    print("Top 10 posts by likes after the latest threadmark: ", end='')
    threadmarked_posts = get_posts_by_threadmark(posts_list, True)
    latest_post = get_latest_post(threadmarked_posts)
    print(f"{latest_post['content']}")
    print("\n========================================\n")
    posts_after_latest = get_posts_after_number(posts_list, latest_post['post_number'])
    print_top_posts_by_likes(posts_after_latest, num_replies)

def print_top_replies_by_likes_for_each_threadmark(num_replies):
    threadmarked_posts = get_posts_by_threadmark(posts_list, True)
    threadmarked_posts.sort(key=lambda x: x['post_number'])

    print(f"Number of threadmarks: {len(threadmarked_posts)}")
    print(f"Printing top {num_replies} replies for each threadmark:")
    for i in range(len(threadmarked_posts)):
        # Get the current threadmark
        threadmark = threadmarked_posts[i]

        # Get the posts after the current threadmark
        posts_after_threadmark = get_posts_after_number(posts_list, threadmark['post_number'])

        # Get the next threadmark
        if i == len(threadmarked_posts) - 1:
            next_threadmark = None
        else:
            next_threadmark = threadmarked_posts[i + 1]

        # Get the posts before the next threadmark
        if next_threadmark is None:
            posts_before_next_threadmark = posts_after_threadmark
        else:
            posts_before_next_threadmark = list(filter(lambda x: x['post_number'] < next_threadmark['post_number'], posts_after_threadmark))

        # Sort the posts by likes
        posts_before_next_threadmark_sorted = sort_posts_by_likes(posts_before_next_threadmark)

        # Print the top posts
        print("\n========================================")
        print(f"{threadmark['content']}:: Replies: {len(posts_before_next_threadmark)}")
        print("========================================\n")
        print_top_posts_by_likes(posts_before_next_threadmark_sorted, num_replies)

if __name__ == '__main__':

    ## ====
    ## Three different ways to load posts. Uncomment the one you want to use.
    ## ====

    # load_posts_from_web(url)
    load_posts_from_file('posts.json')
    # check_for_new_updates()

    # Get the number of posts
    posts_count = len(posts_list)
    print(f"Number of posts: {posts_count}")
    print("\n========================================\n")

    ## ====
    ## Examples of how to use the functions.
    ## ====

    # print_top_replies_by_likes(posts_list, 10)
    # print_top_replies_by_likes_for_latest_threadmark(10)
    print_top_replies_by_likes_for_each_threadmark(2)

    ## Print the top 10 liked non-threadmarked posts. Uncomment the lines below to use.
    # non_threadmarked_posts = get_posts_by_threadmark(posts_list, False)
    # print_top_replies_by_likes(non_threadmarked_posts, 10)

    ## Get users with the most likes on non-threadmarked posts. Uncomment the lines below to use.
    # non_threadmarked_posts = get_posts_by_threadmark(posts_list, False)
    # users = {}
    # for post in non_threadmarked_posts:
    #     if post['author'] in users:
    #         users[post['author']] += post['likes']
    #     else:
    #         users[post['author']] = post['likes']
    # users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    # print(f"Number of users: {len(users)}")
    # print("Users with the most likes on non-threadmarked posts:\n")
    # for user in users[:10]:
    #     print(f"Username: {user[0]}, Likes: {user[1]}")
    #     print("Most liked post:",)
    #     user_posts = get_posts_by_author(non_threadmarked_posts, user[0])
    #     user_posts = sort_posts_by_likes(user_posts)
    #     print_post_details(user_posts[0])
