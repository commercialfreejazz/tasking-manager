import React, { useState } from 'react';
import SetAOI from './setAOI';
import { ProjectCreationMap } from './projectCreationMap'
import SetTaskType from './setTaskType'
import SetTaskSizes from './setTaskSizes'

import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'

var MapboxDraw = require('@mapbox/mapbox-gl-draw');


const Buttons = props => {
  const values ="mt2 f5 ph4-l pv2-l white bg-blue-dark"
  return (
    <div>
      <button
        onClick={() => props.setStep(props.index + 1)}
        className={values} >Next
      </button>
      {
        props.index === 1 ? null :
        (
          <button
            onClick={() => props.setStep(props.index - 1)}
            className={values}>
            Back to previous
          </button>
        )
      }
    </div>
  )
}

const ProjectCreate = () => {
  const [step, setStep] = useState(1)
  const [draw, setDraw] = useState(new MapboxDraw())
  const [map, setMapObj] = useState(null)
  const renderCurrentStep = () => {
  	switch(step) {
  		case 1:
  			return <SetAOI
  				draw={draw}
  			/>
  		case 2:
  			return <SetTaskType />
      case 3:
        return <SetTaskSizes map={map}/>
  	}
  }

  return (
    <div className="cf pv3 ph4">
      <h2 className="f2 fw6 mt2 mb3 ttu barlow-condensed blue-dark">Create project</h2>
      <div className="fl w-30">
        {renderCurrentStep()}
      </div>
      <ProjectCreationMap
        map={map}
        setMapObj={setMapObj}
        draw={draw}/>
      <Buttons index={step} setStep={setStep}/>
    </div>
	);
}

export { ProjectCreate };