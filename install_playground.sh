# install frontend
cd interface
yarn install

# install and run backend
cd ../backend
# Create a conda environment (to install Diart requirements) with Python 3.8 and activate it
echo "Current shell: $SHELL"

conda create -n env python=3.8
# Detect the shell name from the SHELL environment variable
shell_name="$(basename "$SHELL")"
# Run the appropriate conda init command based on the detected shell
case "$shell_name" in
    "bash")
        conda init bash
        ;;
    "zsh")
        conda init zsh
        ;;
    "fish")
        conda init fish
        ;;
    *)  # Handle other or unknown shells
        echo "Unsupported shell: $shell_name"
        echo "Please initialize Conda manually for your shell."
        exit 1
        ;;
esac
# Now, your shell should be properly configured to use 'conda activate'
echo "Your shell has been configured to use 'conda activate'."
conda activate env

# Install diart requirements
conda install portaudio pysoundfile ffmpeg -c conda-forge

# Install packages from 'requirements.txt'
pip install -r requirements.txt
