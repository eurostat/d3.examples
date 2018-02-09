##### Example 2 - `d3`-based chord diagram visualisation of metadata

###### <a name="Description"></a>Description

The chord implementation presented here reuses the `d3` material introduced in an online tutorial on flow diagrams, and aims at representing the dependency links (relationship: _"which indicator utilise(s) this dimension? which dimension(s) are concerned by this indicator?_) between some Eurostat indicators and the dimensions that are exploited for the definition of the population breakdowns. 

The webpage [_example2_icw.html_](https://github.com/eurostat/d3ex4es/blob/master/example2/example2_icw.html) shows the dependency between the various Eurostat (experimental) indicators on income, consumption and wealth (ICW) and the different concerned dimensions. See [below](#References) for further useful references.

<table>
<header>
<td align="centre"><i>ICW</i> indicators</td>
<td align="centre"><i>PEPS/PEES</i> indicators</td>
</header>
<tr>
<td><kbd><img src="example2_icw_excerpt1.png" alt="Example 2 ICW excerpt 1" width="400"> </kbd></td>
<td><kbd><img src="example2_icw_excerpt2.png" alt="Example 2 ICW excerpt 2" width="400"> </kbd></td>
</tr>
<header>
<td align="centre">(far too many) <i>ILC</i> indicators</td>
</header>
<tr>
<td><kbd><img src="example2_icw_excerpt3.png" alt="Example 2 ICW excerpt 3" width="400"> </kbd></td>
</tr>
</table>


You can get a preview of this page using `rawgit`: **check this [address](https://cdn.rawgit.com/eurostat/d3ex4es/15d30510/example2/example2_icw_rawgit.html) for direct rendering**.

###### <a name="Usage"></a>Usage

The original material includes: the _index.html_ webpage as well as the `Javascript` source codes [_d3.layout.chord.sort.js_](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js) and
[_d3.layout.chord.sort.js_](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js). The source [_script.js_](https://github.com/eurostat/d3ex4es/blob/master/example2/script.js) has been slightly adapted so as to make the dynamic data loading of _(dimension/indicator)_ data within the _index.html_ page possible.

We also provide two `Python` modules that will enable you to select and prepare the metadata that are used for the visualisation of the data/metadata relationship:
* [`metadata.py`](https://github.com/eurostat/d3ex4es/blob/master/metadata.py) contains the classes/methods that help retrieve, from _Eurostat_ website, the metadata in bulk format;
* [`adjacency_chord.py`](https://github.com/eurostat/d3ex4es/blob/master/adjacency_chord.py) contains the methods that will enable you to select the output indicators to be presented (see the role of the global _INDICATOR_KEEP_ variable in the code) and format the input metadata table to be used for that purpose.

The latter module will generate 3 `JSON` files (which are actually also `Javascript` scripts...), namely:
* [_INDICATOR.json_](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATOR.json) contains the list of indicators selected and whose metadata have been collected for,
* [_DIMENSION.json_](https://github.com/eurostat/d3ex4es/blob/master/example2/DIMENSION.json) contains the list of dimensions used by any of the indicators in the list above, 
* [_INDICATORxDIMENSION.json_](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATORxDIMENSION.json) contains the pseudo adjacency matrix used to represent the relationships between indicators and dimensions.

These files can then be dynamically loaded by the generic _index.html_ webpage. Note that any number of input indicator(s) present in the original _metabase.txt_ file can be selected, though it is recommended to keep this number small (see figure above with all EU-SILC indicators selected for representation).

For the visualisation of the metadata related to ICW indicators, the webpage [_example2_icw.html_](https://github.com/eurostat/d3ex4es/blob/master/example2/example2_icw.html) has been created as a specific copy of the generic _index.html_ webpage. To display the chord diagram locally in your browser, it will be necessary to download: 
* the source webpage _example2_icw.html, 
* the `Javascript` scripts _d3.layout.chord.sort.js_, _d3.layout.chord.sort.js_, and _script.js_, 
* the generated `JSON` files.

###### <a name="References"></a>References

*  N. Bremer's `d3`-based tutorial on ["How to create a flow diagram with a circular Twist"](https://www.visualcinnamon.com/2015/08/stretched-chord.html).
* [`d3-chord`](https://github.com/d3/d3-chord).
* Eurostat _Experimental Statistics_ [webpage](http://ec.europa.eu/eurostat/web/experimental-statistics/income-consumption-and-wealth) on _Income, Consumption and Wealth_.
