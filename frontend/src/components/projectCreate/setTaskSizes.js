import React from 'react';

export default function SetTaskSizes(props) {
return (
<>
<h3 className="f3 fw6 mt2 mb3 ttu barlow-condensed blue-dark">Step 3: Set tasks sizes</h3>
<div>
    <div>
        <p>General task size:</p>
        <div role="group">
            <button type="button">
				Larger
            </button>
            <button>
            	Smaller
            </button>
        </div>
    </div>
    <div>
        <p>Split a specific area into smaller tasks by drawing an area or point:</p>
        <div role="group">
            <button type="button">
                    Split (polygon)
            </button>
            <button type="button">
                    Split (point)
            </button>
            <button type="button">
                    Reset
            </button>
        </div>
    </div>
    <p>A new project will be created with n tasks.</p>
    <p>The size of each task is approximately is over 9000 km<sup>2</sup>.</p>
</div>
</>
)
}