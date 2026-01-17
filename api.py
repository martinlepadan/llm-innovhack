#!/usr/bin/env python3
"""
Instagram Coach Agent - REST API

FastAPI-based REST API for the Instagram Coach AI Assistant.
Provides endpoints for chat, streaming responses, and agent modes.

Usage:
    uvicorn api:app --reload --port 8000
    
Or run directly:
    python api.py
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import InstagramCoachAgent
from agent_modes import AgentMode, get_mode_description, list_modes, generate_with_mode

# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="Instagram Coach AI API",
    description="AI-powered Instagram coaching assistant with multiple expertise modes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - allow all origins for development
# In production, replace with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (initialized on startup)
agent: InstagramCoachAgent = None


# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================

class ModeEnum(str, Enum):
    """Available agent modes."""
    CONTENT_ANALYST = "content_analyst"
    MONETIZATION = "monetization"
    STRATEGY = "strategy"
    AUDIENCE = "audience"


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    question: str = Field(..., description="The question to ask the AI assistant")
    mode: Optional[ModeEnum] = Field(
        default=ModeEnum.CONTENT_ANALYST,
        description="Agent mode to use for the response"
    )
    n_posts: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant posts to retrieve for context"
    )
    temperature: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="LLM temperature (creativity level)"
    )
    max_tokens: Optional[int] = Field(
        default=1000,
        ge=100,
        le=4000,
        description="Maximum response length in tokens"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quels sont mes posts les plus performants ?",
                "mode": "content_analyst",
                "n_posts": 3,
                "temperature": 0.5,
                "max_tokens": 1000
            }
        }


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    response: str = Field(..., description="AI assistant's response")
    mode: str = Field(..., description="Agent mode used")
    mode_description: str = Field(..., description="Description of the mode used")
    question: str = Field(..., description="Original question")
    relevant_posts_count: int = Field(..., description="Number of posts used for context")


class ModeInfo(BaseModel):
    """Information about an agent mode."""
    mode: str = Field(..., description="Mode identifier")
    description: str = Field(..., description="Mode description")


class StatsResponse(BaseModel):
    """Response body for stats endpoint."""
    username: str
    followers: int
    avg_engagement_rate: float
    niche: str
    total_posts_indexed: int


class HealthResponse(BaseModel):
    """Response body for health check."""
    status: str
    agent_initialized: bool
    message: str


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the agent when the API starts."""
    global agent
    try:
        print("\n🚀 Initializing Instagram Coach Agent...")
        agent = InstagramCoachAgent(auto_load_data=True)
        print("✅ Agent initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("   The API will start but some endpoints may not work.\n")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Instagram Coach AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "POST /api/chat",
            "chat_stream": "POST /api/chat/stream",
            "modes": "GET /api/modes",
            "stats": "GET /api/stats"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if agent else "degraded",
        agent_initialized=agent is not None,
        message="Agent is ready" if agent else "Agent not initialized"
    )


@app.get("/api/modes", response_model=List[ModeInfo], tags=["Agent"])
async def get_modes():
    """Get all available agent modes."""
    return [ModeInfo(**mode) for mode in list_modes()]


