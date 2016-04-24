#!/usr/bin/env python
import os
import datetime
import pprint
import requests
from xml.etree import ElementTree
import csv
import urlparse
import getpass
import shutil
import argparse
import zipfile
from PIL import Image

desc = """This command-line tool helps you download Sentinel-1A and \
Sentinel-2A data products from the European Space Agency's Scientific\
Datahub. 
It also allows us to download only one Sentinel-2A tile from a product."""

def ParseProducts(xml):
    tree = ElementTree.ElementTree(ElementTree.fromstring(xml.content))
    root = tree.getroot()
    entryList = tree.findall('{http://www.w3.org/2005/Atom}entry')
    HEADER = ["href", "quicklook", "filename",
              "orbitdirection", "platformserialidentifier",
              "instrument", "processingbaseline",
              "processinglevel", "size"]
    Sentinel2Ameta = []
    for entry in entryList:
        links = entry.findall("{http://www.w3.org/2005/Atom}link")
        qSen = {}
        qSen['href'] = links[0].attrib['href']
        qSen['quicklook'] = links[2].attrib['href']
        strings = entry.findall("{http://www.w3.org/2005/Atom}str")
        for string in strings:
            if string.attrib['name'] in HEADER:
                qSen[string.attrib['name']] = string.text
        Sentinel2Ameta.append(qSen)
    return Sentinel2Ameta

