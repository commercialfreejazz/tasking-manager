import React, { useState, useLayoutEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { Redirect } from '@reach/router';
import { useQueryParam, NumberParam } from 'use-query-params';
import { FormattedMessage, FormattedNumber } from 'react-intl';

import messages from './messages';
import SetAOI from './setAOI';
import { ProjectCreationMap } from './projectCreationMap';
import SetTaskSizes from './setTaskSizes';
import TrimProject from './trimProject';
import NavButtons from './navButtons';
import Review from './review';
import { fetchLocalJSONAPI } from '../../network/genericJSONRequest';
import { MAP_MAX_AREA } from '../../config';

import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';

const MapboxDraw = require('@mapbox/mapbox-gl-draw');

export const paintOptions = {
  'fill-color': '#00004d',
  'fill-opacity': 0.3,
};

const ProjectCreate = props => {
  const token = useSelector(state => state.auth.get('token'));
  // eslint-disable-next-line
  const [cloneFromId, setCloneFromId] = useQueryParam('cloneFrom', NumberParam);
  const [step, setStep] = useState(1);
  const [cloneProjectName, setCloneProjectName] = useState(null);

  const fetchCloneProjectInfo = useCallback(
    async cloneFromId => {
      const res = await fetchLocalJSONAPI(`projects/${cloneFromId}/`);
      setCloneProjectName(res.projectInfo.name);
    },
    [setCloneProjectName],
  );

  useLayoutEffect(() => {
    if (cloneFromId && !isNaN(Number(cloneFromId))) {
      fetchCloneProjectInfo(cloneFromId);
    }
  }, [cloneFromId, fetchCloneProjectInfo]);

  let cloneProjectData = {
    id: cloneFromId,
    name: cloneProjectName,
  };

  // Project information.
  const [metadata, updateMetadata] = useState({
    geom: null,
    area: 0,
    tasksNo: 0,
    taskGrid: null,
    projectName: '',
    zoomLevel: 9,
    tempTaskGrid: null,
    arbitraryTasks: false,
  });

  const drawOptions = {
    displayControlsDefault: false,
    styles: [
      {
        id: 'gl-draw-polygon-fill-inactive',
        type: 'fill',
        paint: paintOptions,
      },
    ],
  };
  const [mapObj, setMapObj] = useState({
    map: null,
    draw: new MapboxDraw(drawOptions),
  });

  if (!token) {
    return <Redirect to={'login'} noThrow />;
  }

  const renderCurrentStep = () => {
    switch (step) {
      case 1:
        return <SetAOI mapObj={mapObj} metadata={metadata} updateMetadata={updateMetadata} />;
      case 2:
        return <SetTaskSizes mapObj={mapObj} metadata={metadata} updateMetadata={updateMetadata} />;
      case 3:
        return <TrimProject mapObj={mapObj} metadata={metadata} updateMetadata={updateMetadata} />;
      case 4:
        return (
          <Review
            metadata={metadata}
            updateMetadata={updateMetadata}
            token={token}
            cloneProjectData={cloneProjectData}
          />
        );
      default:
        return;
    }
  };

  return (
    <div className="cf bg-tan vh-minus-122-ns h-100 pl4-l pr0-l ph2">
      <div className="fl pt3 w-30-l cf w-100">
        <h2 className="f2 fw6 mt2 mb3 ttu barlow-condensed blue-dark">
          <FormattedMessage {...messages.createProject} />
        </h2>
        {cloneFromId &&
          <p className="fw6 pv2 blue-grey">
            <FormattedMessage {...messages.cloneProject} values={{id: cloneFromId, name: cloneProjectName}}/>
          </p>
        }
        {renderCurrentStep()}
        <NavButtons
          index={step}
          setStep={setStep}
          metadata={metadata}
          mapObj={mapObj}
          updateMetadata={updateMetadata}
          maxArea={MAP_MAX_AREA}
        />
      </div>
      <div className="w-70-l w-100 h-100-l h-50 pt3 pt0-l fr relative">
        <ProjectCreationMap
          metadata={metadata}
          updateMetadata={updateMetadata}
          mapObj={mapObj}
          setMapObj={setMapObj}
        />
        <div className="cf left-1 bottom-2 absolute">
          <p
            className={`fl mr2 pa1 f7-ns white ${
              metadata.area > MAP_MAX_AREA || metadata.area === 0 ? 'bg-red' : 'bg-green'
            }`}
          >
            <FormattedMessage
              {...messages.areaSize}
              values={{
                area: <FormattedNumber value={metadata.area} unit="kilometer" />,
                sq: <sup>2</sup>,
              }}
            />
          </p>
          <p className="fl bg-blue-light white mr2 pa1 f7-ns">
            <FormattedMessage
              {...messages.taskNumber}
              values={{ n: <FormattedNumber value={metadata.tasksNo} /> }}
            />
          </p>
        </div>
      </div>
    </div>
  );
};

export { ProjectCreate };