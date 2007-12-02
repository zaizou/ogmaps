#!/usr/bin/env python

#    OGMaps
#    Copyright (C) 2007 Derek Anderson
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import math, os, re, sys, urllib

RUN_FROM_DIR = os.path.abspath(os.path.dirname(sys.argv[0])) + '/'

from BeautifulSoup import BeautifulSoup
import openanything


def download_if_dne(href, filename):
    if os.path.isfile(filename):
#        print 'already downloaded:', href
        return False
    else:
        try:
            print 'downloading:', href
            oa = openanything.fetch(href)
            if oa['status']==200:
                file = open( filename, 'w' )
                file.write( oa['data'] )
                file.close()
            return True
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
            return False
            
def hide_if_found(o):
    if o:
        o['style'] = 'display:none;'

def get_tile_coords(lat, lng, zl): 
    tile_width = 256
    max_zoom_level = 17
    
    map_size = 2**((max_zoom_level + (math.log(tile_width)/math.log(2)))-zl)
    lng_degrees = abs(-180 - lng)
    lng_ppd = map_size / 360
    lng_ppd_radians = map_size/(2*math.pi)
    e = math.sin(lat*(1/180.*math.pi))
    if e>0.9999: e=0.9999
    if e<-0.9999: e=-0.9999
    
    x = int( lng_degrees * lng_ppd / tile_width )
    y = int( (map_size/2 + 0.5*math.log((1+e)/(1-e)) * (-lng_ppd_radians)) / tile_width )

    return (x, y)

def get_map_data( a, b, zl, max_span=12 ):
#    print a, b, zl
    if a[0]<b[0]: x1=a[0]; x2=b[0]
    else: x1=b[0]; x2=a[0]
    if a[1]<b[1]: y1=a[1]; y2=b[1]
    else: y1=b[1]; y2=a[1]
    if x2-x1 > max_span:
        x1f = (x1+x2)/2-max_span/2; x2f = (x1+x2)/2+max_span/2
    else:
        x1f, x2f = x1, x2
    if y2-y1 > max_span:
        y1f = (y1+y2)/2-max_span/2; y2f = (y1+y2)/2+max_span/2
    else:
        y1f, y2f = y1, y2
#    print 'x1,x2,y1,y2', x1f,x2f,y1f,y2f
    for x in range(x1f,x2f+1):
        for y in range(y1f,y2f+1):
            href = 'http://mt%i.google.com/mt?n=404&v=w2.63&x=%i&y=%i&zoom=%i' % ((x+y)%4,x,y,zl)
            filename = 'mt_n=404&v=w2.63&x=%i&y=%i&zoom=%i' % (x,y,zl)
            download_if_dne( href, os.path.join(RUN_FROM_DIR, 'data', 'tiles', filename) )

def download(location=None):
    
    # init dirs
    for dir in [ 'data', os.path.join('data','tiles') ]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    # download the base page
    if location:
        print 'downloading the following location:', location
        oa = openanything.fetch( 'http://maps.google.com/maps?q='+urllib.quote_plus(location) )
    else:
        print 'downloading the default world map'
        oa = openanything.fetch('http://maps.google.com')
    if oa['status']!=200:
        print 'error connecting to http://maps.google.com - aborting'
        return
    html = oa['data']
    
    # find our lat,lng
    p = re.compile('center:{lat:([0-9.-]+),lng:([0-9.-]+)}')
    m = p.search(html)
    if m:
        lat, lng = float(m.group(1)), float(m.group(2))
    else:
        lat, lng = 37.0625,-95.677068
    print '\tlat, lng =', lat, lng
    
    # find our zoom level
    p = re.compile('span:{lat:([0-9.]+),lng:([0-9.]+)}')
    m = p.search(html)
    if m:
        span_lat, span_lng = float(m.group(1)), float(m.group(2))
    else:
        span_lat, span_lng = 32, 64
#    print 'span_lat, span_lng', span_lat, span_lng
    
    mapfiles = 'http://www.google.com/intl/en_us/mapfiles/94/maps2'

    # perform some base transformations
    html = html.replace('&#160;', '') # beautifulsoup doesn't like this char
    html = html.replace('http://mt0.google.com/mt?', 'data/tiles/mt?')
    html = html.replace('http://mt1.google.com/mt?', 'data/tiles/mt?')
    html = html.replace('http://mt2.google.com/mt?', 'data/tiles/mt?')
    html = html.replace('http://mt3.google.com/mt?', 'data/tiles/mt?')
    html = html.replace('body{margin-top: 3px;margin-bottom: 0;margin-left: 8px;}', 'body{margin:0px;}')
    html = html.replace('#map {left: 20em;margin-left: 8px;margin-right: 20em;', '#map {')
    
    # get our kitchen
    soup = BeautifulSoup(html)
    
    hide_if_found( soup.find('div', attrs={'id':'header'}) )
    hide_if_found( soup.find('div', attrs={'id':'guser'}) )
    hide_if_found( soup.find('div', attrs={'id':'gbar'}) )
    hide_if_found( soup.find('div', attrs={'id':'gbh'}) )
    hide_if_found( soup.find('div', attrs={'id':'hp'}) )
    hide_if_found( soup.find('div', attrs={'id':'panel'}) )
    hide_if_found( soup.find('a', attrs={'id':'paneltoggle'}) )

    # get main.js and transmogrify
    if not os.path.isfile(os.path.join(RUN_FROM_DIR, 'data', 'main.js')):
        print 'downloading:', mapfiles+'/main.js'
        oa = openanything.fetch(mapfiles+'/main.js')
        js = oa['data']
        js = js.replace('function rf(a,b){','function rf(a,b){b = b.replace("tiles/mt?","tiles/mt_");')
        js = js.replace('mb("/maps/gen_204?ev=failed_tile&cad="+f)','mb("data/transparent.png")')
        file = open( os.path.join(RUN_FROM_DIR, 'data', 'main.js'), 'w' )
        file.write( js )
        file.close()
    
    # get mod_cb.js and transmogrify
    if not os.path.isfile(os.path.join(RUN_FROM_DIR, 'data', 'mod_cb.js')):
        print 'downloading:', mapfiles+'/mod_cb.js'
        oa = openanything.fetch(mapfiles+'/mod_cb.js')
        js = oa['data']
        js = js.replace('/mapfiles/cb','data')
        file = open( os.path.join(RUN_FROM_DIR, 'data', 'mod_cb.js'), 'w' )
        file.write( js )
        file.close()
    
    # get mod_traffic_app.js and transmogrify
    if not os.path.isfile(os.path.join(RUN_FROM_DIR, 'data', 'mod_traffic_app.js')):
        print 'downloading:', mapfiles+'/mod_traffic_app.js'
        oa = openanything.fetch(mapfiles+'/mod_traffic_app.js')
        js = oa['data']
        js = js.replace('/maps/tldata','data/tldata')
        file = open( os.path.join(RUN_FROM_DIR, 'data', 'mod_traffic_app.js'), 'w' )
        file.write( js )
        file.close()
    
    # get mod_ms.js and transmogrify
    if not os.path.isfile(os.path.join(RUN_FROM_DIR, 'data', 'mod_ms.js')):
        print 'downloading:', mapfiles+'/mod_ms.js'
        oa = openanything.fetch(mapfiles+'/mod_ms.js')
        js = oa['data']
        js = js.replace('http://maps.google.com','data')
        js = js.replace('/mapfiles','')
        file = open( os.path.join(RUN_FROM_DIR, 'data', 'mod_ms.js'), 'w' )
        file.write( js )
        file.close()
    
    # get other scripts
    scripts = [ 'mod_mymaps.js', 'mod_mpl_host.js', 'mod_kml.js', 'mod_le.js', ]
    for s in scripts:
        download_if_dne( mapfiles+'/'+s, os.path.join(RUN_FROM_DIR, 'data', s) )
    
    # get linked scripts
    for tag in soup.findAll('link'):
        try:
            href = tag['href']
            filename = href.split('/')[-1]
            download_if_dne( href, os.path.join(RUN_FROM_DIR, 'data', filename) )
            tag['href'] = 'data/'+filename
        except:
            print 'error:', tag

    # get all static images
    for tag in soup.findAll('img'):
        try:
            src = tag['src']
            filename = src.split('/')[-1]
            download_if_dne( src, os.path.join(RUN_FROM_DIR, 'data', filename) )
            tag['src'] = 'data/'+filename
        except:
            # print 'error:', tag
            pass
    
    # get other misc files
    download_if_dne( 'http://www.google.com/mapfiles/cb/bounds_cippppt.txt', os.path.join(RUN_FROM_DIR, 'data', 'bounds_cippppt.txt') )
    download_if_dne( 'http://maps.google.com/maps/tldata?tldtype=1&hl=en&country=us&callback=_xdc_._1f9onnphn', os.path.join(RUN_FROM_DIR, 'data', 'tldata') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/arrow-white.png', os.path.join(RUN_FROM_DIR, 'data', 'arrow-white.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/arrow.png', os.path.join(RUN_FROM_DIR, 'data', 'arrow.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/lmc.png', os.path.join(RUN_FROM_DIR, 'data', 'lmc.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/lmc-bottom.png', os.path.join(RUN_FROM_DIR, 'data', 'lmc-bottom.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/slider.png', os.path.join(RUN_FROM_DIR, 'data', 'slider.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/scale.png', os.path.join(RUN_FROM_DIR, 'data', 'scale.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/arrowtransparent.png', os.path.join(RUN_FROM_DIR, 'data', 'arrowtransparent.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/overcontract.gif', os.path.join(RUN_FROM_DIR, 'data', 'overcontract.gif') )
    download_if_dne( 'http://maps.google.com/mapfiles/etna.jpg', os.path.join(RUN_FROM_DIR, 'data', 'etna.jpg') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/drag_cross_67_16.png', os.path.join(RUN_FROM_DIR, 'data', 'drag_cross_67_16.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iws2.png', os.path.join(RUN_FROM_DIR, 'data', 'iws2.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iw2.png', os.path.join(RUN_FROM_DIR, 'data', 'iw2.png') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iw_close.gif', os.path.join(RUN_FROM_DIR, 'data', 'iw_close.gif') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iw_plus.gif', os.path.join(RUN_FROM_DIR, 'data', 'iw_plus.gif') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iw_fullscreen.gif', os.path.join(RUN_FROM_DIR, 'data', 'iw_fullscreen.gif') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/iw_minus.gif', os.path.join(RUN_FROM_DIR, 'data', 'iw_minus.gif') )
    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/transparent.gif', os.path.join(RUN_FROM_DIR, 'data', 'transparent.gif') )
#    download_if_dne( 'http://www.google.com/intl/en_us/mapfiles/', os.path.join(RUN_FROM_DIR, 'data', '') )
    
            
    # some post transformations, then write to disk
    html = soup.prettify()
    html = html.replace(mapfiles, 'data')
    html = html.replace('http://www.google.com/intl/en_us/mapfiles', 'data')
    file = open( os.path.join(RUN_FROM_DIR, 'ogmaps.html'), 'w')
    file.write( html )
    file.close()
    #print html

    # get map data
    for zl in range(17,-3,-1):
        get_map_data( get_tile_coords( lat-span_lat, lng-span_lng, zl ), get_tile_coords( lat+span_lat, lng+span_lng, zl ), zl )
    




if __name__ == "__main__":
    if len(sys.argv)>1:
        for addr in sys.argv[1:]:
            download(addr)
    else:
        download()
