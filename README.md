# Essential Gadgets
The Essential Gadgets is a collection of useful tools and services that can be used to simplify the daily tasks.

## Development guidelines
### Project layout
This project is following and extend the [Standard Go Project Layout](https://github.com/golang-standards/project-layout).

`/api`: OpenAPI/Swagger specs, JSON schema files, protocol definition files.  
`/applications/{app-name}`: The directory contains the source code of the application. Each application should be an instance of [Flask](http://flask.palletsprojects.com/en/stable/tutorial/layout/) and placed in a separate directory.  
`/build`: The directory contains the build scripts and configuration files.  
`/docs`: The directory contains the documentation of the project.  
`/internal`: The directory contains the shared libraries. In some cases, the shared libraries can be used by multiple applications.  
`/scripts`: The directory contains the scripts to perform various tasks.  
`/web`: The directory contains the web interface source code of the project. It can be known as the frontend of the project.  
`/websites`: The directory of public deployment website. Commonly, the built code from `/web` will be copied to each nest folders in this directory. Each folder is a separate website and have different git repository.  

### Start the development environment
```bash
# Navigate to the project root directory
docker compose -f compose.dev.yml up
```

After run the command, the development environment will be started. The backend application will be available at `http://localhost:8080`. It is automatically reloaded when the source code is changed.

## Deployment

### Build Docker images
```bash
# Navigate to the project root directory

# Build the base image
/bin/bash scripts/egb/1_docker-image-build.sh

# Build the application
# Specify the application name
APP_NAME=shorten-url 

/bin/bash scripts/app/${APP_NAME}/1_docker-image-build.sh
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

### Deploy GUI website 
1. Follow the [Firebase Setup](web/README.md#Firebase-Setup) to create Firebase App
2. Create a folder same as the hostname that you want to serve the website in `/websites` folder. For example, you decide use `shorten.example.com`, you should create folder `websites/shorten.example.com`. 
3. Run command `bash scripts/2_web_build.sh`. The built assets will copy to all folder in `/websites` automatically. It is ready to deploy to any host that serve the static frontend (Github Page, Cloudflare Page).
