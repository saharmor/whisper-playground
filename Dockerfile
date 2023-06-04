FROM python:3.8.16-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg
RUN apt-get install -y portaudio19-dev
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN npm install yarn -g
RUN npm install pm2 -g

COPY . .

WORKDIR /app/interface
RUN yarn install

WORKDIR ../backend
RUN pip install wheel 
RUN pip install -r requirements.txt

WORKDIR /app

CMD /bin/bash -c "cd backend && pm2 start 'flask --app app run --port 8000' --name=backend && cd ../interface && pm2-runtime start 'yarn start' --name=interface"