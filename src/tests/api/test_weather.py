import os
from http import HTTPStatus

import ujson
from httpx import AsyncClient
from pytest_httpx import HTTPXMock
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import settings
from src.clients import open_weather_client
from src.clients import OpenWeatherHTTPClient
from src.models import Weather

url = '/get-by-cities'

london_json = {
    'cod': '200',
    'message': 0,
    'cnt': 1,
    'list': [
        {
            'dt': 1772733600,
            'main': {
                'temp': 288.89,
                'feels_like': 288.14,
                'temp_min': 284,
                'temp_max': 288.89,
                'pressure': 1014,
                'sea_level': 1014,
                'grnd_level': 1010,
                'humidity': 62,
                'temp_kf': 4.89,
            },
            'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01n'}],
            'clouds': {'all': 2},
            'wind': {'speed': 2.51, 'deg': 160, 'gust': 6.63},
            'visibility': 10000,
            'pop': 0,
            'sys': {'pod': 'n'},
            'dt_txt': '2026-03-05 18:00:00',
        }
    ],
    'city': {
        'id': 2643743,
        'name': 'London',
        'coord': {'lat': 51.5085, 'lon': -0.1257},
        'country': 'GB',
        'population': 1000000,
        'timezone': 0,
        'sunrise': 1772692655,
        'sunset': 1772732808,
    },
}

ukraine_json = {
    'cod': '200',
    'message': 0,
    'cnt': 1,
    'list': [
        {
            'dt': 1772733600,
            'main': {
                'temp': 288.89,
                'feels_like': 288.14,
                'temp_min': 284,
                'temp_max': 288.89,
                'pressure': 1014,
                'sea_level': 1014,
                'grnd_level': 1010,
                'humidity': 62,
                'temp_kf': 4.89,
            },
            'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01n'}],
            'clouds': {'all': 2},
            'wind': {'speed': 2.51, 'deg': 160, 'gust': 6.63},
            'visibility': 10000,
            'pop': 0,
            'sys': {'pod': 'n'},
            'dt_txt': '2026-03-05 18:00:00',
        }
    ],
    'city': {
        'id': 2643743,
        'name': 'Ukraine',
        'coord': {'lat': 51.5085, 'lon': -0.1257},
        'country': 'UA',
        'population': 1000000,
        'timezone': 0,
        'sunrise': 1772692655,
        'sunset': 1772732808,
    },
}


async def test_get_weather(
    client: AsyncClient,
    session: AsyncSession,
    httpx_mock: HTTPXMock,
) -> None:
    cities = ['London', 'Ukraine']
    days_forecast = 2
    params: dict[str, int | list[str]] = {'cities': cities, 'days_forecast': days_forecast}
    httpx_mock.add_response(
        method='GET',
        url=open_weather_client.get_url(OpenWeatherHTTPClient.ROUTES.GET_FORECAST_BY_CITY).format(
            city=cities[0],
            cnt=days_forecast * 8,
        ),
        status_code=HTTPStatus.OK,
        json=london_json,
    )
    httpx_mock.add_response(
        method='GET',
        url=open_weather_client.get_url(OpenWeatherHTTPClient.ROUTES.GET_FORECAST_BY_CITY).format(
            city=cities[1],
            cnt=days_forecast * 8,
        ),
        status_code=HTTPStatus.OK,
        json=ukraine_json,
    )
    response = await client.get(url, params=params)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 2

    london_weather = await session.scalar(select(Weather).filter(Weather.city == cities[0]))
    assert london_weather is not None
    ukraine_weather = await session.scalar(select(Weather).filter(Weather.city == cities[1]))
    assert ukraine_weather is not None


async def test_get_weather_city_not_found(
    client: AsyncClient,
    session: AsyncSession,
    httpx_mock: HTTPXMock,
) -> None:
    cities = ['London']
    days_forecast = 2
    params: dict[str, int | list[str]] = {'cities': cities, 'days_forecast': days_forecast}
    httpx_mock.add_response(
        method='GET',
        url=open_weather_client.get_url(OpenWeatherHTTPClient.ROUTES.GET_FORECAST_BY_CITY).format(
            city=cities[0],
            cnt=days_forecast * 8,
        ),
        status_code=HTTPStatus.NOT_FOUND,
        json={'cod': '404', 'message': 'city not found'},
    )
    response = await client.get(url, params=params)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': f"City {cities[0]} does not exists"}


async def test_get_weather_city_wrong_days_forecast_lower_than_1(client: AsyncClient) -> None:
    params: dict[str, int | list[str]] = {'cities': ['London'], 'days_forecast': 0}
    response = await client.get(url, params=params)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_get_weather_city_wrong_days_forecast_bigger_than_5(client: AsyncClient) -> None:
    params: dict[str, int | list[str]] = {'cities': ['London'], 'days_forecast': 6}
    response = await client.get(url, params=params)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_get_weather_cache_hit(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    cities = ['London']
    params: dict[str, int | list[str]] = {'cities': cities, 'days_forecast': 1}
    cache_file = f"{settings.DATA_DIR}/{cities[0]}_cache_test.json"
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    with open(cache_file, 'w') as f:
        ujson.dump(london_json, f)

    await session.execute(
        insert(Weather).values(
            city=cities[0],
            file_path=cache_file,
            hours_forecast=params['days_forecast'] * 8,
        )
    )
    await session.commit()

    response = await client.get(url, params=params)

    assert response.status_code == HTTPStatus.OK

    if os.path.exists(cache_file):
        os.remove(cache_file)


async def test_get_weather_rate_limiter(
    client: AsyncClient,
    session: AsyncSession,
    httpx_mock: HTTPXMock,
) -> None:
    cities = ['London', 'Ukraine']
    days_forecast = 2
    params: dict[str, int | list[str]] = {'cities': cities, 'days_forecast': days_forecast}
    httpx_mock.add_response(
        method='GET',
        url=open_weather_client.get_url(OpenWeatherHTTPClient.ROUTES.GET_FORECAST_BY_CITY).format(
            city=cities[0], cnt=days_forecast * 8
        ),
        status_code=HTTPStatus.OK,
        json=london_json,
    )
    httpx_mock.add_response(
        method='GET',
        url=open_weather_client.get_url(OpenWeatherHTTPClient.ROUTES.GET_FORECAST_BY_CITY).format(
            city=cities[1], cnt=days_forecast * 8
        ),
        status_code=HTTPStatus.OK,
        json=ukraine_json,
    )
    await client.get(url, params=params)
    response = await client.get(url, params=params)
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