def QueryTileCoords(tileid):
    path = os.path.dirname(os.path.realpath(__file__))
    tiledatabase = path + os.sep + 'sen2tiles.csv'
    tiledict = {}
    with open(tiledatabase, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            tiledict[row[0]] = [row[2], row[1]]
    return tiledict[tileid]

def DownloadFile(user, password, requrl, opath, auth):
    valid = False
    while valid == False:
        with open(opath, 'wb') as f:
            r = requests.get(requrl, auth=auth, verify=False, stream=True)
            f.write(r.content)

        if os.path.splitext(opath)[1] == ".zip":
            try:
                print zipfile.is_zipfile(opath)
                valid = zipfile.is_zipfile(opath)
                print "valid: ", valid

            except:
                print "Failed downloading. Sendown is gonna try it again."
                print requrl

        if os.path.splitext(opath)[1] in [".jp2", ".jpg"]:
            try:
                img = Image.open(opath)
                valid = True
                img = None
            except:
                print "Failed downloading. Sendown is gonna try it again."

def QueryProducts(user, password, query):
    try:
        session = requests.Session()
        session.auth = (user, password)
        response = requests.get(query, auth=session.auth, verify=False)
        if response.status_code == 503:
            print ("503 error code - Service Unavailable")
        return response
    except Exception as e:
        print " Request: ", e

def MenuText(listofdicts, quick, odir):
    print 50 * '-'
    print "No. QUERY RESULT "
    print 50 * "-"
    for i in range(1, len(listofdicts) + 1):
        print i, listofdicts[i - 1]['filename']
    print "* All product"
    print 50 * "-"
    if (quick == True):
        print ' -- Check your quicklooks in your output directory : ', odir
    print " -- Enter the number of the product(s) " \
          "you wish to download."
    print " -- Listed above i.e. 1,2,4"
    print " -- If you need all products than just enter * "

def GetEntries(url, sessionauth):
    response = requests.get(url, auth=sessionauth, verify=False)
    tree = ElementTree.ElementTree(ElementTree.fromstring(response.content))
    root = tree.getroot()
    linklist = tree.findall("{http://www.w3.org/2005/Atom}entry")

    return linklist

def MakeRootDir(rootnodeurl, odir, sessionauth):
    entries = GetEntries(rootnodeurl, sessionauth)
    for entry in entries:
        for child in entry:
            if child.tag == "{http://www.w3.org/2005/Atom}title":
                odir = odir + os.sep + child.text
                if not os.path.exists(odir):
                    os.mkdir(odir)
    return odir

def PullTile(nodeurl, tileid, sessionauth):
    try:
        tildict = {}
        entries = GetEntries(nodeurl, sessionauth)
        for entry in entries:
            for child in entry:
                if child.tag == "{http://www.w3.org/2005/Atom}link":
                    if 'title' in child.attrib.keys():
                        if child.attrib['title'] == 'Nodes':
                            inurl = urlparse.urljoin(nodeurl, child.attrib[
                                'href']) + "('GRANULE')/Nodes"
                            tileentries = GetEntries(inurl, sessionauth)
                            for tileentry in tileentries:
                                for child in tileentry:
                                    if "{http://www.w3.org/2005/Atom}title" ==\
                                            child.tag:
                                        if tileid == child.text[-13:-7]:
                                            tildirurl = inurl + \
                                            "('%s')/Nodes('IMG_DATA')/Nodes" \
                                            % (child.text)
                                            bandentries = GetEntries(tildirurl,
                                            sessionauth)
                                            for bandentry in bandentries:
                                                for bandchild in bandentry:
                                                    if bandchild.tag == \
                                        '{http://www.w3.org/2005/Atom}title':
                                                        tildict[bandchild.text]\
                                                            = tildirurl + \
                                                            "('%s')/$value" %\
                                                              (bandchild.text)
        return (tildict)
    except Exception as e:
        print e

def main():
    parser = argparse.ArgumentParser(description=desc,
                                   version='%prog version 0.1')

    parser.add_argument('-l', '--latlon',
                      help='WGS84 point coordinates i.e. Budapest 47.5 19.04',
                      dest='latlon',
                      nargs=2, action='store')
    parser.add_argument('-s', '--sat',
                      help='Which satellite/platform i.e. S1A or S2A',
                      dest='platform')
    parser.add_argument('-e', '--extent',
                      help='Extent Coordinates xmin ymin xmax ymax i.e. '
                           '16.72 45.74 22.21 48.37 for Hungary',
                      dest='extent', nargs=4)
    parser.add_argument('-t', '--tile',
                      help='Sentinel-2A Tile ID i.e. T34TCT for Budapest',
                      dest='tile')
    parser.add_argument('-d', '--dates',
                      help='Date Interval, if not set it only checks that day',
                      dest='dates', nargs=2,
                      default=(
                          datetime.datetime.now().strftime("%Y-%m-%d"),
                          datetime.datetime.now().strftime("%Y-%m-%d")))
    parser.add_argument('-u', '--username',
                      help='username - SciHub username, if '
                           'not set it goes by guest by default',
                      dest='user', default='guest')
    parser.add_argument('-o', '--odir', help='Output Directory', dest='odir',
                      default=os.getcwd())
    parser.add_argument('-y', '--type',
                      help='Sentinel-1A Product Type i.e. RAW, SLC, GRD',
                      dest='type')
    parser.add_argument('-q', '--quicklook',
                      help='At first download quicklooks to the Output Directory',
                      dest='quick',
                      action='store_true', default=False)
    parser.add_argument('--hun', help='Extent of Hungary', dest='hun',
                      action='store_true', default=False)

    args = parser.parse_args()

    apihub = 'https://scihub.copernicus.eu/apihub/search?rows=10000&q='

    if args.user is 'guest':
        args.password = 'guest'
    if args.user is not 'guest':
        args.password = getpass.getpass()
    if args.hun:
        args.extent = ['16.72', '45.74', '22.21', '48.37']
    if (args.tile is not None) and (
                    args.latlon is not None or args.extent is not None):
        print ' -- You need to switch on the [-t, --tile] option OR the ' \
              '[-l, --latlon] OR [-e, --extent] options to specify your '\
              'Area of Interest'
        print ' -- If you plan to perform downloading by tile you ' \
              'would switch only the [-t, --tile] option.' \
              ' i.e. -t T34TCT for Budapest'
        quit()

    if args.platform is None:
        print ' -- You forget to set the satellite option [-s, --sat]: S1A ' \
              'or S2A'

    if args.tile is not None:
        print " -- Start querying products by tile"
        print " -- Username : ", args.user
        print " -- TileID : ", args.tile
        args.platform = "Sentinel-2"
        platform = 'AND (platformname:%s)' % (args.platform)
        print " -- Platform : ", args.platform
        args.tilelatlon = QueryTileCoords(args.tile)
        if args.tilelatlon:
            footprint = '( footprint:"Intersects(%s)" )' % (
                ",".join(list(args.tilelatlon)))
            print " -- LatLon : ", args.tilelatlon
        date0, date1 = args.dates
        if date0 == date1:
            date1 = (
                datetime.datetime.strptime(date0,
                                           "%Y-%m-%d") + datetime.timedelta(
                    1)).strftime("%Y-%m-%d")
        interval = ' AND beginPosition:[' + date0 + 'T00:00:00.000Z TO ' \
                   + date1 + 'T00:00:00.000Z] AND endPosition:[' \
                   + date0 + 'T00:00:00.000Z TO ' + date1 + 'T00:00:00.000Z]'
        print " -- Date Interval : ", date0, date1
        query = apihub + footprint + interval + platform
        print " -- This is your OPENDATA query:"
        print query
        xml = QueryProducts(args.user, args.password, query)
        meta = list(reversed(ParseProducts(xml)))
        print ' -- Product number : ', len(meta)
        if (args.quick == True) and (len(meta) > 0):
            print " -- Downloading quicklooks ... "
            session = requests.Session()
            session.auth = (args.user, args.password)
            for product in meta:
                ofile = args.odir + os.sep + \
                        os.path.splitext(product['filename'])[0] + ".jpg"
                print "Quicklook : ", ofile
                DownloadFile(args.user, args.password, product['quicklook'],
                             ofile, session.auth)
        if (len(meta) > 0):
            MenuText(meta, args.quick, args.odir)
            while True:
                try:
                    userinput = raw_input('Number(s):')
                    productnumbers = [i.strip() for i in userinput.split(',')]
                    if ('*' in productnumbers) and (len(productnumbers) == 1):
                        print ' -- Downloading all listed products!'
                        productnumbers = [i for i in range(1, len(meta) + 1)]
                        break
                    else:
                        productnumbers = [int(i.strip()) for i in
                                          userinput.split(',')]
                except Exception:
                    print '!!! Your input is not valid !!!'
                    continue
                subsettest = set(productnumbers) <= set(
                    [p + 1 for p in range(0, len(meta))])
                if subsettest == True:
                    break
                if subsettest == False:
                    print '!!! Your input is not valid !!!'
            if (len(productnumbers) > 0):
                try:
                    session = requests.Session()
                    session.auth = (args.user, args.password)
                    for i in productnumbers:
                        rooturl = os.path.split(meta[i - 1]['href'])[
                                      0] + '/Nodes'
                        productdir = MakeRootDir(rooturl, args.odir,
                                                 session.auth)
                        tiledir = productdir + os.sep + args.tile
                        if os.path.exists(tiledir):
                            shutil.rmtree(tiledir)
                        os.mkdir(tiledir)
                        tiledict = PullTile(rooturl, args.tile, session.auth)
                        for band in tiledict:
                            print "Band: ", band
                            oband = tiledir + os.sep + band
                            with open(oband, "wb") as code:
                                r = requests.get(tiledict[band],
                                                 auth=session.auth,
                                                 verify=False)
                                code.write(r.content)
                except Exception as e:
                    print e
    if (args.latlon is not None or args.extent is not None and
                args.platform is not None):
        print " -- Start querying products by latlon or extent"
        if args.latlon:
            footprint = '( footprint:"Intersects(%s)" )' % (
                ",".join(list(args.latlon)))
            print "LatLon : ", ",".join(list(args.latlon))
        if args.extent:
            footprint = '( footprint:"Intersects(POLYGON(({xmin} {ymin}, ' \
                        '{xmax} {ymin}, {xmax} {ymax}, ' \
                        '{xmin} {ymax},{xmin} {ymin})))" )'.format(
                xmin=args.extent[0], ymin=args.extent[1], xmax=args.extent[2],
                ymax=args.extent[3])
            print "Extent : ", list(args.extent)
        if args.platform == "S1A":
            longplat = "Sentinel-1"
            platform = ' AND (platformname:%s)' % (longplat)
        if args.platform == "S2A":
            longplat = "Sentinel-2"
            platform = ' AND (platformname:%s)' % (longplat)
            print "Platform : ", longplat
        if args.type in ['GRD', 'SLC', 'RAW']:
            platform = 'AND (platformname:%s AND producttype:%s)' % (
                longplat, args.type)
        date0, date1 = args.dates
        if date0 == date1:
            date1 = (
                datetime.datetime.strptime(date0,
                                           "%Y-%m-%d") + datetime.timedelta(
                    1)).strftime("%Y-%m-%d")
        interval = ' AND beginPosition:[' + date0 + 'T00:00:00.000Z TO ' +\
                   date1 + 'T00:00:00.000Z] AND endPosition:' \
                           '[' + date0 + 'T00:00:00.000Z TO ' + date1 + \
                   'T00:00:00.000Z]'
        print "Date Interval: ", date0, date1
        query = apihub + footprint + interval + platform
        print query
        xml = QueryProducts(args.user, args.password, query)
        meta = list(reversed(ParseProducts(xml)))
        meta = ParseProducts(xml)
        print 'Product number : ', len(meta)
        if (args.quick == True) and (len(meta) > 0):
            print " -- Downloading quicklooks ... "
            session = requests.Session()
            session.auth = (args.user, args.password)
            for product in meta:
                ofile = args.odir + os.sep + \
                        os.path.splitext(product['filename'])[0] + ".jpg"
                print "Quicklook : ", ofile
                DownloadFile(args.user, args.password, product['quicklook'],
                             ofile, session.auth)
        if (len(meta) > 0):
            MenuText(meta, args.quick, args.odir)
            while True:
                try:
                    userinput = raw_input('Number(s):')
                    productnumbers = [i.strip() for i in userinput.split(',')]
                    if ('*' in productnumbers) and (len(productnumbers) == 1):
                        print ' -- Downloading all listed products!'
                        productnumbers = [i for i in range(1, len(meta) + 1)]
                        break
                    else:
                        productnumbers = [int(i.strip()) for i in
                                          userinput.split(',')]
                except Exception:
                    print '!!! Your input is not valid !!!'
                    continue
                subsettest = set(productnumbers) <= set(
                    [p + 1 for p in range(0, len(meta))])
                if subsettest == True:
                    break
                if subsettest == False:
                    print '!!! Your input is not valid !!!'
            if (len(productnumbers) > 0):
                try:
                    session = requests.Session()
                    session.auth = (args.user, args.password)
                    for i in productnumbers:
                        zf = meta[i - 1]['href']
                        ofile = args.odir + os.sep + \
                                os.path.splitext(meta[i - 1]['filename'])[
                                    0] + ".zip"
                        DownloadFile(args.user, args.password, zf, ofile,
                                     session.auth)
                except Exception as e:
                    print e

if __name__ == '__main__':
    main()
