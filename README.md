# Amazon Product Price alert

```bash
# install the requirements

# windows
python -m pip install -r requirements.txt

# linux
python3 -m pip install -r requirements.txt
```

## What does the script do?
- fetch the product page and scrape product name and price
- check if price in budget
- if product is in budget then sends email to alert user
- if not then it will perform same operations

## Instructions
- replace the `url` with your product( use only Amazon India product URL )
- replace your budget
- replace your email and password
    - Enable two factor auth for gmail to generate secure app password
- change `timeout` if you want default 60 seconds.
- add `user-agent`

```bash
# run script 

# windows
python main.py

# linux
python3 main.py
```
