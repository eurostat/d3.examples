##### Example 2 - `d3`-based chord diagram visualisation of metadata

###### <a name="Description"></a>Description

The chord implementation presented here reuses the `d3` material introduced in an online tutorial on flow diagrams, and aims at representing the dependency links (relationship: _"which indicator use(s) this dimension? which dimension(s) are used by this indicator?_) between Eurostat indicators and dimensions that are actually used for the definition of the population breakdowns.

The webpage [_example2_icw.html_](https://github.com/eurostat/d3ex4es/blob/master/example2/example2_icw.html) shows the dependency between the various Eurostat (experimental) indicators on income, consumption and wealth (ICW) and the different concerned dimensions. See [below](#References) for further useful references.

<table>
<header>
<td align="centre"><i>ICW indicators</i></td>
<td align="centre"><i>PEPS/PEES indicators</code></td>
</header>
<tr>
<td><kbd><img src="example2_icw_excerpt1.png" alt="Example 2 ICW excerpt 1" width="400"> </kbd></td>
<td><kbd><img src="example2_icw_excerpt2.png" alt="Example 2 ICW excerpt 2" width="400"> </kbd></td>
</tr>
<header>
<td align="centre"><i>(far too many) ILC indicators</i></td>
</header>
<tr>
<td><kbd><img src="example2_icw_excerpt3.png" alt="Example 2 ICW excerpt 3" width="400"> </kbd></td>
</tr>
</table>

You can get a preview of this page using `rawgit`: **check this [address](https://cdn.rawgit.com/eurostat/d3ex4es/30d73f3b/example2/example2_icw_ragwit.html) for direct rendering**.

###### <a name="Usage"></a>Usage

We provide hereby two `Python` modules that will enable you to select and prepare the metadata that are used for the visualisation of the data/metadata relationship:
* [`metadata.py`](https://github.com/eurostat/d3ex4es/blob/master/metadata.py) contains the classes/methods that help retrieve,  from ESTAT website, the metadata in bulk format;
* [`adjacency_chord.py`](https://github.com/eurostat/d3ex4es/blob/master/adjacency_chord.py) contains the methods that will enable you to select the output indicators to be presented and format the input metadata table to be used for that purpose.

The latter module will generate 3 `JSON` files (which are actually also `Javascript` scripts...), namely:
[DIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/DIMENSION.json), 
[INDICATOR.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATOR.json) and
[INDICATORxDIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATORxDIMENSION.json) which can then dynamically loaded by the _index.html_ webpage.

To display the chord diagram on ICW, it is necessary to: 
* download the source webpage [example2_icw.html](https://github.com/eurostat/d3ex4es/blob/master/example2/example2_icw.html), as well as the `Javascript` scripts 
[d3.layout.chord.sort.js](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js) and
[d3.layout.chord.sort.js](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js), 
* download the associated `JSON` files (which are actually also `Javascript` scripts...)
[DIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/DIMENSION.json), 
[INDICATOR.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATOR.json) and
[INDICATORxDIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATORxDIMENSION.json)

then, it is possible to display it locally in your browser.

###### <a name="References"></a>References

*  N. Bremer's `d3`-based tutorial on ["How to create a flow diagram with a circular Twist"](https://www.visualcinnamon.com/2015/08/stretched-chord.html).
* [`d3-chord`](https://github.com/d3/d3-chord).
* Eurostat _Experimental Statistics_ [webpage](http://ec.europa.eu/eurostat/web/experimental-statistics/income-consumption-and-wealth) on _Income, Consumption and Wealth_.
