import React from 'react';

export default function SetAOI({ draw }) {
return (
<>
<h3 className="f3 fw6 mt2 mb3 ttu barlow-condensed blue-dark">Step 1: Define Area</h3>
<div>
  <h3>Option 1:</h3>
  <p>Draw the Area of Interest on the map</p>
  <button
    className="bg-blue-dark white v-mid dn dib-ns br1 f5 bn ph4-l pv2-l"
    type="button"
    onClick={() => draw.changeMode('draw_polygon')}>Draw
  </button>
</div>

<div>
  <h3>Option 2 (disabled):</h3>
  <p>Import a GeoJSON, KML, OSM or zipped SHP file.</p>
  <button
    className="bg-light-silver white v-mid dn dib-ns br1 f5 bn ph4-l pv2-l"
    type="button"
    onClick={() => console.log("BBBBB")}
    disabled={true}>
    Import
  </button>
</div>
</>
  )
  }