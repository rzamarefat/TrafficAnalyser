import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';

const StreamPage = () => {
    const [imageData, setImageData] = useState(null);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8080');

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setImageData(data); // Update state with the received image and metadata
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className='row'>
            <Navbar/>
            <div className='col-sm-8 px-5 my-5'>
                <h1>Live Stream</h1>
                {imageData ? (
                    <div>
                        <img
                            src={`data:image/jpeg;base64,${imageData.img}`}
                            alt="Received frame"
                            style={{ width: '100%', height: 'auto', border: '1px solid black' }}
                        />
                        <p>Metadata: {imageData.metadata}</p>
                    </div>
                ) : (
                    <p>Waiting for images...</p>
                )}
            </div>
            {/* <div className='col-sm-4 bg-danger'>

            </div> */}
        </div>
    );
};

export default StreamPage;
