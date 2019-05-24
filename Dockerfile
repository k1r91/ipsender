FROM python

MAINTAINER k1r911 <cherkasov.kirill@gmail.com>

WORKDIR /usr/scr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./ipsender.py"]
