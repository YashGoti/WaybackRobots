# WaybackRobots

It find all robots.txt year by year (that you given) from webarchives [http://web.archive.org] and requests to target and find live URL's for target.

### Requiremtns 

* re
* json
* requests
* argparse

### Options

|Options|Description|
|-------|-----------|
|-t|Target Host(Domain)|
|-y|Year Range e.g(2000-2020)<br>So it will find robots.txt for year 2000 to 2020|
|-o|Output file (Use txt format)|

### Installation
```
git clone https://github.com/YashGoti/WaybackRobots.git
cd WaybackRobots
pip3 install -r requirements.txt
```

### Usage
```
python3 waybackrobots.py -t google.com -y 1998-2020 -o google.com.txt
```

### Inspired By
```
BitTheByte[https://github.com/BitTheByte/] - https://github.com/BitTheByte/WayRobots
```

### Special Thanks
```
Kathan Patel[https://github.com/KathanP19] - for give me a good idea to do this.
```
