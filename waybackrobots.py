import os, sys, time
import re, json, requests, argparse

log = ""
ArchiveURLs = set()
RobotsTxtURLs = set()

def logger(out):
	global log
	log += out + '\n'
	out = " " + out
	print(out)

def argparser():
	parser = argparse.ArgumentParser(description='Robots.txt collector from wayback machine')
	parser.add_argument('-t', '--target', type=str, help='Target Host', required=True)
	parser.add_argument('-y', '--years', type=str, help='Years Range e.g[2000-2020]', required=True)
	parser.add_argument('-o', '--output', type=str, help='Output File', required=False)
	return parser.parse_args()

def getarchiveurls(target):
	response = requests.get("http://web.archive.org/cdx/m_search/cdx?url=*.{}/*&output=txt&fl=original&collapse=urlkey".format(target)).text
	for url in response.splitlines():
		if url not in ArchiveURLs:
			ArchiveURLs.add(url)

def getrobotstxturl(target):
	for robotstxturl in ArchiveURLs:		
		robotstxturl = re.findall(r".*?.%s.*/robots\.txt" % (target), robotstxturl)
		if len(robotstxturl) == 0:
			pass
		else:
			if robotstxturl[0] not in RobotsTxtURLs:
				RobotsTxtURLs.add(robotstxturl[0])
				logger('\t*- Found {}'.format(robotstxturl[0]))
	logger("")

def parserobotstxt(response):	
	response = response.splitlines()
	uri = []
	for line in response:		
		if not '#' in line:			
			if ':' in line and '/' in line and not 'http' in line and not 'https' in line:				
				uri.append(line.split(':')[1].strip())
	return uri

def fetchcontent(timestamp, url):
	dirs = []
	for ts in timestamp:
		response = requests.get("http://web.archive.org/web/{}if_/{}".format(ts, url)).text		
		_dirs = parserobotstxt(response)		
		dirs.append({ts: _dirs})		
	return dirs

def waybackuri(robotstxturl, year):	
	allow_statuses = [200]
	response = requests.get("http://web.archive.org/__wb/calendarcaptures?url={}&selected_year={}".format(robotstxturl, year)).json()
	try:
		for month in range(1, 12 + 1):
			months = response[month]
			weeks = len(months)
			currentday = 0
			for days in range(weeks):
				for day in months[days]:
					if day != None:
						currentday += 1
						if day != {}:
							timestamp = day['ts']
							status = day['st'][0]
							if status in allow_statuses:
								dirs = fetchcontent(timestamp, robotstxturl)
								for i in dirs:
									for ts, val in i.items():
										return ts, val
	except:
		return

def crawling(endpoint, target, fromyear, toyear):
	if '.' in endpoint:
		endpoint = endpoint.split('.')[0] + '\\.' + endpoint.split('.')[1]
	if '*' in endpoint:
		_tmp = [_temp.start() for _temp in re.finditer(r'\*', endpoint)]
		temp = endpoint[0:_tmp[0]]
		for i in range(len(_tmp)):
			if i in range(len(_tmp) - 1):
				temp = temp + "." + endpoint[_tmp[i]:_tmp[i+1]]
			else:
				temp = temp + "." + endpoint[_tmp[i]:len(endpoint)]
				endpoint = ".*" + temp + ".*"
	else:
		endpoint = ".*" + endpoint + ".*"
	response = requests.get("http://web.archive.org/cdx/search/cdx?url={}&matchType=prefix&from={}&to={}&output=txt&collapse=urlkey&fl=original".format(target, fromyear, toyear)).text	
	return re.findall(endpoint, response)

def checkendpoint(endpoint):
	response = requests.head(endpoint)
	return response.status_code

if __name__ == "__main__":
	args = argparser()
	target = args.target
	years = args.years
	if '-' not in years:
		print("Years Range e.g[2000-2020]")
	else:
		fromyear = int(years.split("-")[0])
		toyear = int(years.split("-")[1])
	output = args.output
	logger('\nSearching robots.txt for *.{}\n'.format(target))
	getarchiveurls(target)
	getrobotstxturl(target)
	for year in range(fromyear, toyear + 1):
		for robotstxturl in RobotsTxtURLs:
			logger("[%s]::[%s] Searching for [robots.txt] snapshot" % (year, robotstxturl))
			waybackuris = waybackuri(robotstxturl, year)
			endpoints = []
			if waybackuris != None:
				for endpoint in waybackuris[1]:
					if endpoint not in endpoints and '/' not in endpoints:
						logger("  |__ " + endpoint)
						endpoints.append(endpoint)
						for i in range(len(crawling(endpoint, target, fromyear, toyear))):
							logger("  |   |___ " + crawling(endpoint, target, fromyear, toyear)[i] + " => " + str(checkendpoint(crawling(endpoint, target, fromyear, toyear)[i])))
	if output:
		open(output, 'w').write(log)