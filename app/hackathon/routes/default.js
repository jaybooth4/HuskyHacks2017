var express = require('express');
var router = express.Router();

var multer  = require('multer');
var upload = multer({ dest: 'public/images' });

var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.sendFile(__dirname + '/public/idkDude/index.html');
});

router.get('/image.png', function (req, res) {
    res.sendfile(path.resolve('../public/images/image.png'));
});

var type = upload.single('recfile');

router.post('/', type, function (req,res) {

  /** When using the "single"
      data come in "req.file" regardless of the attribute "name". **/
  var tmp_path = req.file.path;

  /** The original name of the uploaded file
      stored in the variable "originalname". **/
  var target_path = 'public/images/' + req.file.originalname;

  /** A better way to copy the uploaded file. **/
  var src = fs.createReadStream(tmp_path);
  var dest = fs.createWriteStream(target_path);
  src.pipe(dest);
  src.on('end', function() { fs.unlink(tmp_path); res.render('index', { title: 'Upload complete', img: req.file.originalname }); });
  src.on('error', function(err) { fs.unlink(tmp_path); res.render('index', { title: 'Upload complete' }); });

});
module.exports = router;
