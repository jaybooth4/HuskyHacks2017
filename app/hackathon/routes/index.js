var express = require('express');
var router = express.Router();

var multer  = require('multer');
var upload = multer({ dest: 'python_modules/unknown_pictures' });
var PythonShell = require('python-shell');
var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Welcome' });
});

router.get('/image.png', function (req, res) {
    res.sendfile(path.resolve('../public/images/image.png'));
});

var type = upload.single('recfile');

router.post('/', type, function (req,res) {

    if (req.file) {
      /** When using the "single"
          data come in "req.file" regardless of the attribute "name". **/
      var tmp_path = req.file.path;

      /** The original name of the uploaded file
          stored in the variable "originalname". **/
      var target_path = 'python_modules/unknown_pictures/' + req.file.originalname;

      /** A better way to copy the uploaded file. **/
      var src = fs.createReadStream(tmp_path);
      var dest = fs.createWriteStream(target_path);
      src.pipe(dest);
      src.on('end', function() {
        src = fs.createReadStream(target_path);
        target_path2 = 'public/images/' + req.file.originalname;
        dest = fs.createWriteStream(target_path2);
        src.pipe(dest);

        var options = {
            mode: 'text',
            pythonPath: '/usr/local/bin/python3',
            pythonOptions: ['-u'],
            scriptPath: __dirname + '/../python_modules/',
            args: []
        };

        fs.unlink(tmp_path);

        PythonShell.run('neuralNet.py', options, function (err, results) {
            if (err) throw err;
            // results is an array consisting of messages collected during execution
            console.log('results: %j', results);

            res.render('index', { results: results, img: req.file.originalname });
        });
      });
      src.on('error', function(err) {
        fs.unlink(tmp_path); res.render('index', { title: 'Upload complete' });
      });
    } else {
        res.render('index', { title: 'Please include a file first' });
    }
});
module.exports = router;
