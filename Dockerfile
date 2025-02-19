FROM python:3

WORKDIR /src
COPY requirements.txt /src/requirements.txt
COPY entrypoint.sh /src/entrypoint.sh
RUN chmod +x /src/entrypoint.sh
RUN pip install --no-cache-dir -r /src/requirements.txt

WORKDIR /workspace
COPY . /workspace
ENTRYPOINT [ "/src/entrypoint.sh" ]