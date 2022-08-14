# -*- coding:utf-8 -*-

from markupsafe import escape
from flask import Flask
from flask import request
from flask_cors import CORS
import taglib
import os
import re
import requests
import json
import time
import pylrc
import difflib

MatchBrackets = True
DownloadLRC = True
Use163Name = True
source_path = './'
split_note = [';', '、', ',', 'feat.', '×', 'and', '/', '&', 'と']
processible_suffix = [".mp3", ".flac", ".ape", ".m4a", ".wav"]
connect_note = ';'
music163_url = "https://ncma-ruddy.vercel.app/"

name_dic = {}
name_dic_path = "D:/name_dic.json"
pri_dic = {}
pri_dic_path = "D:/pri_dic.json"

delete_cv = ["(", ")", "（", "）", "cv:", "CV:", "cv：", "CV：", "cv.", "CV."]
delete_brackets = ["【", "】", "『", "』"]

file_names = os.listdir(source_path)


def BreakDownByBrackets(Artist):
    Artists = []
    flag = False
    temp = ""
    for i in range(len(Artist)):
        if (Artist[i] == '(' or Artist[i] == '（'):
            flag = True
        if (flag):
            temp += Artist[i]
        if (Artist[i] == ')' or Artist[i] == '）'):
            flag = False
            Artists.append(temp)
            temp = ""
    return Artists

def MatchCV(Artist):
    SearchResult = BreakDownByBrackets(Artist)
    if (MatchBrackets and len(SearchResult) >= 1):
        return SearchResult
    else:
        ArtistList = []
        ArtistList.append(Artist)
        return ArtistList

def SplitArtists(Artist):
    for key in pri_dic:
        Artist = Artist.replace(key, pri_dic[key])
    for i in range(len(split_note)):
        if (len(Artist.split(split_note[i])) > 1):
            return Artist.split(split_note[i])
    ArtistList = []
    ArtistList.append(Artist)
    return ArtistList

def Get163Lyrics(netease_id, file_path):
    while True:
        try:
            req = requests.get(music163_url + "lyric",
                               params={
                                   'id': netease_id,
                               })
            break
        except:
            print("API Error")
            time.sleep(5000)
    req = req.json()
    if (req["lrc"] and req["lrc"]["lyric"] != ""):
        lyric = pylrc.parse(req["lrc"]["lyric"])
        try:
            if (req["tlyric"]):
                tlyric = pylrc.parse(req["tlyric"]["lyric"])
                for tsub in tlyric:
                    for jsub in lyric:
                        if (jsub.time == tsub.time and tsub.text != ""):
                            for brackets in delete_brackets:
                                tsub.text = tsub.text.replace(brackets, "")
                            jsub.text += "「" + tsub.text + "」"
        except:
            print("114514")
        if len(lyric.toLRC().strip()) > 0:
            path = os.path.splitext(file_path)[0]+'.lrc'
            with open(path, 'w',
                      encoding='utf-8') as dump_lyric:
                dump_lyric.write(lyric.toLRC())
                dump_lyric.close()
                return "歌词保存到 "+path
        else:
            return "无歌词"


with open(name_dic_path, 'r') as load_name_dic:
    name_dic = json.load(load_name_dic)

with open(pri_dic_path, 'r') as load_pri_dic:
    pri_dic = json.load(load_pri_dic)

app = Flask(__name__)
CORS(app)
inside_set = set()

for someone in name_dic:
    inside_set.add(name_dic[someone])


def processArtist(artists):
    print(artists)
    split_result = SplitArtists(artists)
    processed_artist = []
    for j in range(len(split_result)):
        result = MatchCV(split_result[j].strip())
        for k in range(len(result)):
            processed_artist.append(result[k])

    for j in range(len(processed_artist)):
        result = processed_artist[j]
        for k in range(len(delete_cv)):
            result = result.replace(delete_cv[k], "")
        result = result.strip()
        if (result == ""):
            continue
        processed_artist[j] = result
    return processed_artist


@app.route("/artist", methods=['POST'])
def getArtistInfo():
    # 1.存在，而且就是艺术家
    # 2.存在，而且有对应关系
    # 3.不存在，需要搜索
    artist = request.form["artist"]
    if (artist in inside_set):
        return {"inside": 1}
    elif (artist in name_dic):
        return {"inside": 2}
    else:
        return {"inside": 3}


@app.route("/song", methods=['POST'])
def getSongInfo():
    try:
        path = request.form["path"]
        song = taglib.File(path)
        tags = song.tags
        song.close()
        print(tags)
        if "ARTIST" in tags:
            tags["ARTIST"] = processArtist(''.join(tags["ARTIST"]))
        else:
            tags["ARTIST"] = ['']
        if "ALBUMARTIST" in tags:
            tags["ALBUMARTIST"] = processArtist(''.join(tags["ALBUMARTIST"]))
        else:
            tags["ALBUMARTIST"] = ['']
        if "TITLE" not in tags:
            tags["TITLE"] = ['']
        return {"success": True, "tags": json.dumps(tags)}
    except Exception as e:
        return {"success": False, "error": e}


