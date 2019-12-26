# YandexMusicWebParser

## About
Flask web-application for scraping data from the [Yandex.Music](https://music.yandex.ru) site. <br>
With this app you can browse your music library in a convenient tabular format with ordering and filtering support. <br>
The lite version of this project is available on the [YandexMusicParser](https://github.com/ElFanzo/YandexMusicParser) page.

## Installation
- Clone the repo: <br>
  `git clone https://github.com/ElFanzo/YandexMusicWebParser.git`;
- Install Python >=3.7;
- Install pip;
- Install dependencies: <br>
  `pip install -r requirements.txt`

## Usage
- Go to the yandex_music folder: <br>
  `cd yandex_music`
- Create the database: <br>
  `flask db upgrade`
- Run flask application: <br>
  `flask run`
- Go to the [localhost:5000/](http://127.0.0.1:5000/)
