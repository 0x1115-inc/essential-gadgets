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