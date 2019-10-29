import React from 'react';

export default function SetTaskType(props) {
return (
<>
<h3 className="f3 fw6 mt2 mb3 ttu barlow-condensed blue-dark">Step 2: Choose Task Type</h3>
<ul style={{ listStyle: 'none'}}>
  <li>
    <label>
      <input type="radio" name="form-tasks-type"
      id="square-grid" value="square-grid"/>
      Square Grid
    </label>
  </li>
  <li>
    <label>
      <input
      type="radio" name="form-tasks-type"
      id="arbitrary-tasks" value="arbitrary-tasks"/>
      Arbitrary Tasks
    </label>
  </li>
</ul>
</>
)
}