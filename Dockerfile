FROM python:3.11

# Set home directory to root & home directory to root
ENV HOME /root
WORKDIR /
# ENV HOME /home
# WORKDIR /home/pengwin/buffalo-cs/cse312-web-apps/WebAppProject

# copy all files onto the image
COPY . .

# install dependencies
RUN pip3 install -r requirements.txt

EXPOSE 8080

COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait

# do not use RUN to run your app
# -u  lets you see the output, even if you're using docker
CMD /wait && python3 -u server.py
