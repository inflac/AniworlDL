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
    if not get_stop_indicator(): #In case the program already handles a stop signal, do not run this function again
        set_stop_indicator()
    else:
        return

    if signum != None:
        print(f'\n[{get_time_formated(timeformat="%H:%M")}] Ctrl + C detected.')
    else:
        print("Internal Call for program termination.")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Clearing queue ', end="") #Empty the queue to avoid new threads get started
    q.mutex
    while not q.empty():
        q.get()
        q.task_done()
    print(f"[{GREEN}Done{RESET}]")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Clearing threads: ', end="") #Join every thread for cleanup
    for thread in threads:
            thread.join()
            threads.remove(thread)
            threads_semaphore.release()
    print(f"[{GREEN}Done{RESET}]")

    print(f'[{get_time_formated(timeformat="%H:%M")}] Bye') #Say good bye ^^

def download_controller(anime:str, q:queue, path:str, proxy:dict): 
    global threads_semaphore

    if get_stop_indicator():
        return
    try:
        episode = q.get(timeout=1)
        for streamer in episode.streaming_services: #While episodes download isn't successful, try other streaming services
            req = requests.get(streamer.url, proxies=proxy)
            if req.status_code != 200: #Check if episode of streamer is up
                continue
            else:
                if download_episode(episode, streamer, path, proxy) == True: #If download fails, continue the loop and try another streamer
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

def thread_operator(anime:str, q:queue, threads_amount:int, path:str, proxy:dict):
    global threads, threads_semaphore

    while int(q.qsize()) != 0: #For every queue element, create a thread. passivly wait while max num of threads is reached
        threads_semaphore.acquire()
        thread = threading.Thread(target=download_controller, args=(anime, q, path, proxy))
        threads.append(thread)
        thread.start()
        
        for thread in threads: #For every active thread, check if he is still alive, otherwise join it.
            if not thread.is_alive():
                thread.join()
                threads.remove(thread)

        if get_stop_indicator(): #In case CTRL + C was detected, terminate the program
            stop_program(None, None, q)
            return

def startup(anime=None, season=None, episode=None, threads_amount=None, path=None, proxy=None):
    #Get episode Links with for all Hosters of an episode
    episodes = get_episodes_links(anime=anime, season=season, episode=episode, proxy=proxy)
    
    #Put Episodes into a queue
    q = queue.Queue()
    for episode in episodes:
        q.put(episode)
    print(f'[{get_time_formated(timeformat="%H:%M")}] Episodes queued [{GREEN}Done{RESET}]')
    
    # Register signal handler for Ctrl + C
    signal.signal(signal.SIGINT, lambda sig, frame: stop_program(sig, frame, q))

    #Start threads with downloading tasks
    thread_operator(anime, q, threads_amount, path, proxy)
    
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
    parser.add_argument('-x', '--proxy', type=str, default=None, help='enter an https proxys IP address (e.x 182.152.157.1:80)')

    args = parser.parse_args()
    anime = args.anime
    season = args.season
    episode = args.episode
    threads = args.threads
    path = args.path
    proxy_ip = args.proxy

    if proxy_ip != None: #Configure proxy dict
        proxy = {'https': 'https://' + proxy_ip}
    else:
        proxy = None

    threads_semaphore = threading.Semaphore(threads) #create a semaphore with the maximum amount of threads 

    parameter_checks(anime, season, episode, threads, path, proxy)
    startup(anime=anime, season=season, episode=episode, threads_amount=threads, path=path, proxy=proxy)

if __name__ == '__main__':
    main()