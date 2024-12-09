from fastapi import APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from config.db import conn
from models.model import *
from auth.userauth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_admin
from datetime import timedelta
from bson import ObjectId
from typing import List


user = APIRouter()

templates = Jinja2Templates(directory="templates")

# @user.post("/register", response_class=JSONResponse)
# async def add_user(request: User):
#     try:
        
#         request.username = request.username.lower()
#         user = conn.user.mortgage_details.insert_one(dict(request))
        
#         user_details = {
#             "name": request.name,
#             "username": request.username.lower(),
#             "email": request.email,
#             "contactnumber": request.contactnumber
#         }
        
#         return {"user_details": user_details}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


############################### USER REGISTRATION ################################
@user.post("/register", response_class=JSONResponse)
async def add_user(request: User):
    try:
        request.username = request.username.lower()

        existing_user_by_username = conn.user.mortgage_details.find_one(
            {"username": request.username}
        )
        if existing_user_by_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists."
            )
        
        existing_user_by_email = conn.user.mortgage_details.find_one(
            {"email": request.email}
        )
        if existing_user_by_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

        # Insert the new user
        user = conn.user.mortgage_details.insert_one(dict(request))
        
        # Prepare the user details response
        user_details = {
            "name": request.name,
            "username": request.username,
            "email": request.email,
            "contactnumber": request.contactnumber
        }
        
        return {"user_details": user_details}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


################################ USER LOGIN #####################################
@user.post("/login", response_model=Token)
async def login(login_data: LoginModel):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": login_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    user_details = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "contactnumber": str(user.get("contactnumber", "")),
    }
    mortgage = {
        "hasMortgage": str(user.get("hasMortgage")),
        "isLookingForMortgage": str(user.get("isLookingForMortgage")),
        }
    return {"access_token": access_token, "token_type": "bearer", "user_details": user_details, "mortgage": mortgage}

# @user.put("/mortgage/{username}")
# async def update_mortgage_details(username: str, details: MortgageDetails):
#     existing_user = conn.user.mortgage_details.find_one({"username": username})
#     print(dict(existing_user))
#     if existing_user:
#         conn.user.mortgage_details.update_one(
#             {"username": username},
#             {"$set": details.dict()}
#         )
#         return {"message": "User data updated successfully!", "data": details}


