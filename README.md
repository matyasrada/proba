<b>sendown.py</b> is a command-line tool what helps you download Sentinel-1A or Sentinel-2A data products 
from the <a href="https://scihub.copernicus.eu/dhus/">European Space Agency's Scientific Datahub.</a>
If you wish to download a Sentinel-2A product You can use this tool to fish into the data product 
and download data for only a certain tile.
<br><br>
The tool uses the <a href="http://docs.python-requests.org/en/master/"><b>request</b></a> HTTP library of Python so the request library
is need to be installed.
<br><br>
optional arguments:<br>
<ul>
  <li><b>-h, --help </b>           show this help message and exit <br></li>
  <li><b>-v, --version</b>          show program's version number and exit <br></li>
  <li><b>-l, --latlon </b>          WGS84 point coordinates i.e. Budapest 47.5 19.04 <br></li>
  <li><b>-s, --sat </b>             Which satellite/platform i.e. S1A or S2A <br></li>
  <li><b>-e, --extent</b>           Extent Coordinates xmin ymin xmax ymax i.e. 16.72 45.74 22.21 48.37 for Hungary <br></li>
  <li><b>-t, --tile  </b>           Sentinel-2A Tile ID i.e. T34TCT for Budapest <br></li>
  <li><b>-d, --dates  </b>          Date Interval, if not set it only checks that day <br></li>
  <li><b>-u, --username </b>        username - SciHub username, if not set it goes as guest by default<br></li>
  <li><b>-o, --odir </b>            Output Directory <br></li>
  <li><b>-y, --type </b>            Sentinel-1A Product Type i.e. RAW, SLC, GRD <br></li>
  <li><b>-q, --quicklook </b>       At first download quicklooks to the Output Directory <br></li>
</ul>

<b> Example 1 </b><br>

At first it asks for your password, queries the available Sentinel-2A products between the two dates for the 47.5 19.04 coordinate.
It lists the query result and you can specify which product needs to be downloaded by its number.

<pre>python sendown.py -u username -d 2016-01-01 2016-04-20 -l 47.5 19.04 -s S2A -o /data/tmp 
Password: *****
 -- Start querying products by latlon or extent
LatLon :  47.5,19.04
Platform :  Sentinel-2
Date Interval:  2016-01-01 2016-04-20
Product number :  15
No. QUERY RESULT 
1 S2A_OPER_PRD_MSIL1C_PDMC_20160414T030145_R079_V20160413T095322_20160413T095322.SAFE
2 S2A_OPER_PRD_MSIL1C_PDMC_20160412T164529_R036_V20160410T094029_20160410T094029.SAFE
3 S2A_OPER_PRD_MSIL1C_PDMC_20160324T230459_R079_V20160324T095436_20160324T095436.SAFE
4 S2A_OPER_PRD_MSIL1C_PDMC_20160321T155700_R036_V20160321T094426_20160321T094426.SAFE
5 S2A_OPER_PRD_MSIL1C_PDMC_20160315T064850_R079_V20160314T095144_20160314T095144.SAFE
6 S2A_OPER_PRD_MSIL1C_PDMC_20160311T232023_R036_V20160311T094116_20160311T094116.SAFE
7 S2A_OPER_PRD_MSIL1C_PDMC_20160222T212203_R079_V20160203T095601_20160203T095601.SAFE
8 S2A_OPER_PRD_MSIL1C_PDMC_20160214T194017_R079_V20160213T095503_20160213T095503.SAFE
9 S2A_OPER_PRD_MSIL1C_PDMC_20160210T193312_R036_V20160210T094131_20160210T094131.SAFE
10 S2A_OPER_PRD_MSIL1C_PDMC_20160125T202507_R079_V20160124T100753_20160124T100753.SAFE
11 S2A_OPER_PRD_MSIL1C_PDMC_20160121T181553_R036_V20160121T095704_20160121T095704.SAFE
12 S2A_OPER_PRD_MSIL1C_PDMC_20160114T194758_R079_V20160114T100217_20160114T100217.SAFE
13 S2A_OPER_PRD_MSIL1C_PDMC_20160111T204639_R036_V20160111T094922_20160111T094922.SAFE
14 S2A_OPER_PRD_MSIL1C_PDMC_20160104T182030_R079_V20160104T100050_20160104T100050.SAFE
15 S2A_OPER_PRD_MSIL1C_PDMC_20160101T180916_R036_V20160101T095719_20160101T095719.SAFE
* All product
 -- Enter the number of the product(s) you wish to download.
 -- Listed above i.e. 1,2,4
 -- If you need all products than just enter * 
Number(s):
</pre>

<b> Example 2 </b>
<br><br>
If you set the -q option on, the tool will download the quicklook images of the products to your output directory.<br>
It might help deciding whether the product is worth downloading i.e. cloud-free etc.
<br>
<pre>
python sendown.py -u username -d 2016-01-01 2016-04-20 -l 47.5 19.04 -s S2A -o /data/tmp -q
</pre>

<b> Example 3 </b><br>
<pre>
python sendown.py -u username -d 2016-01-01 2016-04-20 -t T34TCT -o /data/tmp -q
</pre>

If you commit a query with the -t, --tile option It will not be necessery to sepcify the satellite type. The tool uses <i>sen2tiles.csv</i> file to 
to perform the search for the tile. So the <i>sen2tiles.csv</i> file needs to be the same folder as the sendown.py script. 
After specifing the requested products you got the corresponding bands for the tile to your output directory.
<br>

<b> Example 4 </b><br>
<pre>
python sendown.py -u username -d 2016-01-01 2016-04-20 -l 47.5 19.04 -s S1A -o /data/tmp -q
</pre>

You can searh for Sentinel-1A products with the obvious S1A argument.
<br>
You can the product type for thhe Sentinel-1A product by setting the -y option to GRD or SLC or RAW. Without setting the option It queries all three types.
<br><br>
<b> Example 5  </b><br>
<pre>
python sendown.py -u username -d 2016-01-01 2016-04-20 -l 47.5 19.04 -s S1A -y GRD -o /data/tmp -q
</pre>
<br>


