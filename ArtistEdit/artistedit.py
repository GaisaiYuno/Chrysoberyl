# -*- coding:utf-8 -*-

import taglib, os, re, requests, json, time

MatchBrackets = True
source_path = './'
split_note = [';', '、', ',', 'feat.', '×', 'and', '/', '&', 'と']
processible_suffix = [".mp3", ".flac", ".ape", ".m4a", ".wav"]
connect_note = ';'

name_dic = {}
name_dic_path = "D:/name_dic.json"
pri_dic = {}
pri_dic_path = "D:/pri_dic.json"

delete_cv = ["(", ")", "（", "）", "cv:", "CV:", "cv：", "CV：", "cv.", "CV."]

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


music163_url = "https://ncm.icodeq.com/search"


def Get163Name(ArtistName):
    try:
        return name_dic[ArtistName]
    except:
        print("Query for " + ArtistName)
        while True:
            try:
                req = requests.get(music163_url,
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


with open(name_dic_path, 'r') as load_name_dic:
    name_dic = json.load(load_name_dic)

with open(pri_dic_path, 'r') as load_pri_dic:
    pri_dic = json.load(load_pri_dic)

artist_count = []

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
    song = taglib.File(source_path + file_names[i])
    song.tags['ALBUMARTIST'] = [connect_note.join(album_artist)]
    song.save()
    song.close()
