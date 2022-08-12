# -*- coding:utf-8 -*-

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


music163_url = "https://music.cyrilstudio.top/"


def Get163Name(ArtistName):
    try:
        return name_dic[ArtistName]
    except:
        print("Query for " + ArtistName)
        while True:
            try:
                req = requests.get(music163_url + "search",
                                   params={
                                       'keywords': ArtistName,
                                       'type': 100,
                                       'limit': 5
                                   })
                break
            except:
                print("API Error")
                time.sleep(5000)

        req = req.json()
        try:
            Artists = req['result']['artists']
        except:
            Artists = []

        if (len(Artists) == 0):
            print(ArtistName + " doen't exist in 163 music!")
            name_dic[ArtistName] = input("Please enter your choice!")
        else:
            print(
                "Please enter your choice!(0 for original, str for your own)")
            for i in range(len(Artists)):
                print((str)(i + 1) + "." + Artists[i]['name'])
            enter = input()
            if (enter.isdigit() == False):
                name_dic[ArtistName] = enter
                name_dic[enter] = enter
            else:
                choice = (int)(enter) - 1
                if (choice == -1):
                    name_dic[ArtistName] = ArtistName
                else:
                    name_dic[ArtistName] = Artists[choice]['name']
                    name_dic[Artists[choice]['name']] = Artists[choice]['name']
        return name_dic[ArtistName]


def Get163Lyrics(netease_id, file_name):
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
            print("No tlyric!")
        if len(lyric.toLRC().strip()) > 0:
            with open(source_path + file_name + ".lrc", 'w',
                      encoding='utf-8') as dump_lyric:
                print("Lyric saved to " + source_path + file_name + ".lrc")
                dump_lyric.write(lyric.toLRC())
                dump_lyric.close()


with open(name_dic_path, 'r') as load_name_dic:
    name_dic = json.load(load_name_dic)

with open(pri_dic_path, 'r') as load_pri_dic:
    pri_dic = json.load(load_pri_dic)

artist_count = []

if DownloadLRC:
    album_id = input("Input album id:")
    if (album_id != "-1"):
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
        print("Processing Album:", alb_req["album"]["name"])
    else:
        alb_req = ""


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def generate_alias(item, field1, field2):
    name = item[field1]
    try:
        alias = item[field2]
        if (len(alias) > 0):
            return name + "（" + ','.join(alias) + "）"
        else:
            print("No alias!")
            return name
    except:
        print("No alias!")
        return name


for i in range(len(file_names)):
    suffix = os.path.splitext(file_names[i])[-1]
    if suffix not in processible_suffix:
        continue
    song = taglib.File(source_path + file_names[i])
    try:
        split_result = SplitArtists(song.tags['ARTIST'][0])
    except:
        print("Open error!")
        continue
    try:
        if (len(song.tags) == 0):
            song.tags['TRACKNUMBER'] = [i + 1]
        print("--------------------------------------")
        print("Now processing " + song.tags['TRACKNUMBER'][0] + "." +
              song.tags['TITLE'][0])
    except:
        print("Processing error!")

    # song_id=(int)(song.tags['TRACKNUMBER'][0].split('/')[0])

    processed_artist = []
    for j in range(len(split_result)):
        result = MatchCV(split_result[j].strip())
        for k in range(len(result)):
            processed_artist.append(result[k])

    for j in range(len(processed_artist)):
        result = processed_artist[j]
        for k in range(len(delete_cv)):
            result = result.replace(delete_cv[k], "")
        if (result == ""):
            continue
        result = Get163Name(result.strip())
        with open(name_dic_path, 'w') as dump_name_dic:
            json.dump(name_dic, dump_name_dic)
        if (result == ""):
            continue
        processed_artist[j] = result

    if DownloadLRC:
        if (alb_req != ""):
            max_ratio = 0
            netease_id = 0
            matched_name = ""
            matched_song = alb_req["songs"][0]
            for netease_song in alb_req["songs"]:
                ratio = string_similar(netease_song["name"],
                                       song.tags['TITLE'][0])
                if (ratio > max_ratio):
                    max_ratio = ratio
                    netease_id = netease_song["id"]
                    matched_name = netease_song["name"]
                    matched_song = netease_song
            print("Matched", matched_name, "Ratio", max_ratio)
            choice = "yes"
            if (max_ratio < 0.5):
                choice = input(
                    "Match ratio is low, sure to continue? (yes/no)")
            if (choice != "yes" and not choice.isdigit()):
                continue
            if (choice.isdigit()):
                Get163Lyrics((int)(choice), os.path.splitext(file_names[i])[0])
            else:
                if Use163Name:
                    song.tags['TITLE'][0] = generate_alias(
                        matched_song, "name", "alia")
                print("Netease ID:", netease_id)
                Get163Lyrics(netease_id, os.path.splitext(file_names[i])[0])
        else:
            netease_id = input("Input Netease ID:")
            if (netease_id != -1):
                Get163Lyrics(netease_id, os.path.splitext(file_names[i])[0])

    processed_artist = list(set(processed_artist))
    print("Artist list:")
    print(processed_artist)

    artist_count += processed_artist
    song.tags['ARTIST'][0] = connect_note.join(processed_artist)
    song.save()
    song.close()

artist_count = list(set(artist_count))
print("Album artist list:")
print(artist_count)
enter = input(
    "Please enter the number of album artists and choose album artists (or str for your own):"
)
album_artist = []
if (enter.isdigit()):
    for i in range((int)(enter)):
        index = (int)(input())
        album_artist.append(artist_count[index - 1])
else:
    album_artist.append(enter)

album163name = generate_alias(alb_req["album"], "name", "alias")

for i in range(len(file_names)):
    suffix = os.path.splitext(file_names[i])[-1]
    if suffix not in processible_suffix:
        continue
    song = taglib.File(source_path + file_names[i])
    try:
        split_result = SplitArtists(song.tags['ARTIST'][0])
    except:
        print("Open error!")
        continue
    try:
        if (len(song.tags) == 0):
            song.tags['TRACKNUMBER'] = [i + 1]
        print("Now processing " + song.tags['TRACKNUMBER'][0] + "." +
              song.tags['TITLE'][0])
    except:
        print("Processing error!")
    song.tags['ALBUMARTIST'] = [connect_note.join(album_artist)]
    song.tags['ALBUM'] = [album163name]
    song.save()
    song.close()
