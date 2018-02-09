##### Example 2 - `d3`-based chord diagram visualisation of metadata

###### <a name="Description"></a>Description

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

To display the chord diagram, you need to: 
* download the source webpage [example1_icw.html](https://github.com/eurostat/d3ex4es/blob/master/example2/example1_icw.html), as well as the `Javascript` scripts 
[d3.layout.chord.sort.js](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js) and
[d3.layout.chord.sort.js](https://github.com/eurostat/d3ex4es/blob/master/example2/d3.layout.chord.sort.js), _(ii)_
* download the associated `JSON` files (which are actually also `Javascript` scripts...)
[DIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/DIMENSION.json), 
[INDICATOR.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATOR.json) and
[INDICATORxDIMENSION.json](https://github.com/eurostat/d3ex4es/blob/master/example2/INDICATORxDIMENSION.json)

then, you display it locally in your browser.** 

###### <a name="References"></a>References

*  N. Bremer's `d3`-based tutorial on ["How to create a flow diagram with a circular Twist"](https://www.visualcinnamon.com/2015/08/stretched-chord.html).
* [`d3-chord`](https://github.com/d3/d3-chord).
* Eurostat _Experimental Statistics_ [webpage](http://ec.europa.eu/eurostat/web/experimental-statistics/income-consumption-and-wealth) on _Income, Consumption and Wealth_.
