d3ex4es
=======

Applying `d3.js` framework for handling and exploring (Javascript/Python) Eurostat data and metadata.
---

**About**

This page provides few examples of web-based visualisation of the data and metadata disseminated on [ESTAT website](http://ec.europa.eu/eurostat/data/database). It uses for that purpose some already existing templates based on the `d3.js` library (_e.g._ see gallery referenced [below](#References)). Besides the example webpages, the material used to handle the extracted (meta)data and prepare (select/filter/reshape) them for visualisation is also provided.

**Description**

<table>
<header>
<td align="centre">Example 1</td>
<td align="centre">Example 2</td>
</header>
<tr>
<td><kbd><img src="docs/example1_peps01.png" alt="doc SAS" width="400"> </kbd></td>
<td><kbd><img src="docs/example2_icw.png" alt="doc R" width="400"> </kbd></td>
</tr>
</table>

* Example 1

The visualisation provided in example 1 reuses the **material based on [`d3-force` layout](https://github.com/d3/d3-force)** developed for the _New York Times_ publication on [Obama's budget proposal](http://www.nytimes.com/interactive/2012/02/13/us/politics/2013-budget-proposal-graphic.html), so as to provide with an interactive display of selected social indicator.

 The webpage [_example1_peps01.html_](https://github.com/eurostat/d3ex4es/blob/master/example1/example1_peps01.html) actually illustrates some important (2016) figures related to ESTAT indicator _ilc_peps01_ on *people at risk of poverty or social exclusion* by age and sex (see also the  news release [below](#References)). 
A preview of this webpage is available through `rawgit` at this [address](https://cdn.rawgit.com/eurostat/d3ex4es/01d12b8f/example1/example1_peps01.html)  (though the display is much slower and some of the page features are disabled).

* Example 2

**<a name="References"></a>References**

* `d3.js` [website](https://d3js.org/).
* `d3.js` galleries: [wiki](https://github.com/d3/d3/wiki/Gallery) and [_d3list_](http://christopheviau.com/d3list/gallery.html).
* Eurostat dissemination [website](http://ec.europa.eu/eurostat/data/database).
* Eurostat bulk download [facility](http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing).

