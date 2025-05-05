import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [position, setPosition] = useState('');
    const [speed, setSpeed] = useState('');
    const [status, setStatus] = useState('idle');

    const handleMove = () => {
        axios.post('http://localhost:5000/run_positioning_movement', { position, speed })
            .then(() => setStatus("moving"))
            .catch(() => setStatus("error"));
    };

    const handleStop = () => {
        axios.post('http://localhost:5000/quickstop')
            .then(() => setStatus("stopped"))
            .catch(() => setStatus("error"));
    }

    // Poll every second
    useEffect(() => {
        const interval = setInterval(() => {
            axios.get('http://localhost:5000/motor_status')
                .then(res => setStatus(res.data.status))
                .catch(() => setStatus("error"));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <h1>Nanotec Motor Control</h1>
            <p><strong>Status:</strong> {status}</p>
            <label>
                Target Position (*0.1deg):
                <input value={position} onChange={e => setPosition(e.target.value)} />
            </label>
            <br />
            <label>
                Speed (rpm): 
                <input value={speed} onChange={e => setSpeed(e.target.value)} />
            </label>
            <br />
            <button onClick={handleMove}>Start Move</button>
            <button onClick={handleStop} 
            style={{ backgroundColor: 'red', color: 'white' }}> Emergency Stop</button>
        </div>
    );
}
export default App;