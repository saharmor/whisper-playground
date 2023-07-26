# install frontend
cd interface
yarn install

# install and run backend
cd ../backend
# Create a conda environment (to install Diart requirements) with Python 3.8 and activate it
conda create -n env python=3.8
conda activate env

# Install 'wheel'
pip install wheel

# Install diart requirements
conda install portaudio pysoundfile ffmpeg -c conda-forge

# Install packages from 'requirements.txt'
pip install -r requirements.txt
