# AniworlDL
```
  ___        _                    _______ _     
 / _ \      (_)                  | |  _  \ |    
/ /_\ \_ __  ___      _____  _ __| | | | | |    
|  _  | '_ \| \ \ /\ / / _ \| '__| | | | | |    
| | | | | | | |\ V  V / (_) | |  | | |/ /| |____
\_| |_/_| |_|_| \_/\_/ \___/|_|  |_|___/ \_____/
```                                          
                                                
A multithreading anime downloader for aniworld.to. Simply download a single episode or an complete anime.

## Usage
1) Clone this repository `git clone https://github.com/inflac/AniworlDL.git` or downloaded the ZIP file
2) Move into the AniwolDL folder
3) Install the necessary requirements with `pip install -r requirements.txt`
4) Start the program from the command line or by using the .exe executable
* [EXE] Start the downloader by double clicking the main.exe file
* [CLI] Start the downloader with `python main.py -a anime_name -s season_number -t amount_of_threads -p path/where/to/store/the/files`

```
usage: main.py [-h] -a ANIME -s SEASON [-e EPISODE] -p PATH [-t THREADS] [-x PROXY]

A simple program with argparse

options:
  -h, --help            show this help message and exit
  -a ANIME, --anime ANIME
                        Specify the anime name
  -s SEASON, --season SEASON
                        Season to download
  -e EPISODE, --episode EPISODE
                        Episode to download
  -p PATH, --path PATH  Location where the downloaded episodes get stored
  -t THREADS, --threads THREADS
                        Amount of threads
  -x PROXY, --proxy PROXY
                        enter an https proxys IP address (e.x 182.152.157.1:80)
```

## Supported streaming services
| streaming service | Supported |
|-------------------|-----------|
| VOE               | ❌        |
| Doodstream        | ❌        |
| Vidoza            | ✅        |
| Streamtape        | ✅        |

## ToDo
| Feature           | Status      |
|-------------------|-------------|
| VOE               | working     |
| Doodstream        | not planned |
| movies            | planned     |
| languages         | planned     |
| proxy support     | unstable    |