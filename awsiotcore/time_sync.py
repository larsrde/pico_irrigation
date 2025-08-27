import ntptime
import time
import machine
from config import NTP_SERVER, TIME_SYNC_INTERVAL_HOURS

class TimeSync:
    def __init__(self):
        self.last_sync_time = 0
        self.sync_interval_seconds = TIME_SYNC_INTERVAL_HOURS * 3600
        self.rtc = machine.RTC()
        
    def sync_time(self):
        """Synchronize time with NTP server"""
        try:
            print(f"Syncing time with NTP server: {NTP_SERVER}")
            
            # Set NTP server if different from default
            if NTP_SERVER != "pool.ntp.org":
                ntptime.host = NTP_SERVER
            
            # Sync time
            ntptime.settime()
            
            # Update last sync time
            self.last_sync_time = time.time()
            
            # Get current time
            current_time = time.localtime()
            time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                current_time[0], current_time[1], current_time[2],
                current_time[3], current_time[4], current_time[5]
            )
            
            print(f"Time synchronized successfully: {time_str}")
            return True
            
        except Exception as e:
            print(f"Time sync failed: {e}")
            return False
    
    def is_sync_needed(self):
        """Check if time sync is needed"""
        if self.last_sync_time == 0:
            return True  # Never synced
            
        current_time = time.time()
        time_since_sync = current_time - self.last_sync_time
        
        return time_since_sync >= self.sync_interval_seconds
    
    def auto_sync_if_needed(self):
        """Automatically sync time if needed"""
        if self.is_sync_needed():
            return self.sync_time()
        return True
    
    def get_current_time_str(self):
        """Get current time as formatted string"""
        try:
            current_time = time.localtime()
            return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                current_time[0], current_time[1], current_time[2],
                current_time[3], current_time[4], current_time[5]
            )
        except:
            return "Time not available"
    
    def get_timestamp(self):
        """Get current timestamp"""
        return time.time()
    
    def get_time_since_sync(self):
        """Get time elapsed since last sync in seconds"""
        if self.last_sync_time == 0:
            return -1  # Never synced
        return time.time() - self.last_sync_time
    
    def get_status(self):
        """Get time sync status"""
        time_since_sync = self.get_time_since_sync()
        return {
            'current_time': self.get_current_time_str(),
            'last_sync_time': self.last_sync_time,
            'time_since_sync_seconds': time_since_sync,
            'time_since_sync_hours': time_since_sync / 3600 if time_since_sync >= 0 else -1,
            'sync_needed': self.is_sync_needed(),
            'ntp_server': NTP_SERVER,
            'sync_interval_hours': TIME_SYNC_INTERVAL_HOURS
        }