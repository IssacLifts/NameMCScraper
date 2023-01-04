from config import Config
from name_mc_profile import NameMCProfile
from subprocess import run
from sys import exit, platform
from typing import List, Dict
from threading import Thread

try:
    from colorama import Fore, init
    import requests
    import pyfiglet
    from pystyle import Colors, Box, Write
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Please run install_dependecies.bat")

    exit(0)   
     
def main():
    """Main function of the program
    """
    
    # Get the ign to be fetched from namemc
    
    account_name: str = Write.Input("Enter a name -> ", Colors.red_to_purple, interval=0.0025)
    
    validate_input(account_name)
    
    # Fetch the correct id so the link succeeds
    profile_id: str = find_profile_generation(account_name)
    
    # if 'profile_id' is None, it means the ign dosent exsist.
      
    if profile_id is None:
        print(f"{Fore.RED}{account_name} does not exsist.")
        
        clear_main()
    
    # If 'profile_id' is False, it means the search request must've failed.
    
    if not profile_id:
        print(f"{Fore.RED}No profile id found")
        clear_main()
    
    # Build the site URL
    
    namemc_profile_url: str = build_site_url(account_name, profile_id)
 
    # Send request to profile
    
    namemc_profile_response: requests.Response = requests.get(namemc_profile_url,
                    allow_redirects=True,
                    headers=NAMEMC_HEADERS)
    
    # The cookie may have expired if this happens.
    
    if (status_code := namemc_profile_response.status_code) != 200:
        print(f"{Fore.RED}Profile request failed with\
            status code [{Fore.LIGHTYELLOW_EX}{status_code}{Fore.RED}]. \
            Perhaps there are capital/lower letters")
        
        clear_main()
      
    # Parse the profile into html
    
    profile_soup: BeautifulSoup = BeautifulSoup(namemc_profile_response.text, 'html.parser')
    
    # Convert the html to a NameMC Profile
    
    namemc_profile: NameMCProfile = NameMCProfile(profile_soup)
    
    setup_threads(namemc_profile)
       
    print_namemc_profile(FAVOURITE_SERVERS,
                         account_name,
                         FOLLOWERS_AMOUNT,
                         PAST_NAMES,
                         PROFILE_VIEWS,
                         PROFILE_UUID,
                         PROFILE_CAPES)
    
def find_profile_generation(account_name: str) -> str:
    """Find the profile generation

    Args:
        account_name (str): account name

    Returns:
        str: returns an ID
    """
    # Send a request to the search api
    
    search_request: requests.Response = requests.get("https://namemc.com/search?q=%s" % (account_name),
                                   headers=NAMEMC_HEADERS,
                                   data={"q": account_name})
    
    # status code 403 = expired cookie
    
    if (search_status := search_request.status_code) == 403:
        print(f"{Fore.RED}Cookie expired: [{Fore.LIGHTYELLOW_EX}{search_status}{Fore.RED}]")
        
        exit(0)
    
    # Return None if the status code is not 200
    
    elif (search_status := search_request.status_code) != 200:
        print(f"{Fore.RED}Search request failed \
with status code [{Fore.LIGHTYELLOW_EX}{search_status}{Fore.RED}]")
        
        return False

    # Parse the website to html
    
    soup = BeautifulSoup(search_request.text, "html.parser")
    
    # Returns the correct profile id (string) which is returned from the 'fetch_correct_profile_id' function
    
    return fetch_correct_profile_id(soup)
    
def build_site_url(name: str, profile_id: str) -> str:
    """Builds the profile site url

    Args:
        name (str): Account IGN
        id (str): ID of the profile

    Returns:
        str: Completed site url
    """
    
    return "https://namemc.com/profile/" + name + profile_id

def fetch_correct_profile_id(soup: BeautifulSoup) -> str:
    """Fetches the correct profile ID

    Args:
        soup (BeautifulSoup): HTML parsed soup

    Returns:
        str: correct profile ID
    """
 
    # Find all tags that start with <h5> and check if 'results' is in the text.
    
    # Returns the version generation if 'results' is found   
    
    for h5 in soup.find_all('h5'):
        
        if "Profiles" in (h5_text := h5.text):
            
            # If 'results' is not in h5_text it means there's only one account that's had the ign, so we return '.1'
            
            if "results" not in h5_text:
                return ".1"
            
            # If the code got here, it means there's more than one profile that's had the ign.
            
            h5_split = h5_text.split(":")
            
            return ("." + h5_split[1].split("result")[0].rstrip()).replace("\u2002", "")
        
    # Returns None if 'Profiles' is not found in any text
    
    return None

def validate_input(name: str) -> None:
    """Validates the name to see if it's correct

    Args:
        name (str): The input
    """

    if len(name) <= 0:
        print(f"{Fore.RED}The name entered was too short!")
        
        main()
        
    elif len(name) > 16:
        print(f"{Fore.RED}The name entered was too long!")        
        main()
    
    # Check every character in the 'name' variable if its an alphanumeric character excluding '_'
        
    elif any(not char.isalnum() for char in name if char != "_"):
        print(f"{Fore.RED}Special characters are probhibited!")
        
        main()

