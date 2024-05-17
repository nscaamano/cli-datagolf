from .request import RequestHandler
from .models import PlayerFieldUpdatesModel, PlayerFieldUpdateModel, PlayerModel
from collections import OrderedDict

class CommonHandler:

    def __init__(self, request_handler: RequestHandler):
        self._request_handler = request_handler

    @staticmethod
    def _name_comparison(name: str, target_name: str = '') -> bool:        
        if target_name == '': return False
        is_found = True 
        if target_name:
            for name_part in set(name_part.lower().strip() for name_part in target_name.split()): 
                if name_part not in name.lower(): is_found = False             
        return is_found
    
    def get_players(self, player_list_data: list[PlayerModel] = None, dg_id: int = 0, dg_ids: list[int] = [], 
                       name: str = '', names: list[str] = [], **kwargs) -> list[PlayerModel]:
        player_data = player_list_data if player_list_data else self._request_handler.player_list(**kwargs)
        players = [PlayerModel(**player) for player in player_data]
        
        
        if all(not _ for _ in (dg_id, dg_ids, name, names)):
            return players 
        
        target_data: list[PlayerModel] = []
        dg_ids = [int(id_) for id_ in dg_ids]
        dg_ids = [*dg_ids, int(dg_id)] if dg_id else dg_ids
        names = [*names, name] if name  else names
        for player in players:
            for id_ in dg_ids:
                if id_ == player.dg_id:
                    target_data.append(player)
            for name_ in names:
                if CommonHandler._name_comparison(name=player.player_name, target_name=name_): target_data.append(player)
        
        if len(list(set(target_data))) == 1:
            return target_data[0]
        #return list(OrderedDict.fromkeys(target_data)) if target_data else players
        return list(OrderedDict.fromkeys(target_data)) if target_data else []
  
    def get_player_field_updates(self, dg_id: int = 0, dg_ids: list[int] = [], 
                                 name: str = '', names: list[str] = [], tour: str = 'pga') -> PlayerFieldUpdatesModel:

        player_field_updates: PlayerFieldUpdatesModel = self._request_handler.field_updates(tour=tour)
        player_field_updates['field'] = [PlayerFieldUpdateModel(**field_update) for field_update in player_field_updates.get('field')]
        
        if all(not _ for _ in (dg_id, dg_ids, name, names)):
            return player_field_updates
        
        target_data: list[PlayerFieldUpdateModel] = []
        dg_ids = [*dg_ids, dg_id] if dg_id else dg_ids
        names = [*names, name] if name  else names
        for player_field_update in player_field_updates['field']:
            for dg_id in dg_ids:
                if dg_id == player_field_update.dg_id:
                    target_data.append(player_field_update)
            for name_ in names:
                if CommonHandler._name_comparison(name=player_field_update.player_name, target_name=name_): target_data.append(player_field_update)
        
        player_field_updates['field'] = list(OrderedDict.fromkeys(target_data))         
        return player_field_updates   

    def get_current_tournament(self, **kwargs) -> dict:
        return {k: v for k, v in self._request_handler.field_updates(**kwargs).items() if k == 'event_name'}

    def get_current_round(self, **kwargs) -> dict:
        return {k: v for k, v in self._request_handler.field_updates(**kwargs).items() if k == 'current_round'}
    
    def get_player_live_stats(): pass 
    
    def get_player_live_score(): pass 
    
    def get_player_live_predictions(): pass 
    
    def get_player_combined_stats_predictions(): pass 
    
    def get_dg_rankings_amateurs(): pass
    
    def get_leaderboard(size: int = 25, tour: str = 'pga'): pass
    
    
    
    
    
    

    '''
    def get_player_live_stats(self, names: list, **kwargs) -> dict:
        """stats should be a string comma separated list
           i.e. stats='sg_putt,sg_app'
        """
        if 'stats' in kwargs.keys():
            assert ' ' not in kwargs['stats'], "stats should not have spaces. i.e. stats='sg_putt,sg_app'"
        return self._general_filtered_get(request_func=self._request_handler.get_live_stats,
                                          exception_field='live_stats',
                                          names=names, **kwargs)
    '''