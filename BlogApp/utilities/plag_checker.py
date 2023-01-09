import requests
from requests.exceptions import Timeout
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
import urllib3
import requests
from bs4 import BeautifulSoup
import re
from re import search
from googlesearch import search

import re
from nltk.util import ngrams, pad_sequence, everygrams
from nltk.tokenize import word_tokenize
from nltk.lm import MLE, WittenBellInterpolated
import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter

from newspaper import Article
from newspaper import Config

config = Config()
config.request_timeout = 10

def get_links(query,cnt=10):
    links = []
    for i in search(query, tld='com', lang='en', num=cnt, start=0, stop=cnt, pause=1.5):
        if not i.endswith((".txt", ".pdf", ".mp3")):    #avoids hundred over pages long research papers; you can remove this to improve accuracy but scrapping a 200 page pdf will take an excruciatingly long time...
            links.append(i)
    return links
        

def scrape_website(URL):
    retry = HTTPAdapter(max_retries=3)
    session = requests.Session()
    session.mount(str(URL), retry)
    try:
        
        try:
            r = requests.get(URL, timeout=5)   
        except Timeout:
            print('Timeout Error, unsuccessful in scraping ' + str(URL))
            return ''
        except ConnectionError:
            print('Connection Error, unsuccessful in scraping ' + str(URL))
            return ''
           
        soup = BeautifulSoup(r.text, 'html5lib')

        content = ''

        ct = soup.find_all('p')
        for i in range(len(ct)):
            content += soup.find_all('p')[i].get_text()

        ct = soup.find_all('div')
        for i in range(len(ct)):
            content += soup.find_all('div')[i].get_text()

        #clean the string
        content = re.sub('\s+', ' ', content)
        content = re.sub('<[^>]+>', ' ', content)
        content = content.split('\\')
        content = ''.join((content[0], content[-1]))
        content = content.split('{')
        content = ''.join((content[0], content[-1]))
        content = content.split('}')
        content = ''.join((content[0], content[-1]))
       
        cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        content = re.sub(cleaner, '', content)

        return str(content)
    
    except urllib3.exceptions.ProtocolError:
        print('Protocol Error, unsuccessful in scraping ' + str(URL))
        return ''
    
    except requests.exceptions.ConnectionError:
        print('Connection Error, unsuccessful in scraping ' + str(URL))
        return ''


def scrape_website_np3k(URL):
    content = ''
    try:
        website = Article(str(URL), language='en', config=config)
        
        website.download()
        website.parse()
        website.nlp()
        
        content += website.text
        content += ', '.join([str(elem) for elem in website.keywords])
        content += website.summary
        
        return str(content)
    except:
        return ''
    
    
def load_dataset(query, cnt=10):
    overall = ''
    all_links = get_links(query, cnt)
    if all_links:
        for link in all_links:
            try:
                overall += scrape_website_np3k(link)
            except:
                overall += scrape_website(link)
            print('Scrapped ' + str(link))
                            
    f = open("BlogApp/utilities/train.txt", "w")    
    f.write(overall.lower())
    f.close()
    
    
''' main function which also returns the links that the content is plagaraised from
def main(query):
    with open('test.txt') as f:
        test_text = f.read()
    f.close()
    
    overall = ''
    content_in = []
    for link in get_links(query):
        scrapped = scrape_website(link)
        overall += scrapped
        if search(test_text, scrapped):
            content_in.append(link)
        print('Scrapped ' + str(link))
    
    print(content_in)
    
    f = open("train.txt", "w")    
    f.write(overall)
    f.close()
    '''


def plc():
    
    # Training data file
    train_data_file = "BlogApp/utilities/train.txt"

    # read training data
    with open(train_data_file) as f:
        train_text = f.read().lower()
    f.close()

    # apply preprocessing (remove text inside square and curly brackets and rem punc)
    train_text = re.sub(r"\[.*\]|\{.*\}", "", train_text)
    train_text = re.sub(r'[^\w\s]', "", train_text)

    # set ngram number
    n = 4

    # pad the text and tokenize
    training_data = list(pad_sequence(word_tokenize(train_text), n, 
                                    pad_left=True, 
                                    left_pad_symbol="<s>"))

    # generate ngrams
    ngrams = list(everygrams(training_data, max_len=n))
    print("Number of ngrams:", len(ngrams))

    # build ngram language models
    model = WittenBellInterpolated(n)
    model.fit([ngrams], vocabulary_text=training_data)
    print(model.vocab)

    # testing data file
    test_data_file = "BlogApp/utilities/test.txt"

    # Read testing data
    with open(test_data_file) as f:
        test_text = f.read().lower()
    test_text = re.sub(r'[^\w\s]', "", test_text)

    # Tokenize and pad the text
    testing_data = list(pad_sequence(word_tokenize(test_text), n, 
                                    pad_left=True,
                                    left_pad_symbol="<s>"))
    print("Length of test data:", len(testing_data))

    # assign scores
    scores = []
    for i, item in enumerate(testing_data[n-1:]):
        s = model.score(item, testing_data[i:i+n-1])
        scores.append(s)

    scores_np = np.array(scores)

    # set width and height
    width = 8
    height = np.ceil(len(testing_data)/width).astype("int32")
    print("Width, Height:", width, ",", height)

    # copy scores to rectangular blank array
    a = np.zeros(width*height)
    a[:len(scores_np)] = scores_np
    diff = len(a) - len(scores_np)

    # apply gaussian smoothing for aesthetics
    a = gaussian_filter(a, sigma=1.0)

    # reshape to fit rectangle
    a = a.reshape(-1, width)

    # format labels
    labels = [" ".join(testing_data[i:i+width]) for i in range(n-1, len(testing_data), width)]
    labels_individual = [x.split() for x in labels]
    labels_individual[-1] += [""]*diff
    labels = [f"{x:60.60}" for x in labels]

    # create heatmap
    fig = go.Figure(data=go.Heatmap(
                    z=a, x0=0, dx=1,
                    y=labels, zmin=0, zmax=1,
                    customdata=labels_individual,
                    hovertemplate='%{customdata} <br><b>Score:%{z:.3f}<extra></extra>',
                    colorscale="burg"))
    fig.update_layout({"height":height*28, "width":1000, "font":{"family":"Courier New"}})
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.show()

    
