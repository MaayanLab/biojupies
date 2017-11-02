set -e
cd jupyter
wget -O JupyterNotebook.ipynb $DOWNLOAD
jupyter nbconvert --inplace --to notebook --execute JupyterNotebook.ipynb
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.iopub_data_rate_limit=10000000000 --NotebookApp.default_url="notebooks/JupyterNotebook.ipynb" --NotebookApp.token=