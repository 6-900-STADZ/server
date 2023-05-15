import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OccupancyForm from './components/Occupancy_Form';
import BusSchedule from './components/Bus_Schedule';
import StopData from './components/Stop_Data';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route exact path="/bus_schedule" element={<BusSchedule/>} />
        <Route exact path="/stop_data" element={<StopData/>} />
        <Route exact path="/" element={<OccupancyForm/>} />
      </Routes>
    </Router>
  );
};

export default App;
