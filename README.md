# TaskTrackerAPI

TaskTrackerAPI is a powerful API for mobile to-do applications. The application allows you to manage your tasks using cards with a counter,
The app also features real-time chat using WebSockets and seamless integration with Firebase Cloud Messaging (notifications) to keep users engaged and informed.

## Features

- Keep track of your to-dos with cards.
- Communication with other users in real time.
- User-friendly interface.
- Receiving notifications about received messages.

## Getting Started

Follow these steps to set up and run the bot locally:

1. Clone this repository to your machine.
2. Install the necessary dependencies by running `pip install -r requirements.txt`.
3. Set environment variable MONGODB_URI with the URI of your MongoDB database.
4. Get credential file (key.json) from Firebase Cloud Messaging.
5. Put it in the "credentials" folder.
6. Run the application using `uvicorn main:app --reload`.
