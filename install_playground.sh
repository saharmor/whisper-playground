# install frontend
cd interface
yarn install

# install and run backend
cd ../backend && python3 -m venv venv
source ./venv/bin/activate
pip install wheel
pip install -r requirements.txt