# qgis_extractor
This is a pyQGIS script to randomly sample from the LCDB5.0 database, extract images from a raster based on the random samples and generate masks of the image based on the polygons of the LCDB5.0 database
 

## Required API Keys
Users will need an account with Koordinates to request an API key with [https://data.linz.govt.nz] and [https://lris.scinfo.org.nz]. To apply for an account, users should click on **Log in** on the top right of the portal. Accounts are free and usually granted immediately. To generate an API key, users should click on their profile picture on the top right of the portal and select **API Keys**. 
![Requesting API Keys](apikey_request.png)
Users may optionally obtain an API key for [https://basemaps.linz.govt.nz] for access to a bigger catalog of rasters maps. Sign up is not required, however the API Keys are on a 90 days rotation. 

## Optional plugin
Users may choose to install the LINZ Data Importer [https://plugins.qgis.org/plugins/linz-data-importer/] or [https://github.com/linz/linz-data-importer/] to browse and discover other collection of data. Additional data portals that may be relevant includes Statistics New Zealand (Tatauranga Aotearoa) [datafinder.stats.govt.nz], Ministry for Environment (Manatū Mō Te Taiao) [data.mfe.govt.nz]. 

## Usage
Users can configure the parameters for the data extraction by editing the entries of the file extract_qgis.yaml. A sample yaml file is provided in this repository as a reference for the user.

## Note
Due to the size of the LCDB5.0 database, QGIS may become unresponsive when generating the intermediate files. We will attempt to alleviate the unresponsiveness in a future version of this script

## Motivation
This script was writen due to the challenges in automating the extractiong of crops of rasters from WMTS layers. While this script is originally written to label land covers types and extract masks of land covers, it should be straight forward to adapt this script for other applications. Do file a request for suggestions for enhancements.
