# Chrysoberyl
A Set of Tools for Music Metadata and Cover Editing.

为音乐元数据编辑以及封面编辑准备的一系列工具。

## Chrysoberyl Web

![artist](\src\artist.png)

![music](\src\music.PNG)

![settings](\src\settings.PNG)

更多请查看 https://github.com/GaisaiYuno/Chrysoberyl/wiki

## Squarize

将你的长方形图片变成更好看的正方形，图片自动居中。

## ArtistEdit

自动化整理音乐元数据中 ARTIST 和 ALBUMARTIST 值。

特性：

- 自动分割，如 `A、B` 分割为 `A` 和 `B`。
- 识别 CV，如 `A（CV:B）,C（CV.D）` 分割为 `C` 和 `D`。
- 利用网易云 API 和本地字典，将不同描述的艺术家归为一类，避免歧义，如 `Tsukagoshi Yuuichirou`、`塚越 雄一朗` 、`碓氷悠一朗` 和 `つかごし ゆういちろう` 归为 `塚越雄一朗`。
- 自动整理专辑艺术家。
- 比 Mp3tag 更加省时。
- 根据网易云专辑 ID，计算歌曲标题相似度，自动下载对应歌词。并且自动整合中日文歌词在一起。
- 根据网易云的数据，自动修正标题。

依赖：

- `taglib`
- `requests`
- `pylrc`
- `difflib`
