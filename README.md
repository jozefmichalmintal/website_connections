# website_connections
Web crawler tool for seeking sites with the same operator.


## instalation

### requirements

- python 2.7.10
- dependendences from requirements.txt
- API account (api key) at api.spyonweb.com 

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

It can be use app Gephi. Script writes an output file with suffix gexf . That can be loaded to the Gephi.
