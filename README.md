First make sure you have a python virtualenv

python3 -m venv ./venv -> this creates one in current directory
source ./venv/bin/activate -> this activates it


now do
pip3 install -r requirements.txt

You need to also add your open API key to your local computer:

export OPEN_API_KEY=key here


now to run:
python3 api.py

