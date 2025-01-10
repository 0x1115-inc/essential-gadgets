## Install Dependencies
npm install

## Configure Environment Variables
# Create a .env file in the /web directory and add the following variables
NEXT_PUBLIC_BACKEND_API_URL=<your-backend-api-url>

NEXT_PUBLIC_FIREBASE_API_KEY=<your-firebase-api-key>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<your-firebase-auth-domain>
NEXT_PUBLIC_FIREBASE_PROJECT_ID=<your-firebase-project-id>
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=<your-firebase-storage-bucket>
NEXT_PUBLIC_FIREBASE_MESSAGE_SENDER_ID=<your-firebase-messaging-sender-id>
NEXT_PUBLIC_FIREBASE_APP_ID=<your-firebase-app-id>

## Firebase Setup
# Go to your Firebase Console.
# Create or select a project.
# From the left navigation, select Authentication -> Sign-in Method -> Add new provider -> Google
# From the left navigation, select Setting icon -> Project setting -> Add app -> Web app -> You will see your Firebase configuration: apiKey, authDomain, projectId, storageBucket, messagingSenderId, measurementId. 
# Add the project credentials to .env.local as shown above.