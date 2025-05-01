import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [position, setPosition] = useState('');
    const [speed, setSpeed] = useState('');

    const handleClick = () => {
        axios.post('http://localhost:5000/run_function', { position, speed })
            .then(response => console.log(response.data))
            .catch(error => console.error('Error:', error));
    };

    return (
        <div>
            <h1>Nanotec Motor Control</h1>
            <div>
                <label>
                    Target Position Absolute (0.1deg):
                    <input 
                        type="text" 
                        value={position} 
                        onChange={(e) => setPosition(e.target.value)} 
                    />
                </label>
            </div>
            <div>
                <label>
                    Speed (rpm):
                    <input 
                        type="text" 
                        value={speed} 
                        onChange={(e) => setSpeed(e.target.value)} 
                    />
                </label>
            </div>
            <button onClick={handleClick}>Send command</button>
        </div>
    );
}

export default App;
