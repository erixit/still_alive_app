Build and run the app in Docker

Prerequisites: Docker installed on your machine.

Build the image (run from project root):

```bash
docker build -t still_alive_app:latest .
```

Run the container (bind port 8501):

```bash
docker run --rm -p 8501:8501 \
  -v "$PWD":/app \
  -v "$PWD"/still_alive.db:/app/still_alive.db \
  still_alive_app:latest
```

Notes:
- The image includes Node.js (for building a frontend if you add one) and Python/Streamlit.
- If you add a `frontend` folder with `package.json`, the Dockerfile will attempt to `npm ci` and `npm run build` during image build.
- If `pip install -r requirements.txt` fails due to platform-specific binary deps, build on a machine with matching architecture or adjust the image to include needed OS packages.
