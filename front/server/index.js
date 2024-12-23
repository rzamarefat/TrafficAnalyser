const amqp = require('amqplib');
const WebSocket = require('ws');

const QUEUE_NAME = 'traffic-producer'; // Match the Python producer's queue name

async function startServer() {
    try {
        // Connect to RabbitMQ
        const connection = await amqp.connect('amqp://localhost');
        const channel = await connection.createChannel();
        await channel.assertQueue(QUEUE_NAME, { durable: false });

        console.log(`Connected to RabbitMQ queue: ${QUEUE_NAME}`);

        // Set up WebSocket server
        const wss = new WebSocket.Server({ port: 8080 });

        wss.on('connection', (ws) => {
            console.log('Client connected via WebSocket');

            channel.consume(
                QUEUE_NAME,
                (msg) => {
                    if (msg !== null) {
                        try {
                            const message = JSON.parse(msg.content.toString());
                            ws.send(JSON.stringify(message)); // Send JSON message to clients
                            channel.ack(msg);
                        } catch (error) {
                            console.error('Error processing message:', error);
                            channel.nack(msg, false, false); // Reject message
                        }
                    }
                },
                { noAck: false } // Explicit acknowledgment for processed messages
            );
        });

        console.log('WebSocket server running on ws://localhost:8080');
    } catch (error) {
        console.error('Error starting server:', error);
    }
}

startServer();
