# MagGeo v1.0. 

## Annotate Earth's magnetic components from Swarm into GPS tracks

**Authors** | Fernando Benitez-Paez, Urška Demšar, Jed Long

**Contact**  | [Fernando.Benitez@st-andrews.ac.uk](mailto:Fernando.Benitez@st-andrews.ac.uk), [ud2@st-andrews.ac.uk](mailto:ud2@st-andrews.ac.uk), <jed.long@uwo.ca>

**nbviewer URL** | https://nbviewer.jupyter.org/github/maggeo

**Keywords** | Bird migration, data fusion, Earth’s magnetic field, Swarm, GPS tracking 

## Overview

Inspired by The Environmental Data Automated Track Annotation System (Env-DATA) Service  a tool on Movebank, where ecologists and animal movement researchers all over the world can link movement data with global environmental datasets. Including  hundreds of variables from a diverse set of data sources including the European Space Agency (ESA), the National Aeronautics and Space Administration (NASA), the US National Oceanic and Atmospheric Administration (NOAA), and others. EnvData allow researchers to annotate in space and time multiples environmental information to enrich their GPS tracks to analyze the  influence of several environmental variables in the trajectory. Using the [Env-DATA Track Annotation Service](https://www.movebank.org/cms/movebank-content/env-data-track-annotation) registered users on MoveBank are able to get environmental parameters—such as wind conditions, land use, vegetation, and snow cover—for the whole world. Using different interpolation methods users can include multiple environment variables selecting from a comprehensive list of datasets (you can browse the available dataset [here](https://www.movebank.org/cms/movebank-content/envdata-products)).

The second element that inspired **MagGeo** is having a tool to help researcher to get a better understanding over how the earth's magnetic field is being used by birds as one of their navigational strategies. Despite of there are several approach in this regards we know still have little knowledge about how birds can use the influence of the magnetic field for their migration patterns, especially for those long-distance migratory animals. Other studies have been reflecting into the magnetic field influence based on magnetic field estimation models, or using some displacement experiments with particular species. The disadvantage of those previous studies is the magnetic field is a highly dynamic force that have different impact around the earth every day. Having said that MagGeo wants to take advantage of what is considered best survey of the geomagnetic field and its temporal evolution - Swarm Constellation. Swarm is a ESA’s magnetic field mission, launched on 22 November 2013, consists of the three identical **Swarm satellites (Alpha, Bravo, and Charlie)**. Swarm A and C flying side-by-side (1.4° separation in longitude) at an altitude of 462 km (initial altitude) and Swarm B at higher orbit of 511 km (initial altitude) are equipped with the following set of [identical instruments](https://earth.esa.int/web/guest/missions/esa-eo-missions/swarm/instruments-overview).

The data products available from  Swarm are Level 1b and Swarm Level 2 products. These products include Swarm magnetic field models, ionospheric and thermospheric products, and others. MagGeo use the Swarm Level 1b data product as the corrected and formatted output from each of the three Swarm satellites. For more information about the Swarm Data Products click [here]( https://earth.esa.int/web/guest/missions/esa-eo-missions/swarm/data-handbook).

MagGeo has been deployed using a set of  Jupyter notebooks a powerful tool to run a python environment. Completely build in python 3.8 MagGeo is a well described program that will guide you through several steps to annotate your GPS trajectories with the geomagnetic field components reported by Swarm. You can access to Swarm Data products via HTTP or FTP using :

- via any HTTP browser at [http://swarm-diss.eo.esa.int](http://swarm-diss.eo.esa.int/)
- directly via an ftp client at [ftp://swarm-diss.eo.esa.int](ftp://swarm-diss.eo.esa.int/)

However **MagGeo** use [**VirES**](https://swarm-vre.readthedocs.io/en/latest/Swarm_notebooks/02a__Intro-Swarm-viresclient.html) (Virtual environments for Earth Scientists) a platform for data & model access, analysis, and visualisation for ESA’s magnetic mission **Swarm**. This is a powerful client with the [viresclient API](https://swarm-vre.readthedocs.io/en/latest/Swarm_notebooks/02c__viresclient-API.html) that provide several classes and methods defined in the vires client package. The `viresclient` Python package allows you to connect to the VirES server to download [Swarm](https://earth.esa.int/web/guest/missions/esa-operational-eo-missions/swarm) data and data calculated using magnetic models.

If you want to explore more about Jupyter Notebook and learn more about this tool you can clone or download the [FOSS4G UK 2019 Geoprocessing with Jupyter Notebooks workshop](https://github.com/samfranklin/foss4guk19-jupyter ). 

# Background

> ☝ Before moving on with this MagGeo you might want to take a look at:

## Earth's Magnetic Field

The Earth's magnetic field (or geomagnetic field ) is generated in the fluid outer core by a self-exciting dynamo process. Electrical currents flowing in the slowly moving molten iron generate the magnetic field. In addition to sources in the Earth's core the magnetic field observable at the Earth's surface has sources in the crust and in the ionosphere and magnetosphere[^1]

The Earth's magnetic field is described by seven components. These are **Declination (D)**, **Inclination (I)**, **Horizontal intensity (H)**, **Vertical intensity (Z)**, **total intensity (F)** and the **north (X)** and **east (Y)** components of the horizontal intensity. In most of the geomagnetic data sources the reference frame used to share the magnetic components is **NEC**, which is basically the same XYZ cartesian system.  By convention, declination is considered positive when measured east of north, Inclination and vertical intensity positive down, X (N) positive north, and Y(E) positive east. The magnetic field observed on Earth is constantly changing. [^2] 

<div class="alert alert-warning" role="alert">
  <strong>The Earth's magnetic field varies both in space and time</strong>
    That is why the relevance of <strong>MagGeo</strong> helping researchers to understand the small variations of the geomagnetic field across an animal movement trajectory. In particular having the annotated geomagnetic components at the the date and time the GPS point was collected.  The following image can help you to understand how the geomagnetic components can be represented and how are computed.
</div>

<img src="C:\Users\benit\OneDrive - University of St Andrews\St Andrews Project\Extension of ENV DATA\MagneticComponents-04.png" alt="2" style="zoom:40%;" />

Considering the point of measurement (*p*) as the origin of a Cartesian system of reference, the x-axis is in the geographic meridian directed to the north, y-axis in the geographic parallel directed to the east and z-axis parallel to the vertical at the point and positive downwards. Then we have:
$$
F= \sqrt{X^{2}+Y^{2}+Z^{2}} \hspace{1cm}or\hspace{1cm} 
F= \sqrt{N^{2}+E^{2}+C^{2}} \\
$$
$$
H = \sqrt{N^{2}+E^{2}} \\
D = \arctan\frac{E}{N} \\
I = \arctan\frac{C}{H} \\
$$

The unit of magnetic field intensity, strictly flux density, most commonly used in geomagnetism is the Tesla. At the Earth's surface the total intensity varies from 22,000 nanotesla (nT) to 67,000 nT.  The units of D and I are degrees.

# Data requirements

## Your trajectory must be in a csv format

There are three columns that  must be included to run the **MagGeo**. Make sure your GPS trajectory include all. **Latitude** , **Longitude** and **timestamp**.  Timestamp should follow the day/month/year Hour:Minute (**dd/mm/yyyy HH:MM**) format, Latitude and Longitude should be in decimal degrees ITFRS. Other Columns will be ignored. Here it is an example of how your GPS track should looks like.

![table_example.png](attachment:table_example.png)

Of course with knowledge of pandas and python you can manipulate your csv file and make the adjustment you need. Although if you want to run the **GeoMag** using our suggested steps, we would  recommend to set your GPS track csv file in a text editor before being included into **MagGeo**.

## Get your VirES for Swarm Token 

The magnetic data from Swarm will be downloaded using the *VirES for Swarm client* https://vires.services/oauth/accounts/login/. You will need to sign in there and get your token to get the data from the  VirES-Python-Client https://viresclient.readthedocs.io/en/latest/.  Here you can get the information about how to get the token: https://viresclient.readthedocs.io/en/latest/access_token.html

# Software Requirements

You need to be familiar with the following frameworks:

- [Anaconda](https://anaconda.org/about): Anaconda is a data-science platform that distributes software packages.

- [Conda](https://conda.io/en/latest/): Conda is an open source package management system for installing software in the terminal. Conda also allows isolation of environments.

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html):  Miniconda is a minimal installer (~70 MB) for conda, whereas Anaconda is ~700 MB and provides a full set of data science packages.

-  [Jupiter Notebook](https://jupyter.org/):  Jupyter notebook is popular environment for data scientists who are looking for a "pydata stack" (python packages of numpy, pandas, matplotlib, amongst others).  Jupyter notebooks, often referred to as iPython notebooks, offer a powerful and easy to use development environment to write code to explore, interact with and visualise data. Notebook allow you to run every step letting you to explore how the program is dealing with the data, making easy to share as a file or publish to the web. If you want to explore and learn how Jupiter Notebook works we have prepare a simple example for you.  `/notebook-overview.ipynb`

# How to build your Environment

**MagGeo** can be executed in any python environment you would prefer to use.  In the following steps we will suggest to use `Miniconda` together with a `requirements.yml` file that will provision all the packages with a virtual python environment.

- If you do not have either `Anaconda` or `miniconda` installed, then go and download `miniconda` from https://docs.conda.io/en/latest/miniconda.html.
- Select the Python 3.x option rather than the 2.x version to download and run the installer.
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

For Windows users, we recommend to to use the anaconda terminal app. Open the terminal from the start menu.
You will need to change the directory to where you downloaded the code repository. If you're using the terminal on Linux or macOS, it's the same synatax to change directory.

```
cd MagGeov1
```

Check your terminal can use the conda program with:

```
conda --version
```

Create the conda environment using the environment yaml file, this can take between 5 - 10 minutes:

```
conda env create --file MagGeoRequirements.yml
```

Activate the environment

```
conda activate MagGeoEnv
```

Launch a Jupyter Notebook

```
jupyter notebook
```

You are ready to go, now a tab window will pop up into your browser with the following address https://localhost:8080, follow all the steps either for a sequential or parallel mode. 

# Running MagGeo

There are two modes to run **MagGeo**. Sequential or Parallel, depending how much data you have to annotate. Sequential mode apply a traditional loops to going through the GPS track rows and process every row computing the magnetic components **MagGeo** is offering. If you have a big data set ( e.g. 1 million of records) you might want try the parallel mode. The parallel mode has some differences when you run the required libraries in a windows or Linux environment. We have tested **MagGeo** in a windows server environment, if you have Linux o MacOS you should not have any issue, the sequence is the same. 

* [1. Sequential Mode](#MagGeo_Sequential)
* [2. Parallel Mode](#MagGeo_Parallel)

The following image will help you to understand how the sequential and parallel mode differ, and how in parallel mode you should be able to use the full capacity of your machine. However it is quite important to identify when we need to use a parallel mode. For small datasets running **MagGeo** could be even slower than the sequential mode. 

<img src="C:\Users\benit\OneDrive - University of St Andrews\St Andrews Project\Extension of ENV DATA\ParallelMode-07.png" style="zoom: 50%;" />



# Getting help

**MagGeo** is work in progress and we are constantly making improvements that you call follow up in the commints made in the pubic GitHub repo. For general enquiries, trouble using **MagGeo**, scientific concepts behind, suggestion, bugs or improvements please email: [Fernando.Benitez@st-andrews.ac.uk](mailto:Fernando.Benitez@st-andrews.ac.uk), [ud2@st-andrews.ac.uk](mailto:ud2@st-andrews.ac.uk), <jed.long@uwo.ca> 

# References

[^1]: http://www.geomag.bgs.ac.uk/education/earthmag.html#_Toc2075547
[^2]: https://noaa.maps.arcgis.com/apps/MapJournal/index.html?appid=3b9045c4d1aa408694d3759d1aa5ede4

