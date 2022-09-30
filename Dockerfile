FROM python:3.9-slim

LABEL maintainer="dimdasci <dimds@fastmail.com>"

# Create the user
RUN groupadd --gid 1000 dim \
    && useradd --uid 1000 --gid 1000 -m dim

ENV HOME="/home/dim"
USER dim

WORKDIR "${HOME}/work"
ENV PATH="${HOME}/.local/bin:${PATH}"

COPY requirements.txt ./requirements.txt
COPY src/ src/

RUN pip install --no-cache-dir -r requirements.txt

# ENTRYPOINT [ "ls" ]
# CMD [ "-la" , "src"]
ENTRYPOINT ["python", "src/get_comments.py"]
CMD ["--help"]