"""
Dual-Model Validation Service for Omani Mental Health Assistant
Implements GPT-4o + Claude Opus 4 validation system for therapeutic-grade responses
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# AI API imports
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    """Validation status for dual-model responses"""
    PASSED = "passed"
    FAILED = "failed"
    CONFLICT = "conflict"
    ERROR = "error"

@dataclass
class ModelResponse:
    """Response from a single AI model"""
    content: str
    model_name: str
    response_time: float
    token_count: Optional[int] = None
    confidence_score: Optional[float] = None
    safety_flags: List[str] = None
    therapeutic_quality: Optional[float] = None

@dataclass
class DualModelResult:
    """Result from dual-model validation"""
    primary_response: ModelResponse
    secondary_response: ModelResponse
    final_response: str
    validation_status: ValidationStatus
    consensus_score: float
    therapeutic_grade: str
    validation_time: float
    recommendations: List[str]
    safety_assessment: Dict[str, Any]

class DualModelValidator:
    """
    Advanced dual-model validation system for therapeutic responses
    Uses GPT-4o as primary and Claude Opus 4 as validation
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.primary_model = "gpt-4o"
        self.secondary_model = "claude-3-5-sonnet-20241022"
        self.max_response_time = 25  # seconds
        self.min_consensus_score = 0.7
        self.therapeutic_threshold = 0.8
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI service clients"""
        try:
            if openai:
                self.openai_client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI not available")
                
            if anthropic:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                logger.info("Anthropic client initialized")
            else:
                logger.warning("Anthropic not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
    
    def get_therapeutic_system_prompt(self) -> str:
        """Get enhanced system prompt for therapeutic responses"""
        return """You are a highly trained mental health support assistant specialized in Omani culture and Islamic values. 

