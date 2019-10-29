import React, { useLayoutEffect, useState, useCallback } from 'react';
import { fallbackRasterStyle } from '../projects/projectsMap';
import mapboxgl from 'mapbox-gl';
import { MAPBOX_TOKEN } from '../../config';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = MAPBOX_TOKEN;

const ProjectCreationMap = ({draw, map, setMapObj}) => {
  const mapRef = React.createRef();

  useLayoutEffect(() => {
    setMapObj(
      new mapboxgl.Map({
        container: mapRef.current,
        // style: 'mapbox://styles/mapbox/bright-v9',
        style: MAPBOX_TOKEN ? 'mapbox://styles/mapbox/streets-v11' : fallbackRasterStyle,
        zoom: 0,
      }),
    );

    return () => {
      map && map.remove();
    };
  }, []);

  useLayoutEffect(() => {
    const updateArea = () => {
      alert('AAAAA')
    }

    if (map !== null) {
      map.on('load', () => {
        map.addControl(draw);
      });

      map.on('draw.create', updateArea);
    }
  }, [map]);

  return <div id="map" className="fl w-70 vh-75-l" ref={mapRef}></div>;
};

export { ProjectCreationMap }
