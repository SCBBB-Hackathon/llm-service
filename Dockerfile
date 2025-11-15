FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel

RUN mkdir -p /main
WORKDIR /main
COPY . /main

RUN pip install -r requirements.txt


EXPOSE 1542
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "1542"]