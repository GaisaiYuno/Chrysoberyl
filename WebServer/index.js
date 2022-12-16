var express = require('express')
var bodyParser = require('body-parser');
var fs = require('fs');
var Path=require('path');
var os = require('os');
var child_process = require("child_process");
const { exec } = require('child_process');
var app = express()

music_suffix=[".mp3", ".flac", ".ape", ".m4a", ".wav"]

function includesuffix(suffix){
	for (const v of music_suffix){
		if (v==suffix){
			return true;
		}
	}
	return false;
}

app.use(bodyParser.urlencoded({
	extended: true
}))

app.get('/', function (req, res) {
	res.sendFile(__dirname + "/" + "index.html");
})
app.get('/settings', function (req, res) {
	res.sendFile(__dirname + "/" + "settings.html");
})
app.get('/addartist', function (req, res) {
	res.sendFile(__dirname + "/" + "addartist.html");
})
app.get('/song', function (req, res) {
	res.sendFile(__dirname + "/" + "song.html");
})
app.use('/dist', express.static(Path.join(__dirname, 'dist')));

app.post('/', function (req, res) {
	filepath = req.body.path
	var exists = fs.existsSync(filepath);
	if (exists) {
		var stat = fs.lstatSync(filepath);
		if (stat.isDirectory()) {
			res.send({ success: true, files: fileList(filepath) })
		}
		else {
			res.send({ success: false })
		}
	}
	else {
		res.send({ success: false })
	}
})

app.post('/prepath',function(req,res){
	res.send({success:true,pre_path:Path.resolve(req.body.path,"..")})
})

function fileList(path) {
	ret=[];
	fs.readdirSync(path).forEach(
		function(item){
			var stat=fs.lstatSync(path+"/"+item)
			ret.push({
				path:path+"/"+item,
				name:item,
				isdir:stat.isDirectory(),
				ismusic:includesuffix(Path.extname(item)),
				time:fs.statSync(path+"/"+item).mtime.getTime()
			})
		}
	)
	ret.sort(function(a,b){return -a.time+b.time;})
	return ret;
}

/*
if (exists) {
	var stat = fs.lstatSync(filepath);
	if (stat.isFile()) {
		res.writeHead(200, { 'Content-Type': 'text' });
		return fs.createReadStream(filepath).pipe(res);
	} else if (stat.isDirectory()) {
		res.writeHead(200, { 'Content-Type': 'text/html' });
		return res.end(fileList(filepath));
	}
} else {
	res.writeHead(404, { 'Content-Type': 'text/html' });
	return res.end('<h2>没有找到文件</h2');
}
*/

/**
 * 列出指定文件目录，默认当前目录
 */
/*
function fileList(path = defaultPath) {
	var html = '';
	// 如果是windows系统
	if ('Windows_NT' == os.type()) {
		var index = path.indexOf(':');
		path = path.slice(index + 1);
	}
	fs.readdirSync(path).forEach(function(item) {
		var href = (path + '/' + item).replace('//', '/');
		html += '<a href="' + href + '">' + item + '</a><br/>';
	});
	return html;
}*/

var server = app.listen(3000)

console.log('Chrysoberyl server running at http://127.0.0.1:3000/');