@app.route("/savesong", methods=['POST'])
def saveSong():
    try:
        print(request.form)
        path = request.form["path"]
        song = taglib.File(path)
        tags = json.loads(request.form["tags"])
        tags["ARTIST"] = [connect_note.join(tags["ARTIST"])]
        tags["ALBUMARTIST"] = [connect_note.join(tags["ALBUMARTIST"])]
        song.tags = tags
        song.save()
        song.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": e}


@app.route("/savesetting", methods=['POST'])
def saveSetting():
    global MatchBrackets, DownloadLRC, Use163Name, music163_url, split_note, delete_cv
    print(request.form)
    MatchBrackets = request.form["match"] == 'true'
    DownloadLRC = request.form["lyric"] == 'true'
    Use163Name = request.form["neteasedata"] == 'true'
    music163_url = request.form["api"]
    split_note = request.form["split"].split(' ')
    delete_cv = request.form["cv"].split(' ')
    return {"success": True}


@app.route("/getsetting", methods=['POST'])
def getSetting():
    return {
        "match": MatchBrackets,
        "lyric": DownloadLRC,
        "neteasedata": Use163Name,
        "api": music163_url,
        "split": ' '.join(split_note),
        "cv": ' '.join(delete_cv)
    }


@app.route("/getlrc", methods=['POST'])
def getLRC():
    try:
        return {"success": True, "info": Get163Lyrics(request.form["netease_id"], request.form["path"])}
    except:
        return {"success": False}


@app.route("/search/<string:query>", methods=['GET'])
def search(query):
    try:
        query = escape(query)
        ret = {"success": True, "results": []}
        for artist in inside_set:
            if re.match(query.lower(), artist.lower()):
                ret["results"].append(
                    {
                        "name": artist,
                        "value": artist,
                        "description": artist,
                        "text": artist,
                    }
                )
        return ret
    except:
        return {"success": False}


@app.route("/search/", methods=['GET'])
def search2():
    try:
        ret = {"success": True, "results": []}
        for artist in inside_set:
            ret["results"].append(
                {
                    "name": artist,
                    "value": artist,
                }
            )
        return ret
    except:
        return {"success": False}


@app.route("/getartist", methods=['POST'])
def getArtist():
    try:
        ArtistName=request.form["name"]
        ret = {"success": True, "artists": []}
        try:
            req = requests.get(music163_url + "search",
                               params={
                                   'keywords': ArtistName,
                                   'type': 100,
                                   'limit': 5
                               })
        except:
            print("API Error")
            time.sleep(5000)
        req = req.json()
        try:
            Artists = req['result']['artists']
        except:
            Artists = []
        
        for i in range(len(Artists)):
            ret["artists"].append(
                {
                    "name":Artists[i]['name'],
                    "url":Artists[i]['img1v1Url']
                }
            )
        ret["artists"]=json.dumps(ret["artists"])
        return ret
    except Exception as e:
        return {"success": False,"e":e}

def save_name_dic():
    with open(name_dic_path, 'w') as dump_name_dic:
        json.dump(name_dic, dump_name_dic)

@app.route("/adddic" ,methods=['POST'])
def addDic():
    try:
        artist1=request.form["artist1"]
        artist2=request.form["artist2"]
        name_dic[artist1]=artist2
        inside_set.add(artist2)
        save_name_dic()
        return {"success":True}
    except:
        return {"success": False}

# 输入album_id,music_tags，输出一个list 代表匹配度，163id

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

@app.route("/getalbum", methods=['POST'])
def getAlbum():
    try:
        album_id = request.form["album_id"]
        print(album_id)
        while True:
            try:
                alb_req = requests.get(music163_url + "album",
                                       params={
                                           'id': album_id,
                                       })
                break
            except:
                print("API Error")
                time.sleep(5000)
        alb_req = alb_req.json()
        print(alb_req)
        music_tags = json.loads(request.form["music_tags"])
        print(music_tags)
        matched_list = []
        for i in range(len(music_tags)):
            print(i)
            my_song = music_tags[i]
            print(my_song)
            max_ratio = 0
            netease_id = 0
            matched_name = ""
            for netease_song in alb_req["songs"]:
                ratio = string_similar(
                    netease_song["name"], my_song['TITLE'][0])
                if (ratio > max_ratio):
                    max_ratio = ratio
                    netease_id = netease_song["id"]
                    matched_name = netease_song["name"]
            matched_list.append(
                {"ratio": max_ratio, "netease_id": netease_id, "name": matched_name})
        return {"success": True, "matched_list": json.dumps(matched_list)}
    except:
        return {"success": False}