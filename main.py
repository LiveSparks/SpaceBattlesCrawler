import requests, threading, queue, datetime, json
from bs4 import BeautifulSoup

posts_list = []
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

    # Print the data
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Start date: {start_date}")
    print(f"Watchers: {watchers}")
    print(f"Recent readers: {recent_readers}")
    print(f"Threadmarks: {threadmarks}")
    print(f"Words: {word_count}")
    print(f"Pages: {pages}")

    print("\n========================================\n")

    return story_stats

def extract_content_from_link(link):
    print(f"Getting {link}...", end=' ')
    r = requests.get(link)
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        exit()
    print("Done")
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
    story_stats = extract_story_stats(contents)

    # Generate the links for all the pages
    links = generate_links(url, story_stats['pages'], 1)

    # Add all the links to the link_queue
    for link in links:
        link_queue.put(link)

    # Create the worker threads
    for i in range(num_threads):
        t = threading.Thread(target=post_extraction_worker_thread, args=(link_queue,))
        t.start()

    # Wait for all the tasks to be done
    link_queue.join()

def load_posts_from_file(filename):
    global posts_list
    with open(filename, 'r', encoding='utf-8') as f:
        posts_list = json.load(f)

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

if __name__ == '__main__':

    # load_posts_from_web(url)
    
    # # Sort the list by post_number
    # posts_list.sort(key=lambda x: x['post_number'])

    # # Save the list to a file
    # with open('posts.json', 'w', encoding='utf-8') as f:
    #     json.dump(posts_list, f, ensure_ascii=False, indent=4)


    load_posts_from_file('posts.json')

    # Get the number of posts
    posts_count = len(posts_list)
    print(f"Number of posts: {posts_count}")
    print("\n========================================\n")

    # Print the top 10 posts by likes after the latest threadmark
    print("Top 10 posts by likes after the latest threadmark: ", end='')
    threadmarked_posts = get_posts_by_threadmark(posts_list, True)
    latest_post = get_latest_post(threadmarked_posts)
    print(f"{latest_post['content']}")
    print("\n========================================\n")
    posts_after_latest = get_posts_after_number(posts_list, latest_post['post_number'])
    posts_after_latest_sorted = sort_posts_by_likes(posts_after_latest)
    for post in posts_after_latest_sorted[:10]:
        print_post_details(post)