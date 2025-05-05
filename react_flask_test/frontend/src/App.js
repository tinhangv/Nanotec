import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [position, setPosition] = useState('');
    const [speed, setSpeed] = useState('');
    const [status, setStatus] = useState('idle');

    const handleAbsMove = () => {
        axios.post('http://localhost:5000/run_abs_movement', { position, speed })
            .then(() => setStatus("moving"))
            .catch(() => setStatus("error"));
    };

    const handleRelMove = () => {   
        axios.post('http://localhost:5000/run_rel_movement', { position, speed })
            .then(() => setStatus("moving"))
            .catch(() => setStatus("error"));
    }

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
                Target Position (*0.1deg) [-2,147,483,648 to 2,147,483,647]:
                <input value={position} onChange={e => setPosition(e.target.value)} />
            </label>
            <br />
            <label>
                Speed (rpm): 
                <input value={speed} onChange={e => setSpeed(e.target.value)} />
            </label>
            <br />
            <button onClick={handleAbsMove}>Move Absolute</button>
            <button onClick={handleRelMove}>Move Relative</button>
            <button onClick={handleStop} 
            style={{ backgroundColor: 'red', color: 'white' }}> Emergency Stop</button>
        </div>
    );
}
export default App;