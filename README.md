# website_connections
Web crawler tool for seeking sites with the same operator.


## instalation

### requirements

- python 2.7.10
- dependendences from requirements and tools
- API account (api key) at api.spyonweb.com 

### requirements
- beautifulsoup4==4.6.3
- certifi==2018.10.15
- chardet==3.0.4
- Click==7.0
- decorator==4.3.0
- Flask==1.0.2
- idna==2.7
- itsdangerous==1.1.0
- Jinja2==2.10
- MarkupSafe==1.1.0
- networkx==2.2
- requests==2.20.1
- urllib3==1.24.1
- Werkzeug==0.14.1

### install environment

```bash
virtualenv env

source env/bin/activate

pip install -r requirements.txt
```

## run script

```bash
python website_connections.py --domain alza.sk --graph alza.gexf 

or

python website_connections.py --domain alza.sk --graph alza.gexf --apikey API_KEY --wayback 2
```


## show results

Script writes an output file with suffix gexf . File can be loaded to Gephi.
