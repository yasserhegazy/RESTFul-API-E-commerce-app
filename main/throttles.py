from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'
    rate = '5/minute'
    
class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'
    rate = '100/day'