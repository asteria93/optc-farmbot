"""
Farming module
Core farming logic for events, story, and missions
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class FarmingMode(Enum):
    """Available farming modes"""
    STORY = "story"
    EVENTS = "events"
    MISSIONS = "missions"
    GRINDING = "grinding"
    ALL = "all"

class FarmingStrategy(Enum):
    """Farming intensity strategies"""
    AGGRESSIVE = "aggressive"
    MODERATE = "moderate"
    CONSERVATIVE = "conservative"

class Farmer:
    """Main farming bot class"""
    
    def __init__(self, account_id: str, account_data: Dict):
        self.account_id = account_id
        self.account_data = account_data
        self.farming_active = False
        self.current_mode = None
        self.strategy = FarmingStrategy.MODERATE
        self.farming_history = []
    
    def start_farming(self, mode: FarmingMode = FarmingMode.ALL, strategy: FarmingStrategy = FarmingStrategy.MODERATE) -> Dict:
        """
        Start farming operation
        
        Args:
            mode: Farming mode to use
            strategy: Farming strategy intensity
            
        Returns:
            Farming session data
        """
        self.farming_active = True
        self.current_mode = mode
        self.strategy = strategy
        
        session = {
            'start_time': datetime.utcnow(),
            'mode': mode.value,
            'strategy': strategy.value,
            'runs': 0,
            'rewards': {
                'berries': 0,
                'gold': 0,
                'experience': 0,
            },
        }
        
        logger.info(f'Farming started for account {self.account_id}: mode={mode.value}, strategy={strategy.value}')
        return session
    
    def stop_farming(self) -> Dict:
        """Stop farming operation"""
        self.farming_active = False
        session = {
            'end_time': datetime.utcnow(),
            'total_runs': len(self.farming_history),
            'status': 'completed',
        }
        logger.info(f'Farming stopped for account {self.account_id}')
        return session
    
    def farm_story(self, chapter: int) -> Dict:
        """Farm a story chapter"""
        rewards = self._calculate_rewards('story', chapter)
        self._record_farming_run('story', chapter, rewards)
        return rewards
    
    def farm_event(self, event_id: str) -> Dict:
        """Farm an event"""
        rewards = self._calculate_rewards('event', event_id)
        self._record_farming_run('event', event_id, rewards)
        return rewards
    
    def farm_mission(self, mission_id: str) -> Dict:
        """Farm a mission"""
        rewards = self._calculate_rewards('mission', mission_id)
        self._record_farming_run('mission', mission_id, rewards)
        return rewards
    
    def farm_grinding(self, location: str) -> Dict:
        """Farm grinding location"""
        rewards = self._calculate_rewards('grinding', location)
        self._record_farming_run('grinding', location, rewards)
        return rewards
    
    def _calculate_rewards(self, farm_type: str, target: str) -> Dict:
        """Calculate rewards based on farm type and target"""
        base_rewards = {
            'story': {'berries': 100, 'gold': 50, 'experience': 500},
            'event': {'berries': 200, 'gold': 100, 'experience': 1000},
            'mission': {'berries': 50, 'gold': 25, 'experience': 250},
            'grinding': {'berries': 150, 'gold': 75, 'experience': 750},
        }
        
        multiplier = 1.0 if self.strategy == FarmingStrategy.MODERATE else \
                    1.5 if self.strategy == FarmingStrategy.AGGRESSIVE else 0.8
        
        rewards = base_rewards.get(farm_type, {'berries': 0, 'gold': 0, 'experience': 0})
        return {k: int(v * multiplier) for k, v in rewards.items()}
    
    def _record_farming_run(self, farm_type: str, target: str, rewards: Dict):
        """Record a farming run in history"""
        run_record = {
            'timestamp': datetime.utcnow(),
            'type': farm_type,
            'target': target,
            'rewards': rewards,
        }
        self.farming_history.append(run_record)
        
        # Update account data
        self.account_data['berry'] += rewards.get('berries', 0)
        self.account_data['gold'] += rewards.get('gold', 0)
        self.account_data['experience'] += rewards.get('experience', 0)
        self.account_data['farming_stats']['total_runs'] += 1
    
    def get_farming_status(self) -> Dict:
        """Get current farming status"""
        return {
            'account_id': self.account_id,
            'farming_active': self.farming_active,
            'current_mode': self.current_mode.value if self.current_mode else None,
            'strategy': self.strategy.value,
            'total_runs': len(self.farming_history),
            'account_level': self.account_data.get('level', 1),
            'total_berries': self.account_data.get('berry', 0),
            'total_gold': self.account_data.get('gold', 0),
            'total_experience': self.account_data.get('experience', 0),
        }


class FarmingScheduler:
    """Schedules and manages farming operations"""
    
    def __init__(self):
        self.scheduled_jobs = {}
        self.active_farmers = {}
    
    def schedule_farming(self, account_id: str, mode: FarmingMode, start_time: str, duration: int) -> Dict:
        """
        Schedule a farming job
        
        Args:
            account_id: Account to farm on
            mode: Farming mode
            start_time: When to start (ISO format)
            duration: Duration in minutes
            
        Returns:
            Job data
        """
        job = {
            'account_id': account_id,
            'mode': mode.value,
            'start_time': start_time,
            'duration': duration,
            'created_at': datetime.utcnow(),
            'status': 'scheduled',
        }
        
        self.scheduled_jobs[account_id] = job
        logger.info(f'Farming scheduled for account {account_id}')
        return job
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get all scheduled jobs"""
        return list(self.scheduled_jobs.values())
    
    def cancel_job(self, account_id: str) -> bool:
        """Cancel a scheduled job"""
        if account_id in self.scheduled_jobs:
            del self.scheduled_jobs[account_id]
            logger.info(f'Job cancelled for account {account_id}')
            return True
        return False
