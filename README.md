# youlearn-project
YouLearn Tech Screen Project

## Explaining the tech stack

### Backend

For backend PDF processing, I have built a PDF Extractor module that the backend endpoint uses to process PDF files. Whenever a PDF URL is sent, I have used PyMuPDF to process each page of the file.
If the page text returns empty, that means that it is image-based and will require OCR, otherwise PyMuPDF extracts all the texts, along with other information like bbox coordinates. Tech stack:

- PyMuPDF (MUCH faster than PDF Miner)
- Google Cloud Vision API for OCR (blazing fast results)
- Fast API 
- Docker contained in 2 gig memory and 2 CPU cores

For bbox highlighting I have achieved it, though not fully. For text-based PDF files, whenever a line on the transcript on the right is highlighted, the corresponding line will highlight on the PDF. But where it falls short is that I could not develop this feature for image-based text PDFs, though my app can render them perfect. Moreover, only single lines highlighted show on the original PDF on the left, if you highlight multiple lines, the PDF highlighter does NOT work. I needed more time for that. Zooming works flawlessly. For highlighting, I am using a mix of bbox coordinates and pdf-search functionality. Moreover, if you select just one word, multiple words on the right-side PDF will be highlighted. As you select a good chunk of unique text, only that text will be highlighted on the right-side PDF.

The `/extract` enpoint will give you text, bbox which is a list of four floats, plus it will also return a bunch of other info that my app uses.

The backend also has a pdf proxy feature available at `/pdf-proxy/` since the front-end react-pdf-viewer cannot get PDFs from sites that have CORS restrictions and would often times show a "Network error: cannot fetch resource" error. So, I built this proxy where instead of the front-end, it's the backend that gets the PDF from the given URL using the requests library and then returns a streaming URL that then gets fed into the front-end `react-pdf-viewer` which then shows the preview of the PDF file.

### Front end

I have used Next.js with a bunch of tailwind CSS to build the front end. I have used react-pdf-viewer and multiple of its components like highlight and search. I have also used react-markdown to display the transcript of the text. I have deployed the frontend on Vercel, though it won't work due to the backend not being deployed (more on this).

## Performance

I have ran the application (backend) multiple times in a docker contained environment that had 2 cpu cores and 2 gigs of memory, and I have done extensive testing of the app and it has always worked fine. Even with the big 1300 pages PDF, the app has performed significantly good (thanks to PyMuPDF, PDFMiner was 10x slower, if not more).

## Flaws

I could not host the backend in time. I have tried a lot and different services but everything got a little bit complicated. Especially since I am using Google's Vision AI, they provide a .JSON file for authentication, so that caused some issues. I later found out that using just API Keys also work, and I have tried to deploy the backend on fly.io, and it still did not work. I will include a link to the fly.io page just in case and maybe keep working to see if I can deploy it.

## Building

I am including all the files you will need. The backend and the front-end as well, along with my .env file (which needs to be placed inside of `backend`). I have hosted the source code on GitHub and so will include a link to that for you to download easily. While you can use the requirements.txt and Pipenv files to re-create the environment, I think Docker will be used. A dockerfile is also included and I will include. You can easily build using the Dockerfile. I will also include the Docker Image file just for your convenience.

To build from dockerfile (from inside the `backend` folder):

```
sudo docker build -t pdf-processor .
```

To run from the provided docker image:

```
sudo docker load -i pdf-processor.tar
```

To run,

```
sudo docker run -p 8000:8000 --env-file .env --network host --cpus="2" --memory="2g" pdf-processor
```

Running the front end:

While being in the `frontend` dir, 

```
npm install
```

To install packages and then do 

```
npm run dev
```

To run the app. Make sure it runs on localhost:3000 and the backend on localhost:8000.

I hope you like my work! (I have skipped homework to complete this project!!)
