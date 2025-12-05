"""
A helper module to make calls to the NexTrip API.
For reference, the documentation: https://svc.metrotransit.org/swagger/index.html
"""

import requests
from typing import List, Dict, Tuple
from datetime import datetime, time
import json


class ApiCaller:
    """Helper class for Metro Transit API interactions."""

    def __init__(self, debug: bool = False):
        self.nextrip_url = "https://svc.metrotransit.org/nextrip/"
        self.schedule_url = "https://svc.metrotransit.org/schedule/"
        self.max_departures = 3
        self.debug = debug

    def get_departure_times(self, route_id: int, direction_id: int,
                            from_stop: int, to_stop: int) -> List[str]:
        """
        Get the next three departure times for a stop in a given route and direction.

        Args:
            route_id: Route ID (e.g., 921 for A-line)
            direction_id: 1 for East/Northbound, 2 for West/Southbound
            from_stop: Departure stop ID
            to_stop: Destination stop ID

        Returns:
            List of next three departure times
        """
        departure_list = []
        try:
            url = (f"{self.schedule_url}stops/{route_id}/{direction_id}/"
                   f"{from_stop}/{to_stop}/")
            response = self._make_api_request(url)

            if response:
                departures = response.get('departures', [])
                for i in range(min(self.max_departures, len(departures))):
                    departure_time = departures[i].get('board_time')
                    if departure_time:
                        departure_list.append(departure_time)
        except Exception as e:
            if self.debug:
                print(f"Error in get_departure_times: {e}")

        return departure_list

    def get_all_route_ids(self) -> Dict[int, str]:
        """
        Retrieve all route IDs in the Twin Cities Metro Transit system.

        Returns:
            Dictionary mapping route IDs to their labels
        """
        id_map = {}
        try:
            url = f"{self.nextrip_url}routes/"
            response = self._make_api_request(url)

            if response and isinstance(response, list):
                for route in response:
                    route_id = int(route.get('route_id', 0))
                    label = route.get('route_label', '')
                    if route_id:
                        id_map[route_id] = label
        except Exception as e:
            if self.debug:
                print(f"Error in get_all_route_ids: {e}")

        return id_map

    def get_all_stops(self, route_id: int, direction_id: int) -> List['Stop']:
        """
        Get a list of all stops for a given route and direction.

        Args:
            route_id: Route ID (e.g., 63 for Route 63)
            direction_id: integer for direction (varies by route, typically 0-3)

        Returns:
            List of Stop objects

        Note: According to NexTrip API v2, use endpoint:
              GET /nextrip/{route_id}/{direction_id}/{place_code}
              For getting stops, we need to iterate through place codes or use directions endpoint
        """
        from stop import Stop  # Local import to avoid circular dependency

        stop_list = []
        try:
            # First, try to get directions to find valid direction_id
            directions_url = f"{self.nextrip_url}directions/{route_id}"
            directions = self._make_api_request(directions_url)

            if not directions:
                if self.debug:
                    print(f"Could not get directions for route {route_id}")
                return stop_list

            # Get stops for this direction
            stops_url = f"{self.nextrip_url}stops/{route_id}/{direction_id}"
            response = self._make_api_request(stops_url)

            if response and isinstance(response, list):
                for stop_data in response:
                    stop_id = stop_data.get('stop_id') or stop_data.get('place_code')
                    stop_name = stop_data.get('description') or stop_data.get('stop_name')

                    if stop_id and stop_name:
                        new_stop = Stop(int(stop_id) if isinstance(stop_id, int) else stop_id, stop_name)
                        new_stop.add_route(route_id)
                        stop_list.append(new_stop)
        except Exception as e:
            if self.debug:
                print(f"Error in get_all_stops: {e}")

        return stop_list

    def get_transit_time(self, route_id: int, start_stop_id: int,
                         end_stop_id: int, schedule_number: int) -> float:
        """
        Get the transit time in minutes between two stops.

        Args:
            route_id: Route ID
            start_stop_id: Starting stop ID
            end_stop_id: Ending stop ID
            schedule_number: 1 for East/Northbound, 2 for West/Southbound

        Returns:
            Transit time in minutes
        """
        transit_times = []
        try:
            url = (f"{self.schedule_url}stops/{route_id}/{schedule_number}/"
                   f"{start_stop_id}/{end_stop_id}/")
            response = self._make_api_request(url)

            if response:
                departures = response.get('departures', [])

                for i in range(min(self.max_departures, len(departures))):
                    board_time = departures[i].get('board_time')
                    exit_time = departures[i].get('exit_time')

                    if board_time and exit_time:
                        start_time = datetime.strptime(board_time, '%H:%M:%S').time()
                        end_time = datetime.strptime(exit_time, '%H:%M:%S').time()

                        # Calculate duration in minutes
                        start_dt = datetime.combine(datetime.today(), start_time)
                        end_dt = datetime.combine(datetime.today(), end_time)
                        duration = (end_dt - start_dt).total_seconds() / 60

                        transit_times.append(duration)

            return transit_times[0] if transit_times else 0.0

        except Exception as e:
            if self.debug:
                print(f"Error in get_transit_time: {e}")
            return 0.0

    def get_coordinate(self, coordinate_type: str, stop_id: int) -> float:
        """
        Get the specified coordinate (latitude or longitude) for a stop.

        Args:
            coordinate_type: Either "latitude" or "longitude"
            stop_id: Stop ID

        Returns:
            The requested coordinate value
        """
        try:
            url = f"{self.nextrip_url}{stop_id}/"
            response = self._make_api_request(url)

            if response:
                stops = response.get('stops', [])
                if stops and len(stops) > 0:
                    return stops[0].get(coordinate_type, 0.0)
        except Exception as e:
            if self.debug:
                print(f"Error in get_coordinate: {e}")

        return 0.0

    def get_route_ids_from_stop_id(self, stop_id: int) -> List[int]:
        """
        Get the route IDs that service a given stop.

        Args:
            stop_id: Stop ID

        Returns:
            List of route IDs
        """
        routes_list = []
        try:
            url = f"{self.nextrip_url}{stop_id}/"
            response = self._make_api_request(url)

            if response:
                departures = response.get('departures', [])

                for departure in departures:
                    route_id = departure.get('route_id')
                    if route_id and route_id not in routes_list:
                        routes_list.append(route_id)
        except Exception as e:
            if self.debug:
                print(f"Error in get_route_ids_from_stop_id: {e}")

        return routes_list

    def _make_api_request(self, url: str) -> Dict:
        """
        Helper method to make API requests.

        Args:
            url: The URL to request

        Returns:
            JSON response as dictionary
        """
        if self.debug:
            print(f"Requesting URL: {url}")

        try:
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 404:
                raise Exception("Error 404: Resource not found")
            elif response.status_code == 400:
                raise Exception(f"Error 400: Bad request for URL: {url}")
            elif response.status_code != 200:
                raise Exception(f"HTTP request failed with code: {response.status_code}")

            return response.json()

        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"Request exception: {e}")
            raise


if __name__ == "__main__":
    caller = ApiCaller(debug=True)

    # Test get route IDs from stop ID
    route_ids = caller.get_route_ids_from_stop_id(19315)
    print(f"Route IDs for stop 19315: {route_ids}")