from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specify specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body model
class SearchQuery(BaseModel):
    name: str
    city_id: str
    cityId: str
    city_name: str
    url: str

# Define the request body model
class City(BaseModel):
    id: str
    cityId: str
    name: str
    url: str

class Locality(BaseModel):
    id: str
    center: list

class Features(BaseModel):
    city: City
    locality: Locality
    propertyType: int
    bedrooms: int
    size: int
    furnishingType: str

class EstimationRequest(BaseModel):
    features: Features
    product: str

@app.post("/search-locality")
def search_property(query: SearchQuery):
    # Define the request payload
    payload = {
        "query": """
          query($searchQuery: SearchQueryInput!, $variant: String, $pageType: String) {
            chimeraTypeAhead(
              searchQuery: $searchQuery
              variant: $variant
              pageType: $pageType
            ) {
              results {
                id
                name
                displayType
                type
                subType
                url
                localityName
                center
              }
              defaultUrl
              isCrossCitySearch
            }
          }
        """,
        "variables": {
            "searchQuery": {
                "name": query.name,
                "service": "buy",
                "category": "residential",
                "city": {
                    "id": query.city_id,
                    "cityId": query.cityId,
                    "name": query.city_name,
                    "url": query.url
                },
                "excludeEntities": []
            },
            "variant": "localitySearch",
            "pageType": "PROPERTY_VALUATION"
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Make the request to the API
    response = requests.post(
        'https://zeusptest.housing.com/api/gql/cache-first?apiName=TYPE_AHEAD_API&emittedFrom=client_buy_COST_VALUATION&isBot=false&source=web',
        json=payload,
        headers=headers
    )

    # Handle the response
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/estimate-propert-value")
def estimate_price(request: EstimationRequest):
    # Define the request payload
    payload = {
        "query": """
          mutation($features: EstimationModelInputV2!, $product: String!) {
            estimatedValueV2(features: $features, product: $product) {
              success
              value
              message
              steps {
                value
                hide
                numValue
              }
              actualValue
              pricePosition
            }
          }
        """,
        "variables": {
            "features": {
                "city": {
                    "id": request.features.city.id,
                    "cityId": request.features.city.cityId,
                    "name": request.features.city.name,
                    "url": request.features.city.url
                },
                "locality": {
                    "id": request.features.locality.id,
                    "center": request.features.locality.center
                },
                "propertyType": request.features.propertyType,
                "bedrooms": request.features.bedrooms,
                "size": request.features.size,
                "furnishingType": request.features.furnishingType
            },
            "product": request.product
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Make the request to the API
    response = requests.post(
        'https://zeusptest.housing.com/api/gql?apiName=PRICE_ESTIMATION&emittedFrom=client_buy_COST_VALUATION&isBot=false&source=web',
        json=payload,
        headers=headers
    )

    # Handle the response
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# # Run the application
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
