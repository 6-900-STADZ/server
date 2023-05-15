import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Occupancy_Form.css';
import '../index.css'

const OccupancyForm = () => {
    const [occupancy, setOccupancy] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = {'occupancy': occupancy};

        try {
            const response = await fetch('http://efpi-17.mit.edu/milo_server/occupancy/WEB', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                navigate('/bus_schedule');
            } else {
                throw new Error('Something went wrong');
            }
        } catch (error) {
        console.log(error);
        }
    };

    return (
        <form class='container' onSubmit={handleSubmit}>
        <p>You can help improve the Miami-Dade Transit System by answering this simple question! :)</p>
        <p>After you submit a short answer, you will also be able to see the estimated bus times!</p>
        <label>
            Occupancy: 
            <input
            type="text"
            value={occupancy}
            onChange={(e) => setOccupancy(e.target.value)}
            />
        </label>
        <button id='submitButton' type="submit">Submit</button>
        </form>
    );
};

export default OccupancyForm;