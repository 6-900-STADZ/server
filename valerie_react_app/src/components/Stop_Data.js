import React, {useEffect, useState} from 'react';
import {
  VictoryChart, 
  VictoryAxis, 
  VictoryLine, 
  VictoryTheme, 
  VictoryHistogram, 
  VictoryLabel,
  VictoryZoomContainer
} from 'victory';

import dayjs from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';

import { get, post } from "../utilities.js";
import './Stop_Data.css'
import '../index.css'

const StopData = () => {

    const [init, setInit] = useState(false);
    const [date, setDate] = useState(dayjs().set('hour',8).set('minute',0))
    const [timestamp, setTimestamp] = useState(0)

    const [is_esp_occupancy, set_is_esp_occupancy] = useState(true);

    const [wait_time_data, set_wait_time_data] = useState([])
    const [timestamps, setTimestamps] = useState([])
    const [esp_occupancy, setEsp_occupancy] = useState([])
    const [web_occupancy, setWeb_occupancy] = useState([])
    const [data, setData] = useState([[],[],[]])
    const stopName = 'SW 26 St & SW 127 Av';

    useEffect(() => {
      if (!init){
        setInit(true);
        get_all_data();
        get_wait_time(date);
      } 
      else {
        const intervalId = setInterval(() => {
          get_all_data();
          get_wait_time(date);
        }, 60000);
  
        // Return a function that will clear the interval when the component unmounts
        return () => {
          clearInterval(intervalId);
        };
      }
    });

    const get_all_data = () => {
      try {
        get('http://efpi-17.mit.edu/valerie/all_data').then((response) => {
          const new_data = JSON.parse(JSON.stringify(response));
          console.log(new_data);
          setEsp_occupancy(new_data['esp_occupancy'].map((d) => ({x: new Date(d[0]), y: Number(d[1])})));
          setWeb_occupancy(new_data['web_occupancy'].map((d) => ({x: new Date(d[0]), y: Number(d[1])})));
          setData([
            new_data[is_esp_occupancy ? 'esp_occupancy': 'web_occupancy'].map((d) => ({x: new Date(d[0]), y: Number(d[1])})),
            new_data['t'].map((d) => ({x: new Date(d[0]), y: Number(d[1])})),
            new_data['rh'].map((d) => ({x: new Date(d[0]), y: Number(d[1])}))
          ])
        })
      }
      catch (error) {
          console.log(error);
      }
    }

    const get_wait_time = (newDate) => {
      try {
        get('http://efpi-17.mit.edu/valerie/wait_time', {'date': newDate.format('YYYY-MM-DD')}).then((response) => {
            const data = JSON.parse(JSON.stringify(response));
            console.log(data);
            let wt_data = {}
            for (let dt in data){
              wt_data[dt] = data[dt].map((wt) => ({x: wt}))
            }
            set_wait_time_data(wt_data);
            setTimestamps(Object.keys(wt_data))
        })
      } catch (error) {
        console.log(error);
      }
    }

    const width = 600;
    const height = 400;
    const offset = 50
    const xOffsets = [offset, width/2, width-offset];
    const tickPadding = [0, 0, -15];
    const tickValues = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0];
    const anchors = ["end", "middle", "start"];
    const colors = ["#63B77D", "#DB3931", '#257AFD'];
    const labels = ["Occupancy", "Temperature", "Relative \nHumidity (in %)"]

    // find maxima for normalizing data
    const maxima = data.map(
      (dataset, i) =>i != 0 ? Math.max(...dataset.map((d) => d.y)) : 20
    );

    const valueFormatting = (value) => {
      return timestamps[value]
    }

    const changeDate = (newDate) => {
      setDate(newDate)
      get_wait_time(newDate)
    }

    const changeTimestamp = (event) => {
        let index = Number(event.target.value)
        setTimestamp(timestamps[index]);
    }

    const update_occupancy_line = (new_is_esp_occupancy) => {
      set_is_esp_occupancy(new_is_esp_occupancy);
      setData([new_is_esp_occupancy ? esp_occupancy : web_occupancy, data[1], data[2]])
    }

    return (
        <html>
        <div className='container stop_page'>
        <h1>Recorded Data from {stopName}!</h1>
        <div>
          <h2>Current Weather Conditions</h2>
          <p>Temperature: {data[1].length !=0 ? data[1][0].y: 'Loading'}</p>
          <p>Relative Humidity: {data[2].length !=0 ? data[2][0].y : 'Loading'}</p>
        </div>
        <div id="checkbox_container">
        <FormControlLabel
        label="Occupancy Measured by ESP"
        control={<Checkbox
          checked={is_esp_occupancy}
          onChange={(checked) => (update_occupancy_line(checked))}
          inputProps={{ 'aria-label': 'controlled' }}
          style ={{color: "#63B77D"}}
        />}
        />
        <FormControlLabel
        label="Occupancy Measured Online"
        control={<Checkbox
          checked={!is_esp_occupancy}
          onChange={(checked) => (update_occupancy_line(!checked))}
          inputProps={{ 'aria-label': 'controlled' }}
          style ={{color: "#63B77D"}}
        />}
        />
        </div>
        <div class="graph">
        <VictoryChart 
        width={width} height={height} 
        theme={VictoryTheme.material} 
        scale={{ x: "time" }}
        containerComponent={
          <VictoryZoomContainer
            zoomDimension="x"
          />
        }
        >
          <VictoryLabel x={offset} y={30}
            text={labels[0]}
          />
          <VictoryLabel x={width/2-50} y={30}
            text={labels[1]}
          />
          <VictoryLabel x={width-offset-50} y={30}
            text={labels[2]}
          />
          <VictoryAxis/>
          {data.map((d, i) => (
            <VictoryAxis dependentAxis
              key={i}
              offsetX={xOffsets[i]}
              style={{
                axis: { stroke: colors[i] },
                ticks: { padding: tickPadding[i] },
                tickLabels: { fill: colors[i], textAnchor: anchors[i] }
              }}
              // Use normalized tickValues (0 - 1)
              tickValues={[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]}
              // Re-scale ticks by multiplying by correct maxima
              tickFormat={i !=0 ? (t) => Math.round(t * maxima[i]*10)/10: (t) => t * maxima[i]}
            />
          ))}
          {data.map((d, i) => (
            <VictoryLine
              interpolation={(i != 0) ? "linear" : "step"}
              key={i}
              data={d}
              style={{ data: { stroke: colors[i] } }}
              // normalize data
              y={(datum) => datum.y / maxima[i]}
            />
          ))}
        </VictoryChart>
        </div>
        <div id='avg_wait_time_selector'>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DatePicker
                style='width:fit-content'
                value={date}
                onChange={changeDate}
                />
            </LocalizationProvider>
            <Box sx={{ width: 300 }}><Slider
                defaultValue={0}
                onChange={changeTimestamp}
                marks
                min={0}
                max={timestamps.length-1}
                valueLabelDisplay="auto"
                valueLabelFormat={valueFormatting}
                />
            </Box>
        </div>
        <div class="graph">
        <VictoryChart>
          <VictoryAxis
          label="Waiting Time (in Minutes)"
          style={{ticks:{padding:-5}}}
          tickValues={[0,3,6,9,12,15,18,21]}
          />
          <VictoryAxis dependentAxis
          label="Number of People Waiting"
          style={{ticks:{padding:-5}}}
          tickValues={[0,1,2,3,4,5,6,7,8,9,10]}
          />
          <VictoryHistogram
            style={{
              data: {
                fill: "#63B77D",
              }
            }}
            cornerRadius={5}
            data={wait_time_data[timestamp]}
            bins={[0,3,6,9,12,15,18,21]}
          />
        </VictoryChart>
        </div>
        </div>
        </html>
    );
}

export default StopData;
