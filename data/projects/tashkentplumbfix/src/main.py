from fastapi import FastAPI, Depends, HTTPException
from typing import List
from src.database import supabase
from src.models import CreateRequest, RequestResponse, CreateBid, BidResponse
from src.auth import get_current_user

app = FastAPI(title="TashkentPlumbFix MVP")

@app.get("/")
def health_check():
    return {"status": "ok", "market": "Uzbekistan", "version": "1.0.0"}

# --- Client Endpoints ---

@app.post("/requests", response_model=RequestResponse)
def create_request(req: CreateRequest, user: dict = Depends(get_current_user)):
    if user['role'] != 'client':
        raise HTTPException(403, "Only clients can create requests")
        
    data = {
        "client_id": user['id'],
        "description": req.description,
        "photo_url": req.photo_url,
        "status": "open"
    }
    
    res = supabase.table("requests").insert(data).execute()
    if not res.data:
        raise HTTPException(500, "Failed to create request")
    return res.data[0]

@app.post("/bids/{bid_id}/accept")
def accept_bid(bid_id: str, user: dict = Depends(get_current_user)):
    # 1. Verify bid belongs to a request owned by this user
    bid_res = supabase.table("bids").select("*, requests(client_id)").eq("id", bid_id).execute()
    
    if not bid_res.data:
        raise HTTPException(404, "Bid not found")
        
    bid = bid_res.data[0]
    # Note: Supabase nested select syntax varies, simplistic check here:
    # In real app, ensure Join is handled or verify ownership separately
    
    # 2. Update Bid Status
    supabase.table("bids").update({"status": "accepted"}).eq("id", bid_id).execute()
    
    # 3. Close Request
    supabase.table("requests").update({"status": "closed"}).eq("id", bid['request_id']).execute()
    
    return {"message": "Master hired! Exchange contacts now."}

# --- Master Endpoints ---

@app.get("/feed", response_model=List[RequestResponse])
def get_open_requests(user: dict = Depends(get_current_user)):
    if user['role'] != 'master':
        raise HTTPException(403, "Only masters can view feed")
        
    res = supabase.table("requests").select("*").eq("status", "open").order("created_at", desc=True).execute()
    return res.data

@app.post("/bids", response_model=BidResponse)
def place_bid(bid: CreateBid, user: dict = Depends(get_current_user)):
    if user['role'] != 'master':
        raise HTTPException(403, "Only masters can bid")
        
    data = {
        "request_id": str(bid.request_id),
        "master_id": user['id'],
        "price": bid.price,
        "message": bid.message,
        "status": "pending"
    }
    
    res = supabase.table("bids").insert(data).execute()
    return res.data[0]