from bs4 import BeautifulSoup
from typing import List, Set
from threading import Thread

class NameMCProfile:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.profile_soup: BeautifulSoup = soup
        
    def fetch_profile_views(self) -> int:
        """Fetches the amount of views on the users profile

        Returns:
            int: The amount of profile views
        """
        
        # Search divs which have the 'col-auto' class
        
        for div in self.profile_soup.find_all('div', class_="col-auto"):
            if "/ month" in div.text:
                
                # Only get the integer value
                
                return int(div.text.split(" ")[0])
            
            else:
                continue
         
         # If '/ month' is never found, return None
            
        return None
    
    def fetch_profile_followers_amount(self) -> int:
        """Fetches the amount of followers on a players namemc profile

        Returns:
            int: The amount of followers
        """
        
        # Find the tag 'a' with the key '#followers'
        
        profile_followers_tag: BeautifulSoup.tagStack = self.profile_soup.find('a', href="#followers")
        
        # Check if the tag is None, if it is return None and this means an error has occured.
        
        if profile_followers_tag is None:
            return None
        
        # Check if 'Followers (' is in the tag
        
        if "Followers (" in (profile_followers_tag_text := profile_followers_tag.text):
            
            # Split the text so we only get the part with the integer
            
            profile_followers_tag_text_split: List[str] = profile_followers_tag_text.split(" ")
            
            # Remove one of the brackets
            
            bracket_one_removed: str = profile_followers_tag_text_split[1].replace("(", "")
            
            # Remove the other bracket then convert to integer
            
            return int(bracket_one_removed.replace(")", ""))
        
        # If 'Followers (' is not in the tag, it means an error has occured    

        else:
            return None
                    
    def fetch_profile_past_names(self) -> List[str]:
        """Fetches the past names of the user from the user profile

        Returns:
            List[str]: List of the past names
        """
        
        # List of past names
        
        past_names: List[str] = []
        
        # Search over 'a' tags with the key 'translate'
        
        for tag in self.profile_soup.find_all('a', translate='no'):
            
            # Get href tags when '/search?q=' is in the tag and it's not None
            
            if (tag_text := tag.get('href')) is not None and "/search?q=" in tag_text:
                
                # Split the tag into parts
                
                tag_text_split = tag_text.split("=")
                
                # Append the tag[1] to the 'past_names' list
                
                past_names.append(tag_text_split[1])
        
        # Return the 'past_names' list
        
        return past_names
    
    def fetch_profile_favourite_servers(self) -> List[str]:
        """Fetches all of the users favourite servers

        Returns:
            List[str]: List of favourite servers
        """
       
        # List of favourite servers
        
        favourite_servers: List[str] = []
        
        # Search over 'a' tags with the key 'translate'
        
        for tag in self.profile_soup.find_all("a", translate="no"):
            
            # Get href tags when '/server' is in the tag and it's not None
            
            if (tag_server := tag.get("href")) is not None and "/server" in tag_server:
                
                # Split the tag into parts
                
                tag_server_split = tag_server.split("/")
                
                # Append the tag[2] to the 'favourite_servers' list 
                
                favourite_servers.append(tag_server_split[2])
        
        # Return the 'favourite_servers' list
        
        return favourite_servers
    
    def fetch_profile_uuid(self) -> str:
        """Fetches thr specified users UUID

        Returns:
            str: user UUID
        """
        
        # Iterate over divs with the 'style' key
        
        for div in self.profile_soup.find_all("div", style="font-size: 90%"):
            
            # UUIDS are 32 characters long
            
            if len(div.text) == 32:
                return div.text
            
            # If not found, continue
            
            else:
                continue
        
        # Return None if UUID is not found
        
        return None
    
    def fetch_profile_capes(self) -> List[str]:
        """Fetches the specified users capes

        Returns:
            Set[str]: Set of capes
        """
        
        # Set of capes
        
        capes_list: List[str] = []
        
        
        def fetch_optifine_capes() -> None:
            """Searches for optifine capes

            Returns:
                str: Optifine cape
            """
                        
            optifine_html: str = (self.profile_soup.find('a', href="https://optifine.net/home"))
            
            if optifine_html is None:
                return None
            
            optifine_text = optifine_html.text
            
            if optifine_html.text == 'OptiFine':
                capes_list.append(optifine_text.title())
                
            return None
             
        Thread(target=fetch_optifine_capes()).start()
        
        # Search over tags
        
        for tag in self.profile_soup.find_all('a'):
            
            # search for '/cape' link
            
            if "/cape" in tag.get('href'):
                cape_name: str = (tag.get('title'))
                if cape_name != "Minecraft Capes": 
                    capes_list.append(cape_name.title())
                    
                # If it wasnt found, continue
                
                else:
                    continue
                      
            else:
                continue
        
        return capes_list