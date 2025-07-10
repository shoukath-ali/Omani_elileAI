"""
Real-time WebSocket Service for Voice-Based Mental Health Assistant
Handles real-time audio streaming and processing with <20s latency target
"""
import asyncio
import websockets
import json
import logging
import time
from typing import Dict, Any, Optional, Callable
import base64
from pathlib import Path

from voice_service import get_voice_service, process_speech_input, generate_speech_output
from chatbot import OmaniMentalHealthChatbot

logger = logging.getLogger(__name__)

class VoiceWebSocketServer:
    """WebSocket server for real-time voice communication"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.voice_service = get_voice_service()
        self.chatbot = OmaniMentalHealthChatbot()
        self.max_latency = 20  # seconds
        self.active_sessions = {}
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        session_id = f"session_{int(time.time())}_{len(self.clients)}"
        self.active_sessions[websocket] = {
            "session_id": session_id,
            "start_time": time.time(),
            "message_count": 0,
            "total_latency": 0,
            "language": "ar-OM"
        }
        
        logger.info(f"Client registered: {session_id}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "connection_established",
                "session_id": session_id,
                "message": "مرحباً بك في المساعد النفسي العماني الصوتي",
                "status": "ready",
                "voice_enabled": True
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Handle client messages
            await self.handle_client_messages(websocket)
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {session_id}")
        except Exception as e:
            logger.error(f"Error handling client {session_id}: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        if websocket in self.active_sessions:
            session = self.active_sessions[websocket]
            logger.info(f"Session ended: {session['session_id']}, "
                       f"Messages: {session['message_count']}, "
                       f"Avg latency: {session['total_latency']/max(session['message_count'], 1):.2f}s")
            del self.active_sessions[websocket]
    
    async def handle_client_messages(self, websocket):
        """Handle incoming messages from WebSocket clients"""
        session = self.active_sessions[websocket]
        
        async for message in websocket:
            try:
                start_time = time.time()
                data = json.loads(message)
                message_type = data.get("type")
                
                session["message_count"] += 1
                
                if message_type == "voice_input":
                    await self.handle_voice_input(websocket, data, start_time)
                elif message_type == "text_input":
                    await self.handle_text_input(websocket, data, start_time)
                elif message_type == "ping":
                    await self.handle_ping(websocket, data)
                elif message_type == "config_update":
                    await self.handle_config_update(websocket, data)
                else:
                    await self.send_error(websocket, f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                await self.send_error(websocket, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await self.send_error(websocket, f"Processing error: {str(e)}")
    
    async def handle_voice_input(self, websocket, data, start_time):
        """Handle voice input from client"""
        try:
            # Extract audio data
            audio_data_b64 = data.get("audio_data")
            if not audio_data_b64:
                await self.send_error(websocket, "No audio data provided")
                return
            
            # Decode base64 audio
            audio_data = base64.b64decode(audio_data_b64)
            
            # Send processing status
            await websocket.send(json.dumps({
                "type": "processing_status",
                "status": "transcribing",
                "message": "جاري معالجة الصوت..."
            }))
            
            # Convert speech to text
            stt_result = await process_speech_input(audio_data)
            
            if not stt_result["success"]:
                await self.send_error(websocket, f"Speech recognition failed: {stt_result.get('error', 'Unknown error')}")
                return
            
            user_text = stt_result["text"]
            if not user_text.strip():
                await self.send_error(websocket, "No speech detected")
                return
            
            # Send transcription result
            await websocket.send(json.dumps({
                "type": "transcription",
                "text": user_text,
                "confidence": stt_result.get("confidence", 0.0),
                "language": stt_result.get("language", "ar-OM")
            }))
            
            # Process with chatbot
            await self.send_processing_status(websocket, "thinking", "جاري التفكير...")
            
            # Get chatbot response
            response = await asyncio.to_thread(
                self.chatbot.get_response, 
                user_text, 
                conversation_id=self.active_sessions[websocket]["session_id"]
            )
            
            # Convert response to speech
            await self.send_processing_status(websocket, "synthesizing", "جاري تحويل الرد إلى صوت...")
            
            tts_result = await generate_speech_output(response["response"])
            
            if not tts_result["success"]:
                # Send text response as fallback
                await self.send_text_response(websocket, response, start_time)
                return
            
            # Encode audio data
            audio_response_b64 = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
            
            # Calculate total latency
            total_latency = time.time() - start_time
            self.active_sessions[websocket]["total_latency"] += total_latency
            
            # Send voice response
            response_data = {
                "type": "voice_response",
                "text": response["response"],
                "audio_data": audio_response_b64,
                "latency": total_latency,
                "crisis_detected": response.get("crisis_detected", False),
                "safety_info": response.get("safety_info", {}),
                "processing_time": {
                    "stt_time": stt_result.get("duration", 0),
                    "chatbot_time": response.get("response_time", 0),
                    "tts_time": tts_result.get("duration", 0),
                    "total_time": total_latency
                }
            }
            
            await websocket.send(json.dumps(response_data))
            
            # Log performance
            if total_latency > self.max_latency:
                logger.warning(f"High latency detected: {total_latency:.2f}s > {self.max_latency}s")
            
            logger.info(f"Voice interaction completed in {total_latency:.2f}s")
            
        except Exception as e:
            logger.error(f"Voice input processing error: {e}")
            await self.send_error(websocket, f"Voice processing failed: {str(e)}")
    
    async def handle_text_input(self, websocket, data, start_time):
        """Handle text input from client (fallback mode)"""
        try:
            user_text = data.get("text", "").strip()
            if not user_text:
                await self.send_error(websocket, "Empty text input")
                return
            
            # Process with chatbot
            await self.send_processing_status(websocket, "thinking", "جاري التفكير...")
            
            response = await asyncio.to_thread(
                self.chatbot.get_response, 
                user_text, 
                conversation_id=self.active_sessions[websocket]["session_id"]
            )
            
            await self.send_text_response(websocket, response, start_time)
            
        except Exception as e:
            logger.error(f"Text input processing error: {e}")
            await self.send_error(websocket, f"Text processing failed: {str(e)}")
    
    async def send_text_response(self, websocket, response, start_time):
        """Send text-only response"""
        total_latency = time.time() - start_time
        self.active_sessions[websocket]["total_latency"] += total_latency
        
        response_data = {
            "type": "text_response",
            "text": response["response"],
            "latency": total_latency,
            "crisis_detected": response.get("crisis_detected", False),
            "safety_info": response.get("safety_info", {}),
            "fallback_mode": True
        }
        
        await websocket.send(json.dumps(response_data))
    
    async def send_processing_status(self, websocket, status, message):
        """Send processing status update"""
        await websocket.send(json.dumps({
            "type": "processing_status",
            "status": status,
            "message": message
        }))
    
    async def handle_ping(self, websocket, data):
        """Handle ping/keep-alive messages"""
        await websocket.send(json.dumps({
            "type": "pong",
            "timestamp": time.time(),
            "session_id": self.active_sessions[websocket]["session_id"]
        }))
    
    async def handle_config_update(self, websocket, data):
        """Handle configuration updates"""
        session = self.active_sessions[websocket]
        
        if "language" in data:
            session["language"] = data["language"]
            logger.info(f"Language updated to {data['language']} for session {session['session_id']}")
        
        await websocket.send(json.dumps({
            "type": "config_updated",
            "session_id": session["session_id"],
            "current_config": {
                "language": session["language"]
            }
        }))
    
    async def send_error(self, websocket, error_message):
        """Send error message to client"""
        await websocket.send(json.dumps({
            "type": "error",
            "error": error_message,
            "timestamp": time.time()
        }))
    
    async def broadcast_message(self, message):
        """Broadcast message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients.copy()],
                return_exceptions=True
            )
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.register_client, self.host, self.port):
            logger.info(f"WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        total_messages = sum(session["message_count"] for session in self.active_sessions.values())
        total_latency = sum(session["total_latency"] for session in self.active_sessions.values())
        avg_latency = total_latency / max(total_messages, 1)
        
        return {
            "active_clients": len(self.clients),
            "total_sessions": len(self.active_sessions),
            "total_messages": total_messages,
            "average_latency": avg_latency,
            "max_latency_threshold": self.max_latency,
            "server_uptime": time.time() - getattr(self, '_start_time', time.time())
        }


# Standalone WebSocket server runner
async def run_websocket_server(host="localhost", port=8765):
    """Run the WebSocket server"""
    server = VoiceWebSocketServer(host, port)
    server._start_time = time.time()
    await server.start_server()


if __name__ == "__main__":
    # Run WebSocket server
    import os
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", "8765"))
    
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_websocket_server(host, port)) 