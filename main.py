import requests
from bs4 import BeautifulSoup
import threading, queue

posts_list = []
link_queue = queue.Queue()

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


print(f"Getting {url}...", end=' ')
r = requests.get(url)
# print(f"Status code: {r.status_code}")
if r.status_code != 200:
    print(f"Error: {r.status_code}")
    exit()
print("Done")

# Store the contents in a file
filename = 'spacebattles.html'

# with open(filename, 'w', encoding='utf-8') as f:
#     f.write(r.text)

# # Process the file
# with open(filename, encoding='utf-8') as f:
#     contents = f.read()

contents = r.text

# Extract the main stats for the story
print("Extracting main stats...")
soup = BeautifulSoup(contents, 'html.parser')

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
import datetime
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

# Generate the links for all the pages
# url + /page-n
# n = 1 to pages
# Store the links in a list
links = []
# for n in range(30, pages + 1):
for n in range(pages + 1):
    links.append(url + f'/page-{n}')

# Get the contents of all the pages
# Store the contents in a list
contents = []
# contents.append(r.text)
for link in links:
    print(f"Getting {link}...", end=' ')
    r = requests.get(link)
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        exit()
    print("Done")
    contents.append(r.text)

# From all the pages, extract all the posts and their stats
# Store the stats in a list
posts = []
# for content in contents:
for i, content in enumerate(contents):
    print("Extracting posts from page", i + 1, "...", end=' ')
    soup = BeautifulSoup(content, 'html.parser')

    # Get all the posts
    # page_posts = soup.find_all('article', class_=lambda x: x and 'message--post' in x)
    # Find the tag with the class="block-body js-replyNewMessageContainer"
    # Get all its children, which are the posts
    # Store the posts in a list
    parent_tag = soup.find(attrs={'class': 'block-body js-replyNewMessageContainer'})
    page_posts = parent_tag.findChildren('article', recursive=False)

    # For each post, extract the stats
    for post in page_posts:
        post_stats = extract_post_stats(post)

        # Add the stats to the list
        posts.append(post_stats)
    
    print("Done")

# Get the number of posts
# Get the length of the list
posts_count = len(posts)
print(f"Number of posts: {posts_count}")

print("\n========================================\n")

# Print the details of 10 non-threadmark posts with the most likes
# Sort the list by likes
posts.sort(key=lambda x: x['likes'], reverse=True)

# Filter the list to only include non-threadmark posts
non_threadmark_posts = [post for post in posts if not post['is_threadmark']]

# Print the details of the first 10 posts
print("Details of 10 non-threadmark posts with the most likes:\n")
for post in non_threadmark_posts[:10]:
    print(f"Author: {post['author']}")
    print(f"Post id: {post['id']}")
    print(f"Date: {post['date']}")
    print(f"Likes: {post['likes']}")
    print(f"Content: {post['content']}")
    print()

# Print the details of all threadmark posts
# Filter the list to only include threadmark posts
threadmark_posts = [post for post in posts if post['is_threadmark']]
print("Details of all threadmark posts:")
for post in threadmark_posts:
    print(f"Author: {post['author']}")
    print(f"Post id: {post['id']}")
    print(f"Date: {post['date']}")
    print(f"Likes: {post['likes']}")
    print(f"Content: {post['content']}")
    print()