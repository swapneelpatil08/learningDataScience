from flask import  Flask, render_template, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import logging
import os
import re
import json

if os.path.exists("youtube_scrape_logs.log"):
    os.remove("youtube_scrape_logs.log")

logging.basicConfig(filename="youtube_scrape_logs.log", level=logging.INFO)

app = Flask(__name__)

yt_url = "https://www.youtube.com/@PW-Foundation/videos"

@app.route("/", methods = ["GET"])
def home_page():
    return render_template("index.html")

@app.route("/getContent", methods= ["POST", "GET"])
def getContent():
    if request.method == "POST":
        try:
            action = request.form["operation"]
            numberOfVideos = int(request.form["numberOfVideos"])
            response = BeautifulSoup(urlopen(yt_url).read(), 'html.parser')
            ytd = response.find_all("script")
            json_txt = re.search("var ytInitialData = (.+)[,;]{1}", str(ytd[36])).group(1)
            json_data = json.loads(json_txt)
            content = (
                    json_data
                    ['contents'] ['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']
                )
            
            current_results = get_video_details(action, content, numberOfVideos)
            return render_template("result.html", results = [current_results])

        except Exception as e:
            logging.exception(e)
            return "Oops, something went wrong!"

    return "Data loaded"



def get_video_details(action, content, numberOfVideos):
    all_details = []
    all_details_csv = []
    
    for data in content:
        for key, value in data.items():
            if type(value) == dict:
                if "videoURL" == action:
                    details = value['content']['videoRenderer']['videoId']
                    all_details.append(f"https://www.youtube.com/watch?v={details}&ab_channel=PhysicsWallahFoundation")
                    videoURL = f"https://www.youtube.com/watch?v={value['content']['videoRenderer']['videoId']}&ab_channel=PhysicsWallahFoundation"
                    urlofThumbnail = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    theTitle = value['content']['videoRenderer']['title']['runs'][0]['text']
                    numberOfViews = value['content']['videoRenderer']['viewCountText']['simpleText']
                    timeOfPosting = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    break

                elif "urlofThumbnails" == action:
                    details = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    all_details.append(details)
                    videoURL = f"https://www.youtube.com/watch?v={value['content']['videoRenderer']['videoId']}&ab_channel=PhysicsWallahFoundation"
                    urlofThumbnail = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    theTitle = value['content']['videoRenderer']['title']['runs'][0]['text']
                    numberOfViews = value['content']['videoRenderer']['viewCountText']['simpleText']
                    timeOfPosting = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    break
                
                elif "theTitle" == action:
                    details = value['content']['videoRenderer']['title']['runs'][0]['text']
                    all_details.append(details)
                    videoURL = f"https://www.youtube.com/watch?v={value['content']['videoRenderer']['videoId']}&ab_channel=PhysicsWallahFoundation"
                    urlofThumbnail = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    theTitle = value['content']['videoRenderer']['title']['runs'][0]['text']
                    numberOfViews = value['content']['videoRenderer']['viewCountText']['simpleText']
                    timeOfPosting = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    break

                elif "numberOfViews" == action:
                    details = value['content']['videoRenderer']['viewCountText']['simpleText']
                    details = details.split(" ")[0]
                    all_details.append(details)
                    videoURL = f"https://www.youtube.com/watch?v={value['content']['videoRenderer']['videoId']}&ab_channel=PhysicsWallahFoundation"
                    urlofThumbnail = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    theTitle = value['content']['videoRenderer']['title']['runs'][0]['text']
                    numberOfViews = value['content']['videoRenderer']['viewCountText']['simpleText']
                    timeOfPosting = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    break

                elif "timeOfPosting" == action:
                    details = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    all_details.append(details)
                    videoURL = f"https://www.youtube.com/watch?v={value['content']['videoRenderer']['videoId']}&ab_channel=PhysicsWallahFoundation"
                    urlofThumbnail = value['content']['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                    theTitle = value['content']['videoRenderer']['title']['runs'][0]['text']
                    numberOfViews = value['content']['videoRenderer']['viewCountText']['simpleText']
                    timeOfPosting = value['content']['videoRenderer']['publishedTimeText']['simpleText']
                    break
            
        line = f"{videoURL}, {urlofThumbnail}, {theTitle}, {numberOfViews}, {timeOfPosting}" 
        all_details_csv.append(line)
            
        if(len(all_details) == numberOfVideos):
            break

    write_csv_file(action, all_details)
    write_csv_file("youtube_scrape", all_details_csv)
    return all_details

def write_csv_file(file_name, all_details):
    try:
        fname = f"{file_name}.csv"
        if os.path.exists(fname):
            os.remove(fname)

        f = open(fname, "w")
        header_line = "videoURL, urlofThumbnail, theTitle, numberOfViews, timeOfPosting\n"
        f.write(header_line)
        for i in all_details:
            f.write(i)
            f.write("\n")
    except Exception as e:
        logging.error(e)
    finally:
        f.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)