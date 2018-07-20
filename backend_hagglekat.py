import io
import os
import json
import pandas as pd

# Imports the Google Cloud client library
from google.cloud import vision_v1p1beta1
from google.cloud.vision_v1p1beta1 import types

def classify_image(image_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/chappers/Documents/DataScience/0_Method_DS/MethodDS-KaggleKat-8b57553f8dbf.json"

    # ### Start of Code to classify the image utilising the Google Vision API
    # Instantiates a client
    client = vision_v1p1beta1.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join(
            os.path.dirname('__file__'),
            image_name)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # create str_search to be used in the EBAY API call for KEYWORDS
    str_search = str(labels[0].description)

    # ### Code to utilise the Best Guess Label within Google Vision API

    web_scores=[]
    best_g=[]

    def detect_web(path):
        """Detects web annotations given an image."""
        client = vision_v1p1beta1.ImageAnnotatorClient()

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision_v1p1beta1.types.Image(content=content)

        # how doe we get this 
        response = client.web_detection(image=image)
        annotations = response.web_detection

        for label in annotations.best_guess_labels:
            print('\nBest guess label: {}'.format(label.label))
            best_g.append(format(label.label))

    # def report(annotations):
        """Prints detected features in the provided web annotations."""
        if annotations.pages_with_matching_images:
            print('\n{} Pages with matching images retrieved'.format(
                    len(annotations.pages_with_matching_images)))
            
            for page in annotations.pages_with_matching_images:
                print('Url   : {}'.format(page.url))
            
            #    if annotations.best_guess_labels:
            #        for label in annotations.best_guess_labels:
            #            print('\nBest guess label: {}'.format(label.label))

        if annotations.full_matching_images:
            print ('\n{} Full Matches found: '.format(
                    len(annotations.full_matching_images)))
            
            for image in annotations.full_matching_images:
                print('Url  : {}'.format(image.url))

        if annotations.partial_matching_images:
            print ('\n{} Partial Matches found: '.format(
                    len(annotations.partial_matching_images)))

            for image in annotations.partial_matching_images:
                print('Url  : {}'.format(image.url))

        if annotations.web_entities:
            print ('\n{} Web entities found: '.format(
                    len(annotations.web_entities)))

            for entity in annotations.web_entities:
                print('Score      : {}'.format(entity.score))
                print('Description: {}'.format(entity.description))
                if (entity.score>0.90):
                    web_scores.append(entity.description)

    # report(annotate('IMG_2934.jpg'))
    detect_web('IMG_2934.jpg')

    for rows in range(0,len(web_scores)):
        str_search=(str_search+" , "+ web_scores[rows])

    # ### Creating keyword string to pass to EBAY API

    # Create the Keyword String to then feed into the Ebay API, note the use of brackets and comma's, according to API
    # documentation, this then results in items being returned with any of words seperated by comma's, ie. OR logic
    keyword_string = best_g[0]
    # kstring = keyword_string.split(" ")
    keyword_string = str("(" + keyword_string + ")")
    keyword_string = keyword_string.replace(" ",",")
    return keyword_string

def make_clickable(val):
    # target _blank to open new window
    return '<a target="_blank" href="{}">{}</a>'.format(val, val)

def call_ebay_api(keyword_string):
    # ### Calling the EBAY API

    # call EBAY API and get offers, based on the keyword_string value.
    from ebaysdk.finding import Connection as Finding
    from ebaysdk.exception import ConnectionError
    
    try:
        api = Finding(siteid='EBAY-US', appid="MethodDa-MethodDa-PRD-babd43d69-a4097943", config_file=None)
        response = api.execute('findItemsByKeywords', {'keywords': keyword_string})
        # print(response.dict())
    except ConnectionError as e:
            print(e)
            print(e.response.dict())

    with open('image_G_output.json', 'w') as outfile:
        json.dump(response.dict(), outfile)

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content,'lxml')

    # ### Creating Pandas DataFrame from the image classification output, containing Item ID's, Title, URL, Price
    # create empty DataFrame
    col_names = ('Item_ID','Item_Title','Item_URL','Item_Price')
    deals_df = pd.DataFrame(columns = col_names)
    #
    totalentries = int(soup.find('totalentries').text)
    items = soup.find_all('item')
    item_id = soup.find_all('itemid')
    item_title = soup.find_all('title')
    item_url = soup.find_all('viewitemurl')
    item_price = soup.find_all('currentprice')
    # add in all deals found, into the pandas dataframe
    for rows in range(0,len(items)):
        deals_df = deals_df.append([{'Item_ID':item_id[rows].text,
                                     'Item_Title':item_title[rows].text,
                                     'Item_URL':item_url[rows].text,
                                     'Item_Price':item_price[rows].text}], 
                                   ignore_index=True)
    deals_df.style.format({'Item_URL': make_clickable})
    print("about to return")
    return deals_df