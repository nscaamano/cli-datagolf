from typing import (
    List, 
    Dict,
    Union, 
    Optional,
) 
from datetime import datetime, timedelta

from .request import RequestHandler
from .models import (
    PlayerModel,
    PlayerFieldUpdateModel,
    PlayerFieldUpdatesModel,
    TourSchedulesModel,
    EventModel,
)


class DgAPI:
    """TODO add docs
    """
    
    _cache_refesh_key = 'last_refresh'
    
    def __init__(self, api_key: Optional[str] = None):
            
        self._request = RequestHandler(api_key=api_key)  # should be public ? 
        self._cache = {}
            # mainly for tests w/ many repetitive api calls
            # TODO need to keep track of kwargs to see if args change across calls in which case refresh needed
            # cache object (class) ? 
        self.cache_interval = 2  # @property ? should be internal ?  
             
    def refresh(self, endpoints):
        #  TODO refesh endpoints in cache ? 
        pass 
    
    def _check_cache(self, endpoint_func, **kwargs):
        endpoint_name = endpoint_func.__name__
        if not self._cache.get(endpoint_name):
            self._cache[endpoint_name] = endpoint_func(**kwargs) 
            self._cache[DgAPI._cache_refesh_label] = datetime.now()
        
        if self._cache.get(DgAPI._cache_refesh_label) and (
            (datetime.now() - self._cache.get(DgAPI._cache_refesh_label)) > timedelta(minutes=self.cache_interval)
        ): self._cache[endpoint_name] = endpoint_func(**kwargs) 
    
    @staticmethod
    def _filter_dg_objects(
        list_data: list, 
        dg_id: Optional[Union[int, List[int]]] = None, 
        name: Optional[Union[str, List[str]]] = None,
    ) -> List[dict]:
        
        if all(not param for param in (dg_id, name)):
            return list_data 
    
        def match_dg_id(dg_object):
            if isinstance(dg_id, list):
                return dg_object.dg_id in [int(id_) for id_ in dg_id]
            elif dg_id is not None:
                return dg_object.dg_id == int(dg_id)
            return True
        
        def match_name(dg_object):
            player_name_lower = dg_object.player_name.lower()
            if isinstance(name, list):
                return any(all(n.lower() in player_name_lower for n in split_name) for split_name in (n.split() for n in name))
            elif name is not None:
                split_name = name.lower().split()
                return all(n in player_name_lower for n in split_name)
            return True
        
        matched_objects = set()
    
        if dg_id:
            for dg_object in list_data:
                if match_dg_id(dg_object):
                    matched_objects.add(dg_object.dg_id)
        
        if name:
            for dg_object in list_data:
                if match_name(dg_object):
                    matched_objects.add(dg_object.dg_id)
        
        filtered_objects = [player for player in list_data if player.dg_id in matched_objects]
        
        return filtered_objects
    
    def get_players(
        self,      
        dg_id: Optional[Union[int, List[int]]] = None, 
        name: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> List[PlayerModel]:
        endpoint = self._request.player_list
        self._check_cache(endpoint, **kwargs)
        
        return DgAPI._filter_dg_objects(
            list_data=[PlayerModel(**player) for player in self._cache[endpoint.__name__]], 
            name=name, 
            dg_id=dg_id
        )
    
    def get_player_field_updates(
        self,
        dg_id: Optional[Union[int, List[int]]] = None, 
        name: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> PlayerFieldUpdatesModel:
        endpoint = self._request.field_updates
        self._check_cache(endpoint, **kwargs)
        
        update = self._cache[endpoint.__name__]
        update['field'] = DgAPI._filter_dg_objects(
            list_data=[PlayerFieldUpdateModel(**update) for update in update['field']], 
            name=name, 
            dg_id=dg_id
        )
        return PlayerFieldUpdatesModel(**update)

    def get_current_tournament(self, **kwargs) -> Dict[str, str]:
        # TODO for this method and next. Specify tour in returned struct.
        endpoint = self._request.field_updates
        self._check_cache(endpoint, **kwargs)
        return {k: v for k, v in self._cache[endpoint.__name__].items() if k == 'event_name'}

    def get_current_round(self, **kwargs) -> Dict[str, int]:
        endpoint = self._request.field_updates
        self._check_cache(endpoint, **kwargs)
        return {k: v for k, v in self._cache[endpoint.__name__].items() if k == 'current_round'}
    
    def get_tour_schedules(
        self,
        event_name: Optional[Union[str, List[str]]] = None,
        event_id: Optional[Union[int, List[int]]] = None, 
        # location,
        # course
        # TODO support to filter on any field in model for this endpoint's list items. 
        **kwargs
    ) -> TourSchedulesModel: 
        endpoint = self._request.tour_schedules
        self._check_cache(endpoint, **kwargs)
        
        tour_schedules = self._cache[endpoint.__name__]
        tour_schedules['schedule'] = DgAPI._filter_dg_objects(
            list_data=[EventModel(**event) for event in tour_schedules['schedule']], 
            name=event_name, 
            dg_id=event_id, # TODO change to misc_id for now; later support any field filtering 
        )
        return TourSchedulesModel(**tour_schedules)
    
    def get_player_live_stats(): pass 
    
    def get_player_live_score(): pass 
    
    def get_dg_rankings_amateurs(): pass
    
    def get_leaderboard(size: int = 25, tour: str = 'pga'): pass