################################# ADD RESPONSE #######################################
@user.post("/add_mortgage_data/")
async def add_mortgage_data(data: MortgageDetails):
    try:
        user_doc = conn.user.mortgage_details.find_one({"username": data.username})
        
        if data.hasMortgage:
            entry = {
                "_id": ObjectId(),
                "hasMortgage": data.hasMortgage,
                "mortgageCount": data.mortgageCount,
                "resOrBuyToLet": data.resOrBuyToLet,
                "mortgageType": data.mortgageType,
                "mortgageAmount": data.mortgageAmount,
                "renewalDate": data.renewalDate,
            }
            # Append to mortgage_details array
            conn.user.mortgage_details.update_one(
                {"username": data.username},
                {"$push": {"mortgage_details": entry}}
            )
        else:
            entry = {
                "_id": ObjectId(),
                "isLookingForMortgage": data.isLookingForMortgage,
                "newMortgageAmount": data.newMortgageAmount,
                "ownershipType": data.ownershipType,
                "annualIncome": data.annualIncome,
                "depositeAmt": data.depositeAmt,
                "foundProperty": data.foundProperty,
            }
            # Append to new_mortgage_requests array
            conn.user.mortgage_details.update_one(
                {"username": data.username},
                {"$push": {"new_mortgage_requests": entry}}
            )
        
        return {"message": "Data added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Admin

def fetch_all_items(cursor):
    items = list(cursor)
    for item in items:
        item["id"] = str(item["_id"])
    return items

def serialize_mongo_document(document):
    if isinstance(document, list):
        return [serialize_mongo_document(doc) for doc in document]
    if isinstance(document, dict):
        document["id"] = str(document["_id"]) if "_id" in document else None
        del document["_id"]
        return {key: (str(value) if isinstance(value, ObjectId) else serialize_mongo_document(value)) for key, value in document.items()}
    return document


############################### MyClients.js #################################
@user.get("/users", response_model=List[AllUser])
async def get_all_users():
    users = conn.user.mortgage_details.find({})
    all_users = fetch_all_items(users)
    return serialize_mongo_document(all_users)


################################ COUNTS BEFORE #############################################
# @user.get("/counts")
# async def get_counts():
#     # Total entries count
#     total_count = conn.user.mortgage_details.count_documents({})

#     has_mortgage_count = conn.user.mortgage_details.count_documents({"hasMortgage": True})

#     is_looking_for_mortgage_count = conn.user.mortgage_details.count_documents({"isLookingForMortgage": True})

#     return {
#         "total_count": total_count,
#         "has_mortgage_count": has_mortgage_count,
#         "is_looking_for_mortgage_count": is_looking_for_mortgage_count,
#     }



def serialize_document(document):
    if isinstance(document, ObjectId):
        return str(document)
    elif isinstance(document, list):
        return [serialize_document(item) for item in document]
    elif isinstance(document, dict):
        return {key: serialize_document(value) for key, value in document.items()}
    else:
        return document

################################# UserDetails.js ##################################
# @user.get("/users/{userId}")
# async def get_user(userId: str):
#     try:
#         user_id = ObjectId(userId)
#         user = conn.user.mortgage_details.find_one({"_id": user_id})
#         if user is None:
#             raise HTTPException(status_code=404, detail="User not found")

#         user = serialize_document(user)
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid user ID")



############################### RESPONSE #################################### 
@user.get("/user/{username}")
async def get_user(username: str):
    try:
        user = conn.user.mortgage_details.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user = serialize_document(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid user ID")

############################### ADMIN LOGIN ####################################
@user.post("/admin/login", response_model=AdminToken)
async def login(login_data: LoginModel):
    admin = authenticate_admin(login_data.username, login_data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": login_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    admin_details = {
        "id": str(admin["_id"]),
        "username": admin["username"],
        "email": admin.get("email", ""),
        "name": admin.get("name", ""),
        "contactnumber": str(admin.get("contactnumber", "")),
    }
    return {"access_token": access_token, "token_type": "bearer", "admin_details": admin_details}


# @user.put("/user_update/{user_id}/")
# async def update_user(user_id: str, user_data: UserUpdate):
#     try:
#         update_data = {k: v for k, v in user_data.dict().items() if v is not None}

#         result = await conn.user.mortgage_details.update_one({"_id": user_id}, {"$set": update_data})
        
#         if result.matched_count == 0:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         updated_user = await conn.user.mortgage_details.find_one({"_id": user_id})
#         if updated_user:
#             updated_user["_id"] = str(updated_user["_id"])
#             return updated_user

#         raise HTTPException(status_code=404, detail="Updated user not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



###############################DELETE RESPONSE #######################################

@user.delete("/delete-response/{response_id}")
async def delete_response(response_id: str, type: str):
    collection = "mortgage_details" if type == "existing" else "new_mortgage_requests"
    result = conn.user.mortgage_details.update_one(
        {collection: {"$elemMatch": {"_id": ObjectId(response_id)}}},
        {"$pull": {collection: {"_id": ObjectId(response_id)}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Response not found")
    return {"message": "Response deleted successfully"}


################################ COUNTS AFTER #############################################

@user.get("/count_mortgages")
async def count_mortgages():
    has_mortgage_count = conn.user.mortgage_details.aggregate([
        {"$unwind": "$mortgage_details"},
        {"$match": {"mortgage_details.hasMortgage": True}},
        {"$count": "has_mortgage_count"}
    ])

    has_mortgage_count = list(has_mortgage_count)
    has_mortgage_count = has_mortgage_count[0]["has_mortgage_count"] if has_mortgage_count else 0

    # Count responses where isLookingForMortgage is true
    looking_for_mortgage_count = conn.user.mortgage_details.aggregate([
        {"$unwind": "$new_mortgage_requests"},
        {"$match": {"new_mortgage_requests.isLookingForMortgage": True}},
        {"$count": "looking_for_mortgage_count"}
    ])

    looking_for_mortgage_count = list(looking_for_mortgage_count)
    looking_for_mortgage_count = looking_for_mortgage_count[0]["looking_for_mortgage_count"] if looking_for_mortgage_count else 0

    total_count = conn.user.mortgage_details.count_documents({})
    return JSONResponse(content={
        "total_count": total_count,
        "has_mortgage_count": has_mortgage_count,
        "looking_for_mortgage_count": looking_for_mortgage_count
    })

########################## UPDATING DATA FROM ADMIN #############################

@user.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate):
    object_id = ObjectId(user_id)
    result = conn.user.mortgage_details.update_one(
        {"_id": object_id},
        {"$set": user_data.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}


@user.put("/update-mortgage/{user_id}")
async def update_mortgage(user_id: str, mortgage: ExistingMortgageDetails):
    user = conn.user.mortgage_details.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = conn.user.mortgage_details.update_one(
        {"_id": ObjectId(user_id), "mortgage_details.id": mortgage.mortgage_id},
        {
            "$set": {
                "mortgage_details.$.hasMortgage": mortgage.hasMortgage,
                "mortgage_details.$.mortgageType": mortgage.mortgageType,
                "mortgage_details.$.mortgageCount": mortgage.mortgageCount,
                "mortgage_details.$.mortgageAmount": mortgage.mortgageAmount,
                "mortgage_details.$.resOrBuyToLet": mortgage.resOrBuyToLet,
                "mortgage_details.$.renewalDate": mortgage.renewalDate,
            }
        },
    )

    if updated.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mortgage details not found")
    
    return {"message": "Mortgage details updated successfully"}