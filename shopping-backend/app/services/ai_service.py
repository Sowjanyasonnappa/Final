"""
AI Service - OpenAI integration for RCA, log analysis, and recommendations
"""
import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from openai import OpenAI
from sqlalchemy.orm import Session

from app.database import alert_model

logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


class AIService:
    """Service for AI-powered analysis and recommendations"""
    
    def __init__(self):
        if not client:
            logger.warning("OpenAI API key not configured. AI features will be limited.")
    
    def generate_root_cause_analysis(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate root cause analysis for an incident"""
        if not client:
            return {"error": "OpenAI API not configured"}
        
        try:
            prompt = self._build_rca_prompt(incident_data)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes expert analyzing incidents and outages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response into structured format
            analysis = self._parse_rca_response(analysis_text)
            
            return {
                "success": True,
                "root_cause_analysis": analysis,
                "confidence": 0.85,
                "model": "gpt-4"
            }
        except Exception as e:
            logger.error(f"Error generating RCA: {e}")
            return {"error": str(e)}
    
    def analyze_logs(self, logs: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze logs and generate summary"""
        if not client:
            return {"error": "OpenAI API not configured"}
        
        try:
            prompt = self._build_log_analysis_prompt(logs, context)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes log analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "success": True,
                "summary": analysis_text,
                "model": "gpt-4"
            }
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {"error": str(e)}
    
    def generate_alert_suggestions(self, alert_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent alert messages and suggested actions"""
        if not client:
            return {"error": "OpenAI API not configured"}
        
        try:
            prompt = self._build_alert_suggestion_prompt(alert_context)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes monitoring expert generating alert messages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            suggestion_text = response.choices[0].message.content
            
            return {
                "success": True,
                "suggestion": suggestion_text,
                "model": "gpt-3.5-turbo"
            }
        except Exception as e:
            logger.error(f"Error generating alert suggestions: {e}")
            return {"error": str(e)}
    
    def recommend_products(self, user_history: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate AI product recommendations based on user history"""
        if not client:
            return []
        
        try:
            prompt = self._build_product_recommendation_prompt(user_history)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an e-commerce product recommendation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            recommendation_text = response.choices[0].message.content
            
            # Parse recommendations and fetch from DB
            recommendations = self._parse_product_recommendations(recommendation_text, db)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating product recommendations: {e}")
            return []
    
    def answer_operational_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer operational questions about Kubernetes"""
        if not client:
            return "AI service not available"
        
        try:
            prompt = self._build_question_answer_prompt(question, context)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes operations expert. Provide clear, actionable answers about Kubernetes issues and operations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Error: {str(e)}"
    
    def suggest_kubectl_commands(self, scenario: Dict[str, Any]) -> List[str]:
        """Suggest kubectl commands for a given scenario"""
        if not client:
            return []
        
        try:
            prompt = self._build_kubectl_suggestion_prompt(scenario)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a kubectl expert. Provide practical kubectl commands as a JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                commands = json.loads(response_text)
                return commands if isinstance(commands, list) else [response_text]
            except:
                return [response_text]
        except Exception as e:
            logger.error(f"Error suggesting kubectl commands: {e}")
            return []
    
    def suggest_yaml_fixes(self, yaml_content: str, error_message: str) -> str:
        """Suggest fixes for YAML manifests"""
        if not client:
            return "AI service not available"
        
        try:
            prompt = f"""
I have a Kubernetes YAML manifest that's causing an error. Please analyze it and suggest fixes.

YAML:
{yaml_content}

Error:
{error_message}

Please provide:
1. Root cause of the error
2. Suggested corrections to the YAML
3. Explanation of the changes
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes YAML expert. Help fix manifest errors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error suggesting YAML fixes: {e}")
            return f"Error: {str(e)}"
    
    def suggest_scaling(self, deployment_data: Dict[str, Any]) -> str:
        """Suggest scaling parameters for a deployment"""
        if not client:
            return "AI service not available"
        
        try:
            prompt = self._build_scaling_suggestion_prompt(deployment_data)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Kubernetes scaling expert. Provide recommendations for horizontal pod autoscaling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error suggesting scaling: {e}")
            return f"Error: {str(e)}"
    
    # Helper methods for building prompts
    
    @staticmethod
    def _build_rca_prompt(incident_data: Dict[str, Any]) -> str:
        """Build prompt for RCA generation"""
        return f"""
Analyze the following incident and provide a comprehensive root cause analysis:

Incident:
- Title: {incident_data.get('title')}
- Description: {incident_data.get('description')}
- Pod: {incident_data.get('pod_name')}
- Namespace: {incident_data.get('namespace')}
- Time: {incident_data.get('timestamp')}

Logs:
{incident_data.get('logs', 'No logs available')}

Metrics at time of incident:
- CPU Usage: {incident_data.get('cpu_usage')}
- Memory Usage: {incident_data.get('memory_usage')}
- Restart Count: {incident_data.get('restart_count')}

Please provide:
1. Root Cause
2. Contributing Factors
3. Timeline of Events
4. Suggested Fixes
5. Preventive Measures
        """
    
    @staticmethod
    def _build_log_analysis_prompt(logs: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for log analysis"""
        context_str = ""
        if context:
            context_str = f"""
Context:
- Pod: {context.get('pod_name')}
- Namespace: {context.get('namespace')}
- Deployment: {context.get('deployment_name')}
            """
        
        return f"""
Analyze the following logs and provide insights:

{context_str}

Logs:
{logs}

Please provide:
1. Summary of events
2. Error patterns identified
3. Potential issues
4. Recommended actions
        """
    
    @staticmethod
    def _build_alert_suggestion_prompt(alert_context: Dict[str, Any]) -> str:
        """Build prompt for alert suggestions"""
        return f"""
Generate a helpful alert message and suggested actions:

Alert Type: {alert_context.get('alert_type')}
Value: {alert_context.get('value')}
Threshold: {alert_context.get('threshold')}
Resource: {alert_context.get('resource')}
Namespace: {alert_context.get('namespace')}

Please provide:
1. Clear alert message
2. Why this alert occurred
3. Immediate actions to take
4. Long-term solutions
        """
    
    @staticmethod
    def _build_product_recommendation_prompt(user_history: Dict[str, Any]) -> str:
        """Build prompt for product recommendations"""
        return f"""
Based on the user's purchase and browsing history, recommend similar products:

Recent Purchases: {user_history.get('purchases', [])}
Recently Viewed: {user_history.get('viewed', [])}
Wishlist: {user_history.get('wishlist', [])}

Please recommend product categories and types that would interest this user.
        """
    
    @staticmethod
    def _build_question_answer_prompt(question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for answering operational questions"""
        context_str = ""
        if context:
            context_str = f"""
Context: {context}
            """
        
        return f"""
Answer the following Kubernetes operations question:

{context_str}

Question: {question}

Provide a clear, practical answer with examples if applicable.
        """
    
    @staticmethod
    def _build_kubectl_suggestion_prompt(scenario: Dict[str, Any]) -> str:
        """Build prompt for kubectl command suggestions"""
        return f"""
Suggest kubectl commands for the following scenario:

Scenario: {scenario.get('description')}
Namespace: {scenario.get('namespace')}
Resource Type: {scenario.get('resource_type')}

Provide as a JSON array of command strings.
        """
    
    @staticmethod
    def _build_scaling_suggestion_prompt(deployment_data: Dict[str, Any]) -> str:
        """Build prompt for scaling suggestions"""
        return f"""
Provide scaling recommendations for the following deployment:

Deployment: {deployment_data.get('name')}
Current Replicas: {deployment_data.get('current_replicas')}
Average CPU: {deployment_data.get('avg_cpu')}
Average Memory: {deployment_data.get('avg_memory')}
Peak CPU: {deployment_data.get('peak_cpu')}
Peak Memory: {deployment_data.get('peak_memory')}

Please recommend:
1. Appropriate replica count
2. Horizontal Pod Autoscaler settings
3. Resource requests and limits
        """
    
    @staticmethod
    def _parse_rca_response(response_text: str) -> Dict[str, str]:
        """Parse RCA response from AI"""
        # Simple parsing - can be enhanced
        sections = response_text.split('\n\n')
        return {
            "root_cause": response_text,
            "summary": sections[0] if sections else response_text
        }
    
    @staticmethod
    def _parse_product_recommendations(recommendation_text: str, db: Session) -> List[Dict[str, Any]]:
        """Parse product recommendations from AI response"""
        # This would fetch actual products from database based on AI recommendations
        # For now, return empty list
        return []