@app.get("/api/stats", response_model=StatsResponse, tags=["Agent"])
async def get_stats():
    """Get Instagram account statistics."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    stats = agent.get_stats()
    profile = stats.get("profile", {})
    
    return StatsResponse(
        username=profile.get("username", "N/A"),
        followers=profile.get("followers", 0),
        avg_engagement_rate=profile.get("avg_engagement_rate", 0.0),
        niche=profile.get("niche", "N/A"),
        total_posts_indexed=stats.get("total_posts", 0)
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a message to the AI assistant and get a response.
    
    This is the main endpoint for interacting with the Instagram Coach.
    The response is returned as a complete message (non-streaming).
    
    **Modes available:**
    - `content_analyst`: Analyzes post performance
    - `monetization`: Advice on partnerships and revenue
    - `strategy`: Content planning and creation ideas
    - `audience`: Audience analysis and insights
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Convert string mode to AgentMode enum
        mode_mapping = {
            "content_analyst": AgentMode.CONTENT_ANALYST,
            "monetization": AgentMode.MONETIZATION,
            "strategy": AgentMode.STRATEGY,
            "audience": AgentMode.AUDIENCE,
        }
        
        selected_mode = mode_mapping.get(request.mode.value, AgentMode.CONTENT_ANALYST)
        
        # Generate response without streaming for API
        result = generate_with_mode(
            rag_pipeline=agent.rag_pipeline,
            question=request.question,
            mode=selected_mode,
            n_results=request.n_posts,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        
        return ChatResponse(
            response=result["response"],
            mode=result["mode"],
            mode_description=result["mode_description"],
            question=result["question"],
            relevant_posts_count=len(result["relevant_posts"])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Send a message to the AI assistant and get a streaming response.
    
    This endpoint returns a Server-Sent Events (SSE) stream for real-time
    response delivery. Use this for better user experience with longer responses.
    
    **Response Format:**
    Each chunk is sent as a text fragment that can be appended to build
    the complete response.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Convert string mode to AgentMode enum
        mode_mapping = {
            "content_analyst": AgentMode.CONTENT_ANALYST,
            "monetization": AgentMode.MONETIZATION,
            "strategy": AgentMode.STRATEGY,
            "audience": AgentMode.AUDIENCE,
        }
        
        selected_mode = mode_mapping.get(request.mode.value, AgentMode.CONTENT_ANALYST)
        
        # Generate streaming response
        result = generate_with_mode(
            rag_pipeline=agent.rag_pipeline,
            question=request.question,
            mode=selected_mode,
            n_results=request.n_posts,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        
        async def generate():
            """Async generator for streaming response."""
            try:
                for chunk in result["response_stream"]:
                    yield chunk
            except Exception as e:
                yield f"\n\n[Error: {str(e)}]"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.post("/api/recommendations/{focus}", tags=["Recommendations"])
async def get_recommendations(focus: str = "general"):
    """
    Get personalized recommendations based on focus area.
    
    **Focus areas:**
    - `general`: Overall Instagram improvement tips
    - `content`: Content optimization advice
    - `growth`: Growth acceleration strategies
    - `engagement`: Engagement rate improvement
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    valid_focus = ["general", "content", "growth", "engagement"]
    if focus not in valid_focus:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid focus. Must be one of: {', '.join(valid_focus)}"
        )
    
    questions = {
        "general": "Quelles sont tes recommandations principales pour améliorer mon Instagram ?",
        "content": "Comment puis-je optimiser mon contenu ?",
        "growth": "Quelles stratégies pour accélérer ma croissance ?",
        "engagement": "Comment augmenter mon taux d'engagement ?",
    }
    
    try:
        result = generate_with_mode(
            rag_pipeline=agent.rag_pipeline,
            question=questions[focus],
            mode=AgentMode.STRATEGY,
            n_results=3,
            stream=False,
        )
        
        return {
            "focus": focus,
            "recommendation": result["response"],
            "mode": result["mode"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.get("/api/top-posts", tags=["Analytics"])
async def get_top_posts(n: int = 3):
    """
    Get analysis of top performing posts.
    
    **Parameters:**
    - `n`: Number of top posts to analyze (1-10)
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if n < 1 or n > 10:
        raise HTTPException(status_code=400, detail="n must be between 1 and 10")
    
    try:
        question = f"Quels sont mes {n} posts les plus performants et pourquoi ?"
        
        result = generate_with_mode(
            rag_pipeline=agent.rag_pipeline,
            question=question,
            mode=AgentMode.CONTENT_ANALYST,
            n_results=n,
            stream=False,
        )
        
        return {
            "analysis": result["response"],
            "posts_analyzed": len(result["relevant_posts"]),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing posts: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting Instagram Coach AI API Server")
    print("=" * 60)
    print("\n📖 API Documentation: http://localhost:8000/docs")
    print("📊 Alternative Docs:  http://localhost:8000/redoc")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
