"""
OPTC API wrapper
Handles communication with OPTC game servers
"""
import logging
import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class OPTCAPIClient:
    """Client for OPTC game API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def login(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate with OPTC servers
        
        Args:
            username: Account username
            password: Account password
            
        Returns:
            Authentication data with token
        """
        try:
            endpoint = f"{self.base_url}/auth/login"
            payload = {
                'username': username,
                'password': password,
            }
            
            async with self.session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f'Login successful for {username}')
                    return data
                else:
                    logger.error(f'Login failed for {username}: {response.status}')
                    return None
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            return None
    
    async def get_story_chapters(self) -> List[Dict]:
        """Get available story chapters"""
        try:
            endpoint = f"{self.base_url}/content/story"
            async with self.session.get(endpoint, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f'Error fetching story chapters: {str(e)}')
            return []
    
    async def get_events(self) -> List[Dict]:
        """Get current and upcoming events"""
        try:
            endpoint = f"{self.base_url}/content/events"
            async with self.session.get(endpoint, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f'Error fetching events: {str(e)}')
            return []
    
    async def get_missions(self) -> List[Dict]:
        """Get available missions"""
        try:
            endpoint = f"{self.base_url}/content/missions"
            async with self.session.get(endpoint, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f'Error fetching missions: {str(e)}')
            return []
    
    async def complete_level(self, level_id: str) -> Optional[Dict]:
        """
        Complete a level and get rewards
        
        Args:
            level_id: ID of the level to complete
            
        Returns:
            Rewards data
        """
        try:
            endpoint = f"{self.base_url}/gameplay/complete-level"
            payload = {'level_id': level_id}
            
            async with self.session.post(endpoint, json=payload, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f'Error completing level: {str(e)}')
            return None
    
    async def get_account_status(self, account_id: str) -> Optional[Dict]:
        """Get account status and stats"""
        try:
            endpoint = f"{self.base_url}/account/{account_id}/status"
            async with self.session.get(endpoint, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f'Error fetching account status: {str(e)}')
            return None
    
    def _get_headers(self) -> Dict:
        """Get request headers with API key"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }


class GameDataManager:
    """Manages game data cache and updates"""
    
    def __init__(self, api_client: OPTCAPIClient):
        self.api_client = api_client
        self.story_chapters = []
        self.events = []
        self.missions = []
        self.last_update = None
    
    async def update_game_data(self):
        """Fetch and cache all game data"""
        try:
            self.story_chapters = await self.api_client.get_story_chapters()
            self.events = await self.api_client.get_events()
            self.missions = await self.api_client.get_missions()
            self.last_update = datetime.utcnow()
            logger.info('Game data updated successfully')
        except Exception as e:
            logger.error(f'Error updating game data: {str(e)}')
    
    def get_active_events(self) -> List[Dict]:
        """Get currently active events"""
        return [e for e in self.events if e.get('active', False)]
    
    def get_available_missions(self) -> List[Dict]:
        """Get available missions"""
        return self.missions
    
    def get_story_chapters(self) -> List[Dict]:
        """Get all story chapters"""
        return self.story_chapters
