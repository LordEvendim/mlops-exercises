# Size comparision of the Docker images

### Unoptimized

- Python 3.12
- 9.94 GB

### Optimized

- Python 3.12 slim-bookworm
- 9.25GB

Dockerfiles ended up being pretty big. After some investigation it turned out that the main reason behind it is a significant size of the .venv folder.
Here is a layer breakdown from Docker Desktop of the optimized Dockerfile with size of every non-zero individual layer:

| Layer                                                  | Size      |
| ------------------------------------------------------ | --------- |
| debian.sh --arch 'amd64' out/ 'bookworm' '@1759104000' | 74.81 MB  |
| RUN /bin/sh -c set -eux; apt-get update;...            | 9.25 MB   |
| RUN /bin/sh -c set -eux; savedAptMark="...             | 40.22 MB  |
| RUN /bin/sh -c set -eux                                | 36 B      |
| RUN /bin/sh -c apt-get update                          | 294.65 MB |
| COPY /app/.venv /app/.venv                             | 7.04 GB   |
| COPY . .                                               | 1.79 GB   |

We can see the significant difference between unoptimized and optimized images, however they are still pretty big.
