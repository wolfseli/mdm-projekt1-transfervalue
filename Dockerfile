# Usage
# docker build -t wolfseli/transfervalue .
# docker run --name transfervalue -e AZURE_STORAGE_CONNECTION_STRING='***' -p 9001:80 -d wolfseli/transfervalue
# docker push wolfseli/transfervalue:latest
# az container create --resource-group mdm-transfervalue --name mdm-transfervalue --image wolfseli/mdm-transfervalue:latest --dns-name-label mdm-transfervalue --ports 80 --environment-variables AZURE_STORAGE_CONNECTION_STRING='***'


FROM python:3.12.1

# Copy Files
WORKDIR /usr/src/app
COPY backend/service.py backend/service.py
COPY frontend frontend

# Install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Docker Run Command
EXPOSE 80
ENV FLASK_APP=/usr/src/app/backend/service.py
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]