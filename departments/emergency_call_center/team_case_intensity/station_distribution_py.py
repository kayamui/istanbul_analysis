import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from copy import deepcopy

import pandas as pd

import logging

# Constants
STATION_MAX_ROTATION_COUNT = 3
MAX_ROTATIONS_COUNT_PER_PERSONNEL = 5
DEFAULT_IMPORTANCE = 1


@dataclass
class Personnel:
    id: str
    name: str
    roles: List[str]
    home_station_id: str
    negative_stations: List[str]
    assigned_from: Optional[str] = None
    preferred_stations: List[str] = field(default_factory=list)
    rotation_count: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Personnel':
        return cls(
            id=data['id'],
            name=data['name'],
            roles=data['roles'],
            assigned_from=data.get('assignedFrom'),
            home_station_id=data['homeStationId'],
            negative_stations=data.get('negativeStations', []),
            preferred_stations=data.get('preferredStations', []),
            rotation_count=data.get('rotationCount', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'roles': self.roles,
            'assignedFrom': self.assigned_from,
            'homeStationId': self.home_station_id,
            'negativeStations': self.negative_stations,
            'preferredStations': self.preferred_stations,
            'rotationCount': self.rotation_count
        }

    def can_work_as(self, role: str) -> bool:
        return role in self.roles

    def can_work_at(self, station_id: str) -> bool:
        return station_id not in self.negative_stations

    def copy_with(self, assigned_from: Optional[str] = None, rotation_count: Optional[int] = None) -> 'Personnel':
        new_personnel = deepcopy(self)
        if assigned_from is not None:
            new_personnel.assigned_from = assigned_from
        if rotation_count is not None:
            new_personnel.rotation_count = rotation_count
        return new_personnel


@dataclass
class Station:
    id: str
    region: str
    assigned_personnel: List[Personnel]
    importance: int = DEFAULT_IMPORTANCE
    max_rotation_count: int = STATION_MAX_ROTATION_COUNT

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Station':
        return cls(
            id=data['id'],
            region=data['region'],
            importance=data.get('importance', DEFAULT_IMPORTANCE),
            max_rotation_count=data.get('maxRotationCount', STATION_MAX_ROTATION_COUNT),
            assigned_personnel=[Personnel.from_dict(p) for p in data['assignedPersonnel']]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'region': self.region,
            'importance': self.importance,
            'maxRotationCount': self.max_rotation_count,
            'assignedPersonnel': [p.to_dict() for p in self.assigned_personnel]
        }

    @property
    def medic_count(self) -> int:
        return len([p for p in self.assigned_personnel if p.can_work_as('medic')])

    @property
    def driver_count(self) -> int:
        return len([p for p in self.assigned_personnel if p.can_work_as('driver')])

    @property
    def is_fully_staffed(self) -> bool:
        return self.medic_count >= 2 and self.driver_count >= 1

    @property
    def has_excess_medics(self) -> bool:
        return self.medic_count > 2

    @property
    def has_excess_drivers(self) -> bool:
        return self.driver_count > 1

    def get_missing_roles(self) -> List[str]:
        missing = []
        if self.medic_count < 2:
            missing.append('medic')
        if self.driver_count < 1:
            missing.append('driver')
        return missing

    def get_excess_roles(self) -> List[str]:
        excess = []
        if self.has_excess_medics:
            excess.append('medic')
        if self.has_excess_drivers:
            excess.append('driver')
        return excess


@dataclass
class StationDistributionResult:
    open_stations: List[Station]
    closed_stations: List[Station]
    excess_stations: Dict[str, Dict[str, int]]
    personnel_moved: int
    logs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'openStations': [s.to_dict() for s in self.open_stations],
            'closedStations': [s.to_dict() for s in self.closed_stations],
            'excessStations': self.excess_stations,
            'personnelMoved': self.personnel_moved,
            'logs': self.logs
        }


