from settings import javascript, headless, count, postcount, board, imgboard, randthreads, image
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import string
from random import choice, randint
import threading
import math
from random_word import RandomWords # https://pypi.org/project/Random-Word/
from proxy import proxyoptions

cattylinks = []

# text that will be posted, make it random
r = RandomWords()
l = string.ascii_letters+string.digits
# {r.get_random_word()} for a random word
def text(body):
    body.fill(f'''my transbian ass:
{r.get_random_word()}
{choice(l)}
{choice(l)}
{choice(l)}
{choice(l)}
''')


def post(threadnum):
    for i in range(math.ceil(postcount/count)):
        with sync_playwright() as p:
            chrome = p.chromium.launch(headless=headless, proxy=proxyoptions)
            try:
                context = chrome.new_context(java_script_enabled=javascript, no_viewport=True, user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A')
                page = context.new_page()
                stealth_sync(page)
                page.route("**/*", lambda route: route.abort() 
                    if route.request.resource_type == "image" 
                    else route.continue_() 
                ) 
                if randthreads == True:
                    page.goto(f'{imgboard}{choice(cattylinks)}')
                else:
                    page.goto(f'{imgboard}/{board}/index.html')
                body = page.query_selector('textarea[name="body"]')
                subimage = page.query_selector('input[type="file"]')
                submit = page.query_selector('input[type="submit"]')
                text(body)
                subimage.set_input_files(image) #images\{str(randint(1,3000))}.png
                page.screenshot(path=fr'during\image-{threadnum}.png')
                submit.click()
                try: # nojs only i think
                    error = page.query_selector('h2')
                    print(f"Post has failed, \"{error.text_content()}\" Thread-{threadnum}") 
                    chrome.close()
                except:
                    print(f'Post was succesful {threadnum}')
                    page.screenshot(path=fr'results-pass\pass-{threadnum}.png')
                    chrome.close()
            except:
                page.screenshot(path=fr'results-fail\fail-{threadnum}.png')
                chrome.close()
                print(f'Failed, attempting again {threadnum}')


def randomthreads():
    with sync_playwright() as p:
        # no need for proxy, they cant ban you if you dont post.
        browser = p.chromium.launch()
        context = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A')
        page = context.new_page()
        stealth_sync(page)
        page.goto(f'{imgboard}/{board}/catalog.html')

        if 'soyjak.party' in imgboard.lower():
            links = page.query_selector_all(f'a[href^="/{board}/thread/"]')
        else:
            links = page.query_selector_all(f'a[href^="/{board}/res/"]')

        for link in links:
            href = link.get_attribute('href')
            cattylinks.append(href)


if randthreads == True:
    randomthreads()

# threading

threads = []

for i in range(count):
    t  = threading.Thread(target=lambda: post(str(i)))
    t.daemon = True
    threads.append(t)

for i in range(count):
    threads[i].start()

for i in range(count):
    threads[i].join()