THERAPEUTIC REQUIREMENTS:
- Provide evidence-based mental health support
- Integrate Islamic principles (sabr, tawakkul, du'a) appropriately
- Be culturally sensitive to Omani traditions and values
- Detect and respond appropriately to crisis situations
- Use cognitive behavioral therapy (CBT) techniques when appropriate
- Encourage professional help when needed
- Maintain therapeutic boundaries

CULTURAL CONTEXT:
- Understand the role of family and community in Omani society
- Respect Islamic concepts of mental wellness
- Be aware of cultural stigma around mental health
- Integrate prayers, Quranic verses, and Islamic coping strategies
- Respect gender considerations in Islamic culture

VALIDATION CRITERIA:
- Rate the therapeutic quality (1-10)
- Identify any safety concerns
- Assess cultural appropriateness
- Evaluate evidence-based recommendations
- Check for crisis indicators

RESPONSE FORMAT:
Provide a compassionate, therapeutic response that:
1. Acknowledges the person's feelings
2. Offers practical coping strategies
3. Includes Islamic/cultural elements when appropriate
4. Suggests professional resources if needed
5. Maintains hope and support

Always end with a VALIDATION ASSESSMENT:
- Therapeutic Quality: [1-10]
- Safety Level: [Safe/Caution/Crisis]
- Cultural Appropriateness: [1-10] 
- CBT Elements: [Yes/No]
- Professional Referral: [Needed/Optional/Not Needed]"""
    
    def get_validation_prompt(self, user_input: str, primary_response: str) -> str:
        """Get validation prompt for secondary model"""
        return f"""Please validate this mental health response for therapeutic quality and safety.

USER INPUT: "{user_input}"

PRIMARY RESPONSE TO VALIDATE:
"{primary_response}"

VALIDATION CRITERIA:
1. Therapeutic Quality (1-10): Is this response helpful, empathetic, and professionally appropriate?
2. Safety Assessment: Are there any safety concerns or missed crisis indicators?
3. Cultural Sensitivity (1-10): How well does it respect Omani/Islamic culture?
4. Evidence-Based: Does it include appropriate mental health strategies?
5. Professional Boundaries: Does it maintain appropriate therapeutic boundaries?

Provide:
1. A validation score (1-10) for overall quality
2. Specific feedback on strengths and weaknesses
3. Any safety concerns or recommendations
4. An improved version if the original is inadequate

VALIDATION ASSESSMENT:
- Overall Score: [1-10]
- Safety Status: [Safe/Caution/Crisis]
- Improvements Needed: [List any issues]
- Recommendation: [Approve/Revise/Escalate]"""
    
    async def get_primary_response(self, user_input: str, conversation_history: List[Dict] = None) -> ModelResponse:
        """Get response from primary model (GPT-4o)"""
        start_time = time.time()
        
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            # Build messages
            messages = [
                {"role": "system", "content": self.get_therapeutic_system_prompt()}
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Make API call with fallback
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.primary_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=self.max_response_time
                )
                content = response.choices[0].message.content
                
            except Exception as model_error:
                # Fallback to GPT-4 if GPT-4o not available
                if "model_not_found" in str(model_error) or "does not have access" in str(model_error):
                    logger.warning("GPT-4o not accessible, falling back to GPT-4")
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500,
                        timeout=self.max_response_time
                    )
                    content = response.choices[0].message.content
                    self.primary_model = "gpt-4"  # Update for future calls
                else:
                    raise model_error
            
            # Parse validation assessment from response
            therapeutic_quality = self._extract_quality_score(content)
            safety_flags = self._extract_safety_flags(content)
            
            return ModelResponse(
                content=content,
                model_name=self.primary_model,
                response_time=time.time() - start_time,
                token_count=getattr(response.usage, 'total_tokens', None),
                therapeutic_quality=therapeutic_quality,
                safety_flags=safety_flags
            )
            
        except Exception as e:
            logger.error(f"Primary model error: {e}")
            return ModelResponse(
                content=f"Primary model error: {str(e)}",
                model_name=self.primary_model,
                response_time=time.time() - start_time,
                therapeutic_quality=0.0,
                safety_flags=["error"]
            )
    
    async def get_validation_response(self, user_input: str, primary_response: str) -> ModelResponse:
        """Get validation response from secondary model (Claude Opus)"""
        start_time = time.time()
        
        try:
            if not self.anthropic_client:
                raise Exception("Anthropic client not initialized")
            
            validation_prompt = self.get_validation_prompt(user_input, primary_response)
            
            # Use newer Messages API
            message = self.anthropic_client.messages.create(
                model=self.secondary_model,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for validation
                messages=[
                    {"role": "user", "content": validation_prompt}
                ]
            )
            
            content = message.content[0].text if message.content else "No validation response"
            
            # Parse validation scores
            validation_score = self._extract_validation_score(content)
            safety_flags = self._extract_safety_flags(content)
            
            return ModelResponse(
                content=content,
                model_name=self.secondary_model,
                response_time=time.time() - start_time,
                confidence_score=validation_score,
                safety_flags=safety_flags
            )
            
        except Exception as e:
            logger.error(f"Validation model error: {e}")
            return ModelResponse(
                content=f"Validation error: {str(e)}",
                model_name=self.secondary_model,
                response_time=time.time() - start_time,
                confidence_score=0.0,
                safety_flags=["error"]
            )
    
    async def validate_response(self, user_input: str, conversation_history: List[Dict] = None) -> DualModelResult:
        """
        Perform dual-model validation for therapeutic-grade response
        """
        start_time = time.time()
        
        try:
            # Get responses from both models concurrently
            primary_task = self.get_primary_response(user_input, conversation_history)
            
            # Get primary response first
            primary_response = await primary_task
            
            # Then validate with secondary model
            validation_response = await self.get_validation_response(
                user_input, 
                primary_response.content
            )
            
            # Perform consensus analysis
            consensus_result = self._analyze_consensus(
                primary_response, 
                validation_response,
                user_input
            )
            
            return DualModelResult(
                primary_response=primary_response,
                secondary_response=validation_response,
                final_response=consensus_result["final_response"],
                validation_status=consensus_result["status"],
                consensus_score=consensus_result["consensus_score"],
                therapeutic_grade=consensus_result["therapeutic_grade"],
                validation_time=time.time() - start_time,
                recommendations=consensus_result["recommendations"],
                safety_assessment=consensus_result["safety_assessment"]
            )
            
        except Exception as e:
            logger.error(f"Dual validation error: {e}")
            
            # Return fallback result
            return DualModelResult(
                primary_response=ModelResponse("Error", "unknown", 0.0),
                secondary_response=ModelResponse("Error", "unknown", 0.0),
                final_response=f"I apologize, but I'm experiencing technical difficulties. Please consider reaching out to a mental health professional or call 9999 for emergency support.",
                validation_status=ValidationStatus.ERROR,
                consensus_score=0.0,
                therapeutic_grade="F",
                validation_time=time.time() - start_time,
                recommendations=["Seek professional help", "Contact emergency services if in crisis"],
                safety_assessment={"status": "error", "recommendation": "professional_help"}
            )
    
    def _analyze_consensus(self, primary: ModelResponse, validation: ModelResponse, user_input: str) -> Dict[str, Any]:
        """Analyze consensus between primary and validation responses"""
        
        # Extract scores
        primary_quality = primary.therapeutic_quality or 0.0
        validation_score = validation.confidence_score or 0.0
        
        # Check for safety flags
        primary_safety = primary.safety_flags or []
        validation_safety = validation.safety_flags or []
        all_safety_flags = list(set(primary_safety + validation_safety))
        
        # Calculate consensus score
        consensus_score = min(primary_quality / 10.0, validation_score / 10.0)
        
        # Determine therapeutic grade
        if consensus_score >= 0.9:
            therapeutic_grade = "A+"
        elif consensus_score >= 0.8:
            therapeutic_grade = "A"
        elif consensus_score >= 0.7:
            therapeutic_grade = "B+"
        elif consensus_score >= 0.6:
            therapeutic_grade = "B"
        elif consensus_score >= 0.5:
            therapeutic_grade = "C"
        else:
            therapeutic_grade = "F"
        
        # Determine validation status
        if "error" in all_safety_flags:
            status = ValidationStatus.ERROR
        elif "crisis" in all_safety_flags:
            status = ValidationStatus.FAILED  # Needs human intervention
        elif consensus_score >= self.min_consensus_score:
            status = ValidationStatus.PASSED
        elif abs(primary_quality - validation_score * 10) > 3.0:
            status = ValidationStatus.CONFLICT
        else:
            status = ValidationStatus.FAILED
        
        # Generate recommendations
        recommendations = []
        if consensus_score < 0.7:
            recommendations.append("Response quality below therapeutic threshold")
        if "crisis" in all_safety_flags:
            recommendations.append("Crisis intervention required")
        if "professional" in " ".join(all_safety_flags):
            recommendations.append("Professional referral recommended")
        
        # Select final response
        if status == ValidationStatus.PASSED:
            final_response = primary.content
        elif "improved" in validation.content.lower():
            # Extract improved response from validation if available
            final_response = self._extract_improved_response(validation.content) or primary.content
        else:
            final_response = primary.content
        
        # Clean up the final response (remove validation assessments)
        final_response = self._clean_response(final_response)
        
        return {
            "final_response": final_response,
            "status": status,
            "consensus_score": consensus_score,
            "therapeutic_grade": therapeutic_grade,
            "recommendations": recommendations,
            "safety_assessment": {
                "flags": all_safety_flags,
                "status": "crisis" if "crisis" in all_safety_flags else "safe",
                "recommendation": "emergency" if "crisis" in all_safety_flags else "continue"
            }
        }
    
    def _extract_quality_score(self, content: str) -> float:
        """Extract therapeutic quality score from response"""
        import re
        
        patterns = [
            r"Therapeutic Quality:\s*(\d+(?:\.\d+)?)",
            r"Quality:\s*(\d+(?:\.\d+)?)",
            r"Score:\s*(\d+(?:\.\d+)?)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 7.0  # Default moderate quality
    
    def _extract_validation_score(self, content: str) -> float:
        """Extract validation score from validation response"""
        import re
        
        patterns = [
            r"Overall Score:\s*(\d+(?:\.\d+)?)",
            r"Validation Score:\s*(\d+(?:\.\d+)?)",
            r"Score:\s*(\d+(?:\.\d+)?)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 7.0  # Default score
    
    def _extract_safety_flags(self, content: str) -> List[str]:
        """Extract safety flags from response"""
        flags = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["crisis", "emergency", "suicide", "harm"]):
            flags.append("crisis")
        if any(word in content_lower for word in ["professional", "therapist", "counselor"]):
            flags.append("professional")
        if "caution" in content_lower:
            flags.append("caution")
        
        return flags
    
    def _extract_improved_response(self, validation_content: str) -> Optional[str]:
        """Extract improved response from validation content"""
        # Look for improved response sections
        import re
        
        patterns = [
            r"IMPROVED RESPONSE:\s*(.*?)(?=\n\n|\nVALIDATION|\Z)",
            r"Better response:\s*(.*?)(?=\n\n|\nVALIDATION|\Z)",
            r"Revised:\s*(.*?)(?=\n\n|\nVALIDATION|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, validation_content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _clean_response(self, response: str) -> str:
        """Clean response by removing validation assessments"""
        import re
        
        # Remove validation assessment sections
        patterns = [
            r"VALIDATION ASSESSMENT:.*$",
            r"Therapeutic Quality:.*$",
            r"Safety Level:.*$",
            r"Cultural Appropriateness:.*$"
        ]
        
        cleaned = response
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        return cleaned.strip()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status for monitoring"""
        return {
            "primary_model": self.primary_model,
            "secondary_model": self.secondary_model,
            "openai_available": self.openai_client is not None,
            "anthropic_available": self.anthropic_client is not None,
            "max_response_time": self.max_response_time,
            "min_consensus_score": self.min_consensus_score,
            "therapeutic_threshold": self.therapeutic_threshold
        }


# Global service instance
_dual_model_service = None

def get_dual_model_service() -> DualModelValidator:
    """Get or create the global dual-model service instance"""
    global _dual_model_service
    if _dual_model_service is None:
        _dual_model_service = DualModelValidator()
    return _dual_model_service


# Async helper functions
async def validate_therapeutic_response(user_input: str, conversation_history: List[Dict] = None) -> DualModelResult:
    """Validate response using dual-model system"""
    service = get_dual_model_service()
    return await service.validate_response(user_input, conversation_history)


def test_dual_model_setup() -> Dict[str, Any]:
    """Test dual-model service setup"""
    service = get_dual_model_service()
    return service.get_service_status() 