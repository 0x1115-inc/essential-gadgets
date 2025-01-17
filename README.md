# Essential Gadgets
The Essential Gadgets is a collection of useful tools and services that can be used to simplify the daily tasks.

## Development guidelines
### Project structure
`/api`: OpenAPI/Swagger specs, JSON schema files, protocol definition files.  
`/applications/{app-name}`: The directory contains the source code of the application. Each application should be an instance of [Flask](http://flask.palletsprojects.com/en/stable/tutorial/layout/) and placed in a separate directory.  
`/docs`: The directory contains the documentation of the project.  
`/internal`: The directory contains the shared libraries. In some cases, the shared libraries can be used by multiple applications.  
`/web`: The directory contains the web interface source code of the project. It can be known as the frontend of the project.  
`/websites`: The directory of public deployment website. Commonly, the built code from `/web` will be copied to each nest folders in this directory. Each folder is a separate website and have different git repository.  

## Deployment

### Build the Docker
```bash
# Build the infrastructure
docker build -t 0x1115/egb .

# Build the application
cd applications/shorten_url
docker build -t 0x1115/shorten-url:latest -t 0x1115/shorten-url:[version-tag] .
```

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