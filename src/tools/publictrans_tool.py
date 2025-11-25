from async_googlemaps import AsyncClient
import aiohttp
from datetime import datetime
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.getAPI import getApiKey


class Public_Trans_Tool():
    def __init__(self):
        pass  

    async def __get_transit_route(self, origin_address, dest_address):
        """
        Google Directions v2: computeRoutes 호출 함수
        """


        async with aiohttp.ClientSession() as client:
            gmaps = AsyncClient(client, key=getApiKey("GOOGLE_API_KEY"))

            # # Geocoding an address
            # geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

            # # Look up an address with reverse geocoding
            # reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

            # Request directions via public transit
            now = datetime.now()
            directions_result = await gmaps.directions(origin_address,
                                                dest_address,
                                                mode="transit",
                                                departure_time=now,
                                                region="ko",
                                                language="ko")
            return directions_result
        
    async def _get_kakao_taxi_fare(self, origin, destination):
        params = {
            "origin": origin,
            "destination": destination,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(getApiKey("KAKAO_API_KEY"), params=params)
            data = response.json()

            return data["results"][0]["summary"]["fare"]["taxi"]

    def __currency_calculation(self, value):
        """환율 계산"""
        pass 


    async def tool_get_public_trans_direct(self, config):
        """
        버스,지하철로 가는 방법과 예상비용(google maps api)
        return
            {
                "direction": dict(api response)
                "price": str
            }
        """
        origin = config["origin"]
        dest = config["dest"]
        nation = config["nation"]
        def display_route_info(data):
            """
            구글 맵스 Directions API 응답 데이터를 보기 좋게 출력하는 함수
            """
            
            for route_idx, route in enumerate(data, 1):
                print("=" * 80)
                print(f"경로 {route_idx}")
                print("=" * 80)
                
                # 경로 요약 정보
                if route.get('summary'):
                    print(f"\n📍 경로 요약: {route['summary']}")
                
                # 저작권 정보
                if route.get('copyrights'):
                    print(f"ℹ️  {route['copyrights']}")
                
                # 경고 메시지
                if route.get('warnings'):
                    print(f"\n⚠️  주의사항:")
                    for warning in route['warnings']:
                        print(f"   - {warning}")
                
                # 각 구간(leg) 정보
                for leg_idx, leg in enumerate(route.get('legs', []), 1):
                    print(f"\n{'─' * 80}")
                    print(f"구간 {leg_idx}")
                    print(f"{'─' * 80}")
                    
                    # 출발지/도착지
                    print(f"\n🚩 출발: {leg['start_address']}")
                    print(f"🏁 도착: {leg['end_address']}")
                    
                    # 시간 및 거리 정보
                    print(f"\n⏰ 출발 시간: {leg['departure_time']['text']}")
                    print(f"⏰ 도착 시간: {leg['arrival_time']['text']}")
                    print(f"⏱️  소요 시간: {leg['duration']['text']}")
                    print(f"📏 총 거리: {leg['distance']['text']}")
                    
                    # 각 단계(step) 정보
                    print(f"\n{'┄' * 80}")
                    print("상세 경로")
                    print(f"{'┄' * 80}")
                    
                    for step_idx, step in enumerate(leg.get('steps', []), 1):
                        travel_mode = step.get('travel_mode', 'UNKNOWN')
                        
                        if travel_mode == 'WALKING':
                            # 도보 구간
                            print(f"\n🚶 단계 {step_idx}: 도보")
                            print(f"   거리: {step['distance']['text']}")
                            print(f"   시간: {step['duration']['text']}")
                            
                            if step.get('html_instructions'):
                                instructions = step['html_instructions']
                                # HTML 태그 제거 (간단한 방식)
                                instructions = instructions.replace('<span class="location">', '').replace('</span>', '')
                                instructions = instructions.replace('<b>', '').replace('</b>', '')
                                print(f"   안내: {instructions}")
                            
                            # 하위 단계가 있는 경우
                            if 'steps' in step and len(step['steps']) > 1:
                                for substep_idx, substep in enumerate(step['steps'], 1):
                                    if substep.get('html_instructions'):
                                        sub_instructions = substep['html_instructions']
                                        sub_instructions = sub_instructions.replace('<span class="location">', '').replace('</span>', '')
                                        print(f"      {substep_idx}. {sub_instructions} ({substep['distance']['text']})")
                        
                        elif travel_mode == 'TRANSIT':
                            # 대중교통 구간
                            transit = step.get('transit_details', {})
                            line = transit.get('line', {})
                            
                            print(f"\n🚇 단계 {step_idx}: {line.get('vehicle', {}).get('name', '대중교통')}")
                            print(f"   노선: {line.get('short_name', line.get('name', 'N/A'))}")
                            print(f"   색상: {line.get('color', 'N/A')}")
                            print(f"   방면: {transit.get('headsign', 'N/A')}")
                            print(f"   정류장 수: {transit.get('num_stops', 'N/A')}개")
                            
                            # 출발역
                            dep_stop = transit.get('departure_stop', {})
                            print(f"\n   📍 출발역: {dep_stop.get('name', 'N/A')}")
                            print(f"      시간: {transit.get('departure_time', {}).get('text', 'N/A')}")
                            dep_loc = dep_stop.get('location', {})
                            if dep_loc:
                                print(f"      위치: {dep_loc.get('lat', 'N/A')}, {dep_loc.get('lng', 'N/A')}")
                            
                            # 도착역
                            arr_stop = transit.get('arrival_stop', {})
                            print(f"\n   📍 도착역: {arr_stop.get('name', 'N/A')}")
                            print(f"      시간: {transit.get('arrival_time', {}).get('text', 'N/A')}")
                            arr_loc = arr_stop.get('location', {})
                            if arr_loc:
                                print(f"      위치: {arr_loc.get('lat', 'N/A')}, {arr_loc.get('lng', 'N/A')}")
                            
                            # 운영 기관
                            agencies = line.get('agencies', [])
                            if agencies:
                                print(f"\n   🏢 운영: {agencies[0].get('name', 'N/A')}")
                                if agencies[0].get('url'):
                                    print(f"      웹사이트: {agencies[0]['url']}")
                            
                            print(f"\n   ⏱️  소요 시간: {step['duration']['text']}")
                            print(f"   📏 거리: {step['distance']['text']}")
                
                print(f"\n{'=' * 80}\n")


        result = await self.__get_transit_route(origin,dest)
        display_route_info(result)

        # if not nation == "kor":



    async def tool_get_taxi_direct(self, config):
        """
        택시로 가는 방법과 예상비용(kakao maps api)(api는 단순 예상 요금가져오는 용도)
        return
            {
                "direction": list(coord)
                "price": str
            }
        """
        origin = config["origin"]
        dest = config["dest"]
        nation = config["nation"]
        

import asyncio 

async def main():

    public_trans = Public_Trans_Tool()
    await public_trans.tool_get_public_trans_direct(
        {
            "origin": "서울 구로구 새말로 97 신도림테크노마트 지하2층",
            "dest": "서울 중구 충무로4길 3 1층",
            "nation": "kor"
        }
    )


if __name__ == "__main__":
    asyncio.run(main())