def execute_assign_user_profile_methods(name_mc_profile_method: NameMCProfile.__call__, variable_name: str) -> None:
    """Executes profile methods and assigns the variables related to the method, this is used for concurrency

    Args:
        name_mc_profile_method (NameMCProfile): The method to be called of the NameMCProfile Object
        variable_name (str): The variable to be assigned
    """
    
    if variable_name == "FAVOURITE_SERVERS":
        global FAVOURITE_SERVERS
        FAVOURITE_SERVERS = name_mc_profile_method()
        
    elif variable_name == "FOLLOWERS_AMOUNT":
        global FOLLOWERS_AMOUNT
        FOLLOWERS_AMOUNT = name_mc_profile_method()
        
    elif variable_name == "PAST_NAMES":
        global PAST_NAMES
        PAST_NAMES = name_mc_profile_method()
    
    elif variable_name == "PROFILE_UUID":
        global PROFILE_UUID
        PROFILE_UUID = name_mc_profile_method()
    
    elif variable_name == "PROFILE_CAPES":
        global PROFILE_CAPES
        PROFILE_CAPES = name_mc_profile_method()
    
    else:
        global PROFILE_VIEWS
        PROFILE_VIEWS = name_mc_profile_method()

def setup_threads(name_mc_profile: NameMCProfile) -> None:
    function_names: List[Dict[name_mc_profile.__call__, str]] = [
        {name_mc_profile.fetch_profile_favourite_servers: "FAVOURITE_SERVERS"},
        {name_mc_profile.fetch_profile_followers_amount: "FOLLOWERS_AMOUNT"},
        {name_mc_profile.fetch_profile_past_names: "PAST_NAMES"},
        {name_mc_profile.fetch_profile_views: "PROFILE_VIEWS"},
        {name_mc_profile.fetch_profile_uuid: "PROFILE_UUID"},
        {name_mc_profile.fetch_profile_capes: "PROFILE_CAPES"}
    ]
    
    thread_pool: List[Thread] = []
    
    for func_name in function_names:
        thread_pool.append(Thread(target=execute_assign_user_profile_methods, args=(list(func_name.keys())[0], list(func_name.values())[0],)))

    for thread in thread_pool:
        thread.start()
           
    for thread in thread_pool:
        thread.join()

def clear(os: str) -> None:   
    """Clears the console
    
    args: os - the operating system the script is being ran on
    """

    if os == "win32":  
        # Clears the console using powershell which is only avaliable on windows
        
        run("cls", shell=True)
        
    else:   
        # Clears using whatever the clients os's terminal
        
        run('clear')

def clear_main() -> None:
    clear()
    main()
        
def print_namemc_profile(favourite_servers: List[str],
                         profile_name: str,
                         profile_followers: int,
                         past_names: List[str],
                         views_amount: int,
                         profile_uuid: str,
                         profile_capes: List[str]):
    
    Write.Print(Box.DoubleCube(f"{profile_name}'s profile"), Colors.blue_to_red)
    print(f"{Fore.RED}UUID: {Fore.LIGHTYELLOW_EX}{profile_uuid}")
    print(f"{Fore.RED}Views: {Fore.LIGHTYELLOW_EX}{views_amount} / month")
    print(f"{Fore.RED}Followers: {Fore.LIGHTYELLOW_EX}{profile_followers}\n")
    
    print(f"{Fore.MAGENTA}-------------------------------------------------------")
    print(f"                  {Fore.RED}PAST NAMES")
    print(f"{Fore.MAGENTA}-------------------------------------------------------")
    for past_name in past_names:
        print(f"{Fore.LIGHTYELLOW_EX}{past_name}")
        
    print("")
        
    print(f"{Fore.MAGENTA}-------------------------------------------------------")
    print(f"                  {Fore.RED}CAPES")
    print(f"{Fore.MAGENTA}-------------------------------------------------------")
    for cape in profile_capes:
        print(f"{Fore.LIGHTYELLOW_EX}{cape}") 
        
    print("")
    print(f"{Fore.MAGENTA}-------------------------------------------------------")
    print(f"                  {Fore.RED}FAVOURITE SERVERS")
    for server in favourite_servers:
        print(f"{Fore.LIGHTYELLOW_EX}{server}")
        
    main()
   
if __name__ == "__main__":
    clear(platform)
    ascii_banner = pyfiglet.figlet_format("NameMC Scraper")
    
    Write.Print(ascii_banner, Colors.blue_to_purple, interval=0)
    
    init(autoreset=True)
    
    NAMEMC_HEADERS: dict = {"cookie": Config.COOKIE,
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0"}
    
    main()
