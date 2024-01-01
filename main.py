import threading
import argparse
import queue
import requests
import signal

from helpers import print_header, get_time_formated, parameter_checks, get_episodes_links, download_episode, set_stop_indicator
from helpers import get_stop_indicator
from helpers import GREEN, RED, BLUE, RESET 

threads = []
threads_semaphore = None

# Function to gracefully stop the program on CTRL + C
def stop_program(signum, frame, q):
    global threads, threads_semaphore
    if not get_stop_indicator():
        set_stop_indicator()
    else:
        return

    if signum != None:
        print(f'\n[{get_time_formated(timeformat="%H:%M")}] Ctrl + C detected.')
    else:
        print("Internal Call for program termination.")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Clearing queue ', end="")
    q.mutex
    while not q.empty():
        q.get()
        q.task_done()
    print(f"[{GREEN}Done{RESET}]")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Clearing threads: ', end="")
    for thread in threads:
            thread.join()
            threads.remove(thread)
            threads_semaphore.release()
    print(f"[{GREEN}Done{RESET}]")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Bye')

def download_controller(anime:str, q:queue, path:str): 
    global threads_semaphore

    if get_stop_indicator():
        return
    try:
        episode = q.get(timeout=1)
        for streamer in episode.streaming_services:
            req = requests.get(streamer.url)
            if req.status_code != 200: #Check if episode of streamer is up
                continue
            else:
                if download_episode(episode, streamer, path) == True: #If download fails, continue the loop and try another streamer
                    q.task_done()
                    threads_semaphore.release()
                    return True
                else:
                    continue
        print(f"{RED}ERROR{RESET}: Episode {BLUE}{episode.episode_num}{RESET} could not be downloaded by any streaming service.")
        threads_semaphore.release()
        return False #Return False in case episode could not be downloaded
    except queue.Empty: #Return True in case the queue is empty
        return True

def thread_operator(anime:str, q:queue, threads_amount:int, path:str):
    global threads, threads_semaphore

    while int(q.qsize()) != 0:
        threads_semaphore.acquire()
        thread = threading.Thread(target=download_controller, args=(anime, q, path))
        threads.append(thread)
        thread.start()
        
        for thread in threads:
            if not thread.is_alive():
                thread.join()
                threads.remove(thread)

        if get_stop_indicator():
            stop_program(None, None, q)

def startup(anime=None, season=None, episode=None, threads_amount=None, path=None):
    #Get episode Links with for all Hosters of an episode
    episodes = get_episodes_links(anime=anime, season=season, episode=episode)
    
    #Put Episodes into a queue
    q = queue.Queue()
    for episode in episodes:
        q.put(episode)
    print(f'[{get_time_formated(timeformat="%H:%M")}] Episodes queued [{GREEN}Done{RESET}]')
    
    # Register signal handler for Ctrl + C
    signal.signal(signal.SIGINT, lambda sig, frame: stop_program(sig, frame, q))

    #Start threads with downloading tasks
    thread_operator(anime, q, threads_amount, path)
    
def main():
    global threads_semaphore
    print_header()
    print(f'[{get_time_formated(timeformat="%H:%M")}] AniworldDL started')

    parser = argparse.ArgumentParser(description='A simple program with argparse')
    parser.add_argument('-a', '--anime', required=True, help='Specify the anime name')
    parser.add_argument('-s', '--season', required=True, type=int, default=1, help='Season to download')
    parser.add_argument('-e', '--episode', help='Episode to download')
    parser.add_argument('-p', '--path', required=True, type=str, help='Location where the downloaded episodes get stored')
    parser.add_argument('-t', '--threads', type=int, default=2, help='Amount of threads')

    args = parser.parse_args()
    anime = args.anime
    season = args.season
    episode = args.episode
    threads = args.threads
    path = args.path

    threads_semaphore = threading.Semaphore(threads)

    parameter_checks(anime, season, episode, threads, path)
    startup(anime=anime, season=season, episode=episode, threads_amount=threads, path=path)

if __name__ == '__main__':
    main()