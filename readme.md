# Project Kururugi (Offline Version)
## Analysis and plotting of the official vaccination statistics data from JKJAV Malaysia



## Features

Plotting of the official CTIF vaccination stastistics into readable interpreted graphs and charts. 

## Online Version

The online live version can be found here:
https://kururugi.blob.core.windows.net/kururugi/index.html

The source code for the live version can be found here:
https://github.com/aminhusni/project_kururugi
Please note that the live version source code will always be slightly behind a few commits
as I am making changes on the offline version first before deploying to the live version. 

## Installation

### Requirements:
- Python 3.9
- Pipenv
### Library & Dependencies
- Pandas
- Plotly
- matplotlib

### Step 1: Create virtual environment and install dependencies
```
pipenv install
````
### Step 2: Generate the static HTML plots
```
python ./main.py
````

#### The graphs will be plotted into `index.html` file. Open with any browser to view