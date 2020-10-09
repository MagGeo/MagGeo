# MagGeo v1.0. 

## Annotation tool to combine Earth's magnetic data from Swarm satellites with GPS trajectories

**Contact**  | [Fernando.Benitez@st-andrews.ac.uk](mailto:Fernando.Benitez@st-andrews.ac.uk), [ud2@st-andrews.ac.uk](mailto:ud2@st-andrews.ac.uk), <jed.long@uwo.ca>

**nbviewer URL** | https://nbviewer.jupyter.org/github/maggeo

**Keywords** | Bird migration, data fusion, Earth’s magnetic field, Swarm, GPS tracking 

## Overview

MagGeo is a tool that helps ecologists or animal movement researchers to link  earth's magnetic field data from satellite source to GPS trajectories. Inspired by the Environmental Data Automated Track Annotation System (Env-DATA) Service a tool from Movebank and help researcher to get a better understanding about the geomagnetic variations across the GPS trajectories. 

MagGeo is entirely build in python and using Jupyter Notebook offers a several ways to annotate GPS tracks with the geomagnetic components using the data from one of the up-to-date satellite sources Swarm Constellation. MagGeo will create a enriched GPS track with the following components:

- **Latitude** from the GPS Track.
- **Longitude** from the GPS Track.
- **Timestamp** from the GPS Track.
- **Magnetic Field Intensity** mapped as Fgps in nanoTeslas (nT).
- **N (Northwards) component** mapped as N in nanoTeslas (nT).
- **E (Eastwards) component** mapped as E. in nanoteslas (nT).
- **C (Downwards or Center)** component mapped as C in nanoTeslas (nT).
- **Horizontal component** mapped as H in nanoTeslas (nT).
- **Magnetic Declination or dip angle** mapped as D in degrees
- **Magnetic Inclination** mapped as I in degrees
- **Total Points** as the amount of Swarm measures included in the ST-IDW process from the trajectories requested in the three satellites.
- **Minimum Distance** mapped as MinDist, representing the minimum distance amount the set of identified point inside the Space Time cylinder and each GPS point location.
- **Average Distance** mapped as AvDist, representing the average distance amount the set of distances between the identified Swarm Point in the Space Time cylinder and the GPS Points location.

Researchers particularly ecologists now can study the annotated table to analyze the Spatio-temporal variation across any GPS trajectory.

<img src="./images/GitHubImage.png">


## How to install and Run MagGeo

To install and run MagGeo you need to follow the following steps.

### 1. Installation and Set up your python environment

**MagGeo** can be executed in any python environment you would like to use.  In the following steps we will suggest to use `Miniconda` together with a `requirements.yml` file that will provide all the packages with a virtual python environment.

- If you do not have either `Anaconda` or `miniconda` installed, then go and download `miniconda` from https://docs.conda.io/en/latest/miniconda.html.
  - Select the **Python 3.x option** rather than the 2.x version to download and run the installer
  - For Windows users, here's a link to the [Win64 Installer](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe). Download this and run the exe installer
  - For those on MacOS or Linux and are happy with the terminal, try either:

```
# get the latest MacOS 64-bit installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
# get the latest linux 64-bit installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

Download a copy of this repository, either downloading of the zip or via git, with:

```
git clone git@github.com: 
```

**For Windows users**, we recommend to use the **anaconda terminal app**. 

1. Open the **anaconda terminal app** from the *Start menu*.
2. You will need to change the directory to where you downloaded the code repository. If you're using the terminal on Linux or macOS, it's the same syntax to change directory.

```
cd MagGeoRepo
```

​		*Check your terminal can use the conda program with:*

```
conda --version
```

3. Create the conda environment using the environment yml file, this can take between 5 - 15 minutes:

```
conda env create --file MagGeoRequirements.yml
```

4. Activate the environment

```
conda activate MagGeoEnv
```

5. Launch a Jupyter Notebook

```
jupyter notebook
```

You are ready to go, now a tab window will pop up into your browser with the following address https://localhost:8080, follow all the steps described in main Notebook.

### 2. Getting a VirES web client Token

**MagGeo** use [**VirES**](https://swarm-vre.readthedocs.io/en/latest/Swarm_notebooks/02a__Intro-Swarm-viresclient.html) (Virtual environments for Earth Scientists) a platform for data & model access, analysis, and visualization for ESA’s magnetic mission **Swarm**. This is a powerful client with the [viresclient API](https://swarm-vre.readthedocs.io/en/latest/Swarm_notebooks/02c__viresclient-API.html) that provide several classes and methods defined in the vires client package. The `viresclient` Python package allows you to connect to the VirES server to download [Swarm](https://earth.esa.int/web/guest/missions/esa-operational-eo-missions/swarm) data and data calculated using magnetic models.

1. First to all you need to create an account and Sign up using https://vires.services/oauth/accounts/signup/
2. Once you have created the account, Log In https://vires.services/
3. Follow the instructions in https://viresclient.readthedocs.io/en/latest/access_token.html to get your token.
4. Copy and Paste your token in section **1.3 Adding your VirES web client Token** once you are running MagGeo.

### 3. Running MagGeo

MagGeo v1.0 is a set of Jupyter Notebooks, you will find four notebooks (.ipynp). 

* [Main Notebook](https://github.com/MagGeo/MagGeo-Annotation-Program/blob/master/MagGeo%20-%20Home.ipynb) : An initial and descriptive notebook where you can get detail information about MagGeo, the sample data used, background concepts and software requirements.
* [Sequential Mode](https://github.com/MagGeo/MagGeo-Annotation-Program/blob/master/MagGeo%20-%20Sequential%20Mode.ipynb): Annotation Notebook applying a sequential mode. Using  a traditional loop to going through the GPS track rows and process every row computing the magnetic components. Particularly useful for small datasets. 
* [Parallel Mode](https://github.com/MagGeo/MagGeo-Annotation-Program/blob/master/MagGeo%20-%20Parallel%20Mode.ipynb):  If you have a "big" dataset ( e.g. 1 million of records) you might want try the parallel mode. The parallel mode has some differences when you run the required libraries in a windows or Linux environment. We have tested **MagGeo** in a windows server environment.
* [Notebook basics](https://github.com/MagGeo/MagGeo-Annotation-Program/blob/master/Notebook%20-%20Basics.ipynb): If you are not familiar with Jupiter Notebooks and want to learn about the basics over how to run the notebooks before try the annotate tool. You can try this notebook to get the basics elements to run cells, read data, and plot some a basic chart.

The following image will help you to understand how the sequential and parallel mode differ, and how in parallel mode you should be able to use the full capacity of your machine. However it is quite important to identify when we need to use a parallel mode. For small datasets running **MagGeo** in Parallel mode could be even slower than the sequential mode. 

<img src="/images/Sequential_ParallelMode-Jupyter.png">

# Getting help

**MagGeo** is work in progress and we are constantly making improvements that you call follow up with the commints made in the pubic GitHub repo. For general enquiries, scientific concepts, suggestions, bugs or improvements using **MagGeo** please email: [Fernando.Benitez@st-andrews.ac.uk](mailto:Fernando.Benitez@st-andrews.ac.uk), [ud2@st-andrews.ac.uk](mailto:ud2@st-andrews.ac.uk), <jed.long@uwo.ca> 

# References

*[1](http://www.geomag.bgs.ac.uk/education/earthmag.html#_Toc2075547)

*[2](https://noaa.maps.arcgis.com/apps/MapJournal/index.html?appid=3b9045c4d1aa408694d3759d1aa5ede4)