class StationDistributor:
    def __init__(self, stations: List[Station], neighboring_regions: Dict[str, List[str]], 
                 max_rotations_per_personnel: int = MAX_ROTATIONS_COUNT_PER_PERSONNEL):
        self.stations = stations
        self.neighboring_regions = neighboring_regions
        self.max_rotations_per_personnel = max_rotations_per_personnel
        self.logs: List[str] = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StationDistributor':
        return cls(
            stations=[Station.from_dict(s) for s in data['stations']],
            neighboring_regions=data['neighboringRegions'],
            max_rotations_per_personnel=data.get('maxRotationsPerPersonnel', MAX_ROTATIONS_COUNT_PER_PERSONNEL)
        )

    def get_rotation_count_for_station(self, station: Station) -> int:
        return len([p for p in station.assigned_personnel 
                   if p.assigned_from is not None and p.assigned_from != station.id])

    def distribute_personnel(self) -> StationDistributionResult:
        # Sort stations by importance (highest first)
        self.stations.sort(key=lambda s: s.importance, reverse=True)
        personnel_moved = 0

        # Identify stations with shortage and excess
        stations_with_shortage = [s for s in self.stations if not s.is_fully_staffed]
        stations_with_excess = [s for s in self.stations if s.has_excess_medics or s.has_excess_drivers]
        stations_with_shortage.sort(key=lambda s: s.importance, reverse=True)

        # Dynamic distribution for shortage stations
        while stations_with_shortage:
            shortage_station = stations_with_shortage[0]

            # Is station still short-staffed?
            if shortage_station.is_fully_staffed:
                stations_with_shortage.pop(0)
                continue

            # Check rotation limit
            current_rotations = self.get_rotation_count_for_station(shortage_station)
            remaining_rotations = shortage_station.max_rotation_count - current_rotations
            if remaining_rotations <= 0:
                self.logs.append(f'{shortage_station.id} rotasyon limitine ulaştı ({shortage_station.max_rotation_count}).')
                stations_with_shortage.pop(0)
                continue

            # Find personnel for missing roles
            missing_roles = shortage_station.get_missing_roles()
            station_progress = False

            for role in missing_roles:
                if remaining_rotations <= 0:
                    self.logs.append(f'{shortage_station.id} için rotasyon limiti doldu.')
                    break

                moved_person = self.find_personnel_for_role(role, shortage_station.id, shortage_station.region, stations_with_excess)

                # If no excess personnel, search from any station (including shortage stations, excluding fully staffed)
                if moved_person is None:
                    moved_person = self.find_personnel_from_any_station(role, shortage_station.id, shortage_station.region)

                if moved_person is None:
                    continue

                # Find original station of personnel
                origin_station = None
                for s in self.stations:
                    if any(p.id == moved_person.id for p in s.assigned_personnel):
                        origin_station = s
                        break

                if origin_station is None:
                    raise Exception(f'Orijinal istasyon bulunamadı: {moved_person.id}')

                # Move personnel
                origin_station.assigned_personnel = [p for p in origin_station.assigned_personnel if p.id != moved_person.id]
                updated_person = moved_person.copy_with(
                    assigned_from=origin_station.id,
                    rotation_count=moved_person.rotation_count + 1
                )
                shortage_station.assigned_personnel.append(updated_person)

                personnel_moved += 1
                remaining_rotations -= 1
                station_progress = True
                self.logs.append(f'{updated_person.name} ({role}) {origin_station.id} -> {shortage_station.id}')

                # Check source station personnel count
                if len(origin_station.assigned_personnel) == 1:
                    self.logs.append(f'{origin_station.id} istasyonunda sadece 1 personel kaldı, istasyon kapatılıyor.')
                    if origin_station in stations_with_shortage:
                        stations_with_shortage.remove(origin_station)
                    
                    # Distribute remaining personnel to other stations
                    remaining_person = origin_station.assigned_personnel[0]
                    new_station = self.distribute_remaining_personnel(remaining_person, origin_station.id, origin_station.region)
                    if new_station is not None:
                        origin_station.assigned_personnel.clear()
                        updated_remaining_person = remaining_person.copy_with(
                            assigned_from=origin_station.id,
                            rotation_count=remaining_person.rotation_count + 1
                        )
                        new_station.assigned_personnel.append(updated_remaining_person)
                        personnel_moved += 1
                        self.logs.append(f'{remaining_person.name} ({", ".join(remaining_person.roles)}) {origin_station.id} -> {new_station.id}')

                # Update lists
                stations_with_excess = [s for s in self.stations if s.has_excess_medics or s.has_excess_drivers]
                stations_with_shortage = [s for s in self.stations if not s.is_fully_staffed and len(s.assigned_personnel) > 1]
                stations_with_shortage.sort(key=lambda s: s.importance, reverse=True)

            # If no progress for this station, remove from list
            if not station_progress:
                stations_with_shortage.pop(0)

        # Identify stations with excess personnel
        excess_stations = {}
        for station in self.stations:
            excess_roles = station.get_excess_roles()
            if excess_roles:
                excess_details = {}
                if station.has_excess_medics:
                    excess_details['medic'] = station.medic_count - 2
                if station.has_excess_drivers:
                    excess_details['driver'] = station.driver_count - 1
                excess_stations[station.id] = excess_details
                self.logs.append(f'{station.id} istasyonunda fazla personel: {", ".join([f"{v} {k}" for k, v in excess_details.items()])}')

        # Prepare results
        open_stations = [s for s in self.stations if s.is_fully_staffed]
        closed_stations = [s for s in self.stations if not s.is_fully_staffed]

        return StationDistributionResult(
            open_stations=open_stations,
            closed_stations=closed_stations,
            excess_stations=excess_stations,
            personnel_moved=personnel_moved,
            logs=self.logs
        )

    def find_personnel_for_role(self, role: str, target_station_id: str, target_region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        # 1. Same region
        same_region_personnel = self._find_in_region(role, target_station_id, target_region, excess_stations)
        if same_region_personnel is not None:
            return same_region_personnel

        # 2. Neighboring regions
        neighbor_personnel = self._find_in_neighbor_regions(role, target_station_id, target_region, excess_stations)
        if neighbor_personnel is not None:
            return neighbor_personnel

        # 3. Other regions
        return self._find_in_any_region(role, target_station_id, excess_stations)

    def find_personnel_from_any_station(self, role: str, target_station_id: str, target_region: str) -> Optional[Personnel]:
        # 1. Same region
        same_region_personnel = self._find_in_region_from_any_station(role, target_station_id, target_region)
        if same_region_personnel is not None:
            return same_region_personnel

        # 2. Neighboring regions
        neighbor_personnel = self._find_in_neighbor_regions_from_any_station(role, target_station_id, target_region)
        if neighbor_personnel is not None:
            return neighbor_personnel

        # 3. Other regions
        return self._find_in_any_region_from_any_station(role, target_station_id)

    def distribute_remaining_personnel(self, person: Personnel, origin_station_id: str, origin_region: str) -> Optional[Station]:
        # 1. Same region
        same_region_station = self._find_station_in_region(person, origin_station_id, origin_region)
        if same_region_station is not None:
            return same_region_station

        # 2. Neighboring regions
        neighbor_region_station = self._find_station_in_neighbor_regions(person, origin_station_id, origin_region)
        if neighbor_region_station is not None:
            return neighbor_region_station

        # 3. Other regions
        return self._find_station_in_any_region(person, origin_station_id)

    def _find_station_in_region(self, person: Personnel, origin_station_id: str, region: str) -> Optional[Station]:
        for role in person.roles:
            shortage_stations = [s for s in self.stations 
                               if s.region == region and not s.is_fully_staffed and s.id != origin_station_id 
                               and role in s.get_missing_roles()]
            shortage_stations.sort(key=lambda s: s.importance, reverse=True)
            
            # Start from most important stations
            for station in shortage_stations:
                current_rotations = self.get_rotation_count_for_station(station)
                if current_rotations >= station.max_rotation_count:
                    continue
                if not person.can_work_at(station.id) or person.rotation_count >= self.max_rotations_per_personnel:
                    continue
                return station
        return None

    def _find_station_in_neighbor_regions(self, person: Personnel, origin_station_id: str, origin_region: str) -> Optional[Station]:
        neighbors = self.neighboring_regions.get(origin_region, [])
        for neighbor in neighbors:
            station = self._find_station_in_region(person, origin_station_id, neighbor)
            if station is not None:
                return station
        return None

    def _find_station_in_any_region(self, person: Personnel, origin_station_id: str) -> Optional[Station]:
        for role in person.roles:
            shortage_stations = [s for s in self.stations 
                               if not s.is_fully_staffed and s.id != origin_station_id 
                               and role in s.get_missing_roles()]
            shortage_stations.sort(key=lambda s: s.importance, reverse=True)
            
            for station in shortage_stations:
                current_rotations = self.get_rotation_count_for_station(station)
                if current_rotations >= station.max_rotation_count:
                    continue
                if not person.can_work_at(station.id) or person.rotation_count >= self.max_rotations_per_personnel:
                    continue
                return station
        return None

    def _find_in_region(self, role: str, target_station_id: str, region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        region_stations = [s for s in excess_stations if s.region == region]
        for station in region_stations:
            personnel = self._find_suitable_personnel(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_neighbor_regions(self, role: str, target_station_id: str, target_region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        neighbors = self.neighboring_regions.get(target_region, [])
        for neighbor in neighbors:
            personnel = self._find_in_region(role, target_station_id, neighbor, excess_stations)
            if personnel is not None:
                return personnel
        return None

    def _find_in_any_region(self, role: str, target_station_id: str, excess_stations: List[Station]) -> Optional[Personnel]:
        for station in excess_stations:
            personnel = self._find_suitable_personnel(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_region_from_any_station(self, role: str, target_station_id: str, region: str) -> Optional[Personnel]:
        region_stations = [s for s in self.stations 
                          if s.region == region and s.id != target_station_id 
                          and not (s.is_fully_staffed and not s.has_excess_medics and not s.has_excess_drivers)]
        # Start from less important stations
        region_stations.sort(key=lambda s: s.importance)
        
        for station in region_stations:
            personnel = self._find_suitable_personnel_from_any_station(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_neighbor_regions_from_any_station(self, role: str, target_station_id: str, target_region: str) -> Optional[Personnel]:
        neighbors = self.neighboring_regions.get(target_region, [])
        for neighbor in neighbors:
            personnel = self._find_in_region_from_any_station(role, target_station_id, neighbor)
            if personnel is not None:
                return personnel
        return None

    def _find_in_any_region_from_any_station(self, role: str, target_station_id: str) -> Optional[Personnel]:
        other_stations = [s for s in self.stations 
                         if s.id != target_station_id 
                         and not (s.is_fully_staffed and not s.has_excess_medics and not s.has_excess_drivers)]
        # Start from less important stations
        other_stations.sort(key=lambda s: s.importance)
        
        for station in other_stations:
            personnel = self._find_suitable_personnel_from_any_station(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_suitable_personnel(self, station: Station, role: str, target_station_id: str) -> Optional[Personnel]:
        if role not in station.get_excess_roles():
            return None

        candidates = [p for p in station.assigned_personnel 
                     if p.can_work_as(role) and p.can_work_at(target_station_id) 
                     and p.rotation_count < self.max_rotations_per_personnel]

        if not candidates:
            return None

        # Prioritize those in rotation
        rotating = [p for p in candidates if p.assigned_from is not None and p.assigned_from != station.id]
        suitable = rotating if rotating else candidates

        # Select the one with least rotations
        suitable.sort(key=lambda p: p.rotation_count)
        least_rotated = [p for p in suitable if p.rotation_count == suitable[0].rotation_count]

        # Prioritize preferred station
        for p in least_rotated:
            if target_station_id in p.preferred_stations:
                return p
        return least_rotated[0]

    def _find_suitable_personnel_from_any_station(self, station: Station, role: str, target_station_id: str) -> Optional[Personnel]:
        # Station must have at least 1 personnel with the required role
        candidates = [p for p in station.assigned_personnel 
                     if p.can_work_as(role) and p.can_work_at(target_station_id) 
                     and p.rotation_count < self.max_rotations_per_personnel]

        if not candidates:
            return None

        # Prioritize those in rotation
        rotating = [p for p in candidates if p.assigned_from is not None and p.assigned_from != station.id]
        suitable = rotating if rotating else candidates

        # Select the one with least rotations
        suitable.sort(key=lambda p: p.rotation_count)
        least_rotated = [p for p in suitable if p.rotation_count == suitable[0].rotation_count]

        # Prioritize preferred station
        for p in least_rotated:
            if target_station_id in p.preferred_stations:
                return p
        return least_rotated[0]


def main():
    with open('C:/Users/mkaya/Onedrive/Masaüstü/data.json', 'r', encoding= 'utf-8') as f:
        data= json.load(f)

    distributor = StationDistributor.from_dict(data)
    result = distributor.distribute_personnel()

    print(f'Açık İstasyonlar: {len(result.open_stations)}')
    print(f'Kapalı İstasyonlar: {len(result.closed_stations)}')
    print(f'Taşınan Personel: {result.personnel_moved}')
    print('\nİşlem Logları:')
    open_station_names = [s.id for s in result.open_stations]
    closed_station_names = [s.id for s in result.closed_stations]
    logs = result.logs

    max_len = max(len(open_station_names), len(closed_station_names), len(logs))

    def pad(lst):
        return lst + [''] * (max_len - len(lst))

    result_excel = pd.DataFrame({
        'Açılan İstasyonlar': pad(open_station_names),
        'İşlem Logları': pad(logs),
        'Kapalı İstasyonlar': pad(closed_station_names)
    })

    result_excel.to_excel('C:/Users/mkaya/Onedrive/Masaüstü/result.xlsx', index=False)
    for log in result.logs:
        print(f'- {log}')
        


if __name__ == "__main__":
    main()