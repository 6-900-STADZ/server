import React, {useEffect, useState} from 'react';
import BusRoute from "./Bus_Route.js"
import { get, post } from "../utilities.js";

import '../index.css';

const BusSchedule = () => {

  const [init, setInit] = useState(false);
  const [busSchedule, setBusSchedule] = useState([]);
  const stopName = 'SW 26 St & SW 127 Av';

  useEffect(() => {
    const stopId = 4097;

    if (!init){
      setInit(true);
      get_bus_schedule(stopId);
    } 
    else{
      // Update bus schedule every tenth of a minute 
      const intervalId = setInterval(() => {
        get_bus_schedule(stopId);
      }, 6000);

      // Return a function that will clear the interval when the component unmounts
      return () => {
        clearInterval(intervalId);
      };
    }
  });

  const get_bus_schedule = (stopId) => {
    try {
      get('http://efpi-17.mit.edu/valerie/bus_info', {'stop':stopId}).then((response) => {
        const data = JSON.parse(JSON.stringify(response));
      
        let routePredictions = []
        for (const r of data['data']['predictionsData']){
          routePredictions.push([r['routeName'],r['destinations'][0]['predictions'].map((eta) => eta['min'])])
        }
        setBusSchedule(routePredictions);
      })
    }
    catch (error) {
      console.log(error);
    }
  }

  return (
    <div class='container'>
      <h1>Bus Schedule for {stopName}!</h1>
      {busSchedule.map((route) => (
        <BusRoute
        routeName={route[0]}
        etas={route[1]}
        />
      )
      )}
    </div>
  );
}

export default BusSchedule;
