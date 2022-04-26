The following locations/lines will require changing the file path to one that is applicable to you.

1) app.py:
 	line 12 - This should be the absolute path to the parser folder
		line: sys.path.insert(0, r"/Users/stuti/Desktop/Utrition/parser")
 	line 184 - This should be the absolute path to the directory where the analysis report should be downloaded
		line: with open('/Users/stuti/Desktop/userOutput.html', 'w+') as outputFile:

2) Download.py: 
	line 186 - Multiple portions of this line will need to be changed.
	
		line: outputFile.write('<!doctype html><html lang="en" ng-app="nutritionApp"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=0.5"><title>Utrition Analysis</title><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap.css"/><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap-theme.css"/><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/css/app.css"/><style>ul {list-style: none} h1 {text-align: center;} li { background: white; }li:nth-child(odd) { background: #D3D3D3; }h2 {text-align: center;} div.report {font-size: 25px} p {text-align: center; font-size: 25px}</style></head><body><div class="header"><img class="logo" src="/Users/stuti/Desktop/Utrition/static/images/EngageHealth-Color-P.png" alt="Engage Health"/></div><h1>Utrition Analysis Report</h1>')
	
		The following portions need to be changed:
		a) href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap.css"
			Path should be replaced with the absolute path to the bootstrap.css file
		b) href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap-theme.css"
			Path should be replaced with the absolute path to the bootstrap-theme.css file
		c) href="/Users/stuti/Desktop/Utrition/static/css/app.css"
			Path should be replaced with the absolute path to the app.css file
		d) src="/Users/stuti/Desktop/Utrition/static/images/EngageHealth-Color-P.png" 
			Path should be replaced with the absolute to the EngageHealth-Color-P.png image file

3) DNA_Parser.py:
	line 14 - This should be the absolute path to the directory where the uploaded DNA file is located
		line: FILEPATH="/Users/stuti/Desktop/"
	