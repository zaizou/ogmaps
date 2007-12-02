==About==
I ordered a [http://en.wikipedia.org/wiki/Nokia_N800 Nokia N800] a day or two ago, and thought "man, wouldn't it be nice to be able to use Google Maps around town even when this thing doesn't have an internet connection?"  Well, a few hours and ~200 lines of code later: the answer is definitely "heck yeah".  =P

This tool downloads and builds a version of [http://maps.google.com/ Google Maps] that will run completely off your own system, with no internet connection, HTTP servers, etc. required.  If your device has a web browser and a python interpreter, you're pretty much good to go.

==Downloading==
Assuming you have SVN installed, run the following command:
{{{
$ svn checkout http://ogmaps.googlecode.com/svn/trunk/ ogmaps
}}}
This will create a directory `ogmaps` and download all the relevant files.

==Instructions==
 # Change to the directory created above.
 # run: `python ogmaps.py "plano, tx"` (replace "plano, tx" with wherever) *while* your internet connection is working
 # open the file "ogmap.html" in your web browser (later, when your internet connection is down)

==FAQ==

===How does this work?===
The script downloads all the HTML, Javascript and images Google Maps uses, and saves them to your hard drive.  It then, through the magic of regular expressions and [http://www.crummy.com/software/BeautifulSoup/ BeautifulSoup], transmographies the files as necessary to use the data it downloaded a moment earlier.

===How much drive space does this use?===
That depends on how many locations you download, but it should be less than 10MB per site.  It's smart enough to know what it has and hasn't downloaded already, and not re-request the same information.  It downloads data for all zoom levels, but to avoid exponential growth only looks at a fixed pixel radius (~3072px / 12 tiles) around whatever point you're looking at.

===Isn't this illegal / against Google's TOC / stealing?===
I doubt it.  Just don't use the images for anything other than personal use and you should be fine.  But if this project disappears suddenly, check out my blog at [http://kered.org/blog] for where I'll re-host it.

===Will this work on my N770/N800/N810?===
Heck if I know.  I'm still waiting for the FedEx guy!

===How can I help?===
To help the project, file a bug for any errors or feature requests you have, and/or join the list.  To help me personally, check out my company's site: [http://allurstuff.com] (it's basically craigslist fused with google maps).
