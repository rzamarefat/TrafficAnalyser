import React, { useEffect, useState } from 'react';

const PageA = () => {
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
        <div>
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
    );
};

export default PageA;
