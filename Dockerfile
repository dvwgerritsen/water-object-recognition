FROM python:3.8-slim

COPY ./requirements.txt /requirements.txt
RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir -r /requirements.txt --find-links https://download.pytorch.org/whl/torch_stable.html
WORKDIR /src
COPY ./ /src
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]