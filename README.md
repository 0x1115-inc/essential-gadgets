# Essential Gadgets

## Development guidelines

### Build the Docker
```bash
# Build the infrastructure
docker build -t 0x1115/egb .

# Build the application
cd applications/shorten_url
docker build -t 0x1115/shorten-url:latest -t 0x1115/shorten-url:[version-tag] .
```

## Deployment
### Deploy to the Google Cloud Run
```bash
# Deploy the application
gcloud run deploy shorten-url \
--image=0x1115/shorten-url:latest \
--port=8080 \
--region=asia-southeast1 \
--service-account=$SHORTERN_URL_SA \
--allow-unauthenticated \
--no-cpu-boost \
--set-env-vars=APP_HOSTNAME=$APP_HOSTNAME,DB_PROVIDER=$DB_PROVIDER,DB_FIRESTORE_PROJECT_ID=$DB_FIRESTORE_PROJECT_ID,DB_FIRESTORE_DATABASE_NAME=$DB_FIRESTORE_DATABASE_NAME \
```