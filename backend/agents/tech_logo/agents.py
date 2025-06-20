from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import base64
from datetime import datetime
import os
from agents.tech_logo.state import LogoDesignState
from llms.openai import OpenAIProvider
from llms.logo import ReplicateProvider
import asyncio


class LogoDesignAgents:
    def __init__(self):
        self.provider = OpenAIProvider()
        self.llm = self.provider.client
        self.vision_llm = OpenAIProvider(model="gpt-4-vision-preview").client
        self.replicate_provider = ReplicateProvider()
        
    def chat_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Conducts initial consultation with user"""
        
        system_prompt = """You are Alex, a senior brand consultant specializing in logo design for tech companies.
        Your goal is to gather ALL essential information for logo design in a focused, efficient conversation.
        
        Ask strategic questions to understand:
        1. Company name, industry, and core business
        2. Target audience and brand personality
        3. Design preferences and style direction
        4. Technical requirements and applications
        5. Competitive context and differentiation goals
        
        Keep the conversation professional, short but efficient. Once you have comprehensive information, 
        summarize what you've learned and confirm with the user before concluding. Ask as less questions as possible. Do not respond with 
        Large texts. It should not feel like a headache to user"""
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in state.get("conversation_history", []):
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
        
        # Add current user input
        if state["user_input"]:
            messages.append(HumanMessage(content=state["user_input"]))
        
        response = self.llm.invoke(messages)
        
        # Update conversation history
        conversation_history = state.get("conversation_history", [])
        conversation_history.extend([
            {"role": "user", "content": state["user_input"]},
            {"role": "assistant", "content": response.content}
        ])
        
        recent_user_msg = state["user_input"].lower().strip()
        recent_assistant_msg = response.content.lower()

        user_said_yes = any(x in recent_user_msg for x in ["yes", "go ahead", "correct", "that's right", "sounds good"])
        assistant_provided_summary = any(
            x in recent_assistant_msg for x in [
                "to summarize", "summary", "here’s what i understood", "let me recap", "does this accurately capture"
            ]
        )

        is_complete = user_said_yes and assistant_provided_summary
        return {
            **state,
            "conversation_history": conversation_history,
            "current_step": "summary" if is_complete else "chat",
            "user_input": ""  # Clear for next iteration
        }
    
    def summary_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Creates structured summary from consultation"""
        
        system_prompt = """You are a brand strategist who creates actionable design briefs from client consultations.
        
        Analyze the conversation and create a structured summary in this EXACT format:
        
        {
            "company_details": {
                "name": "Company Name",
                "industry": "Specific tech sector",
                "business_function": "What they do",
                "target_audience": "Who they serve",
                "unique_value": "Key differentiator"
            },
            "brand_requirements": {
                "personality": ["trait1", "trait2", "trait3"],
                "desired_perception": "How they want to be viewed",
                "core_values": ["value1", "value2"],
                "emotional_goal": "Feeling logo should evoke"
            },
            "design_specifications": {
                "logo_style": "Style preference",
                "color_direction": "Color preferences",
                "aesthetic_approach": "Visual approach",
                "visual_inspiration": "Referenced examples",
                "avoid": "Things to avoid"
            },
            "technical_requirements": {
                "primary_applications": ["usage1", "usage2"],
                "scalability_needs": "Size requirements",
                "background_variations": "Background needs",
                "file_priorities": "Format preferences"
            },
            "competitive_context": {
                "key_competitors": ["comp1", "comp2"],
                "differentiation": "How to stand apart",
                "industry_positioning": "Market position"
            }
        }
        
        Return ONLY the JSON structure, no additional text."""
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in state["conversation_history"]
        ])
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Conversation to summarize:\n{conversation_text}")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            client_requirements = json.loads(response.content)
            return {
                **state,
                "client_requirements": client_requirements,
                "chat_summary": response.content,
                "current_step": "design"
            }
        except json.JSONDecodeError:
            return {
                **state,
                "error_message": "Failed to parse client requirements",
                "current_step": "error"
            }
        
    async def designer_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Creates design concepts and specifications using LLM"""

        # REMOVE: AgentConfig dependency
        # config = AgentConfig.get_config("designer")

        system_prompt = """You are an elite logo designer creating concepts for tech companies.

    Based on the client requirements, create 3 distinct logo concepts in this JSON format:

    {
        "concepts": [
            {
                "concept_id": 1,
                "name": "Concept Name",
                "description": "Brief description of the design approach",
                "style": "minimalist/geometric/wordmark/symbol/etc",
                "color_palette": {
                    "primary": "#hexcode",
                    "secondary": "#hexcode",
                    "accent": "#hexcode"
                },
                "typography": "Font style/approach",
                "symbol_concept": "Description of any symbols/icons",
                "rationale": "Why this concept fits the brand",
                "midjourney_prompt": "Optimized prompt for Midjourney generation"
            }
        ],
        "design_rationale": "Overall strategic reasoning",
        "technical_notes": "Implementation considerations"
    }

    Create midjourney_prompt that's optimized for Midjourney logo generation.
    Use parameters like --ar 1:1 --style raw --v 6.0 for best results.
    Return ONLY the JSON structure."""

        requirements_text = json.dumps(state["client_requirements"], indent=2)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Client Requirements:\n{requirements_text}"}
        ]

        try:
            print("[🎨 DESIGNER AGENT] Requesting logo concepts from LLM...")

            # REMOVE: config["provider"], USE default provider
            response = await self.llm_manager.generate_text(messages)

            print("[✅ RAW LLM RESPONSE]")
            print(response)

            design_concepts_json = json.loads(response)

            # Print each concept clearly to terminal
            for concept in design_concepts_json.get("concepts", []):
                print("\n[🧠 DESIGN CONCEPT]")
                print(f"Name: {concept['name']}")
                print(f"Style: {concept['style']}")
                print(f"Colors: {concept['color_palette']}")
                print(f"Typography: {concept['typography']}")
                print(f"Prompt: {concept['midjourney_prompt']}\n")

            return {
                **state,
                "design_concepts": design_concepts_json["concepts"],
                "current_step": "generate"
            }

        except json.JSONDecodeError as e:
            print("[❌ DESIGNER ERROR] Failed to parse JSON:\n", e)
            print("[❌ RAW RESPONSE WAS]:\n", response)
            return {
                **state,
                "error_message": "Failed to parse design concepts",
                "current_step": "error"
            }

        except Exception as e:
            print("[❌ DESIGNER AGENT EXCEPTION]", str(e))
            return {
                **state,
                "error_message": f"Designer agent error: {str(e)}",
                "current_step": "error"
            }
    
    def generator_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Generates logo images and attaches to chat. Compatible with sync context."""
        import asyncio
        from datetime import datetime
        import os

        async def generate_all():
            generated_logos = []
            log_file = "generated_images_log.txt"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            async def generate_for_concept(concept):
                print(f"[🔄 LOG] Generating image for concept: {concept['name']}")
                result = await self.replicate_provider.generate_image(
                    prompt=concept["generation_prompt"],
                    width=1024,
                    height=1024,
                    style="minimal tech logo"
                )
                print(f"[✅ IMAGE GENERATED] {concept['name']}: {result['image_url']}")

                with open(log_file, "a") as f:
                    f.write(f"[{datetime.now()}] {concept['name']} → {result['image_url']}\n")

                return {
                    "concept_id": concept["concept_id"],
                    "concept_name": concept["name"],
                    "image_url": result["image_url"],
                    "variations": {
                        "primary": result["image_url"],
                        "horizontal": result["image_url"],
                        "icon": result["image_url"]
                    },
                    "generation_metadata": {
                        "prompt_used": concept["generation_prompt"],
                        "generation_time": result.get("generation_time", "unknown"),
                        "model": result.get("model", "replicate/unknown")
                    }
                }

            return await asyncio.gather(*[generate_for_concept(c) for c in state["design_concepts"]])

        # Handle running loop issue
        try:
            generated_logos = asyncio.run(generate_all())
        except RuntimeError:  # Already inside async loop
            generated_logos = asyncio.get_event_loop().run_until_complete(generate_all())

        image_message = {
            "role": "assistant",
            "content": "🖼️ Here are your logo concepts:\n" +
                    "\n".join([logo["image_url"] for logo in generated_logos])
        }
        state["conversation_history"].append(image_message)

        return {
            **state,
            "generated_logos": generated_logos,
            "generation_attempts": state.get("generation_attempts", 0) + 1,
            "current_step": "ranking"
        }
    
    
    def ranking_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Evaluates generated logos for quality and adherence to requirements"""
        
        system_prompt = """You are a logo quality assessor. Evaluate each generated logo against the client requirements.
        
        For each logo, assess:
        1. Design Quality (0-10): Professional appearance, visual appeal
        2. Brand Alignment (0-10): How well it matches client requirements
        3. Technical Quality (0-10): Clarity, scalability, text readability
        4. Uniqueness (0-10): Distinctiveness from competitors
        5. Issues: Any problems like broken text, poor composition, etc.
        
        Return assessment in this JSON format:
        {
            "overall_quality": "pass/fail",
            "best_concept_id": 1,
            "assessments": [
                {
                    "concept_id": 1,
                    "scores": {
                        "design_quality": 8,
                        "brand_alignment": 9,
                        "technical_quality": 7,
                        "uniqueness": 8
                    },
                    "total_score": 32,
                    "issues": ["Minor text clarity issues"],
                    "recommendation": "Approved with minor refinements"
                }
            ],
            "regeneration_needed": false,
            "regeneration_reasons": []
        }
        
        Mark as "pass" if at least one logo scores 28+ total points with no major issues."""
        
        # In production, you'd analyze actual images here
        # For now, simulate the ranking process
        
        ranking_results = {
            "overall_quality": "pass",
            "best_concept_id": 1,
            "assessments": [
                {
                    "concept_id": 1,
                    "scores": {
                        "design_quality": 9,
                        "brand_alignment": 8,
                        "technical_quality": 8,
                        "uniqueness": 9
                    },
                    "total_score": 34,
                    "issues": [],
                    "recommendation": "Approved - excellent quality"
                },
                {
                    "concept_id": 2,
                    "scores": {
                        "design_quality": 7,
                        "brand_alignment": 8,
                        "technical_quality": 6,
                        "uniqueness": 7
                    },
                    "total_score": 28,
                    "issues": ["Text could be clearer at small sizes"],
                    "recommendation": "Approved with minor concerns"
                }
            ],
            "regeneration_needed": False,
            "regeneration_reasons": []
        }
        
        needs_regeneration = (
            ranking_results["overall_quality"] == "fail" and
            state.get("generation_attempts", 0) < state.get("max_attempts", 3)
        )
        
        next_step = "regenerate" if needs_regeneration else "user_review"
        
        return {
            **state,
            "ranking_results": ranking_results,
            "needs_regeneration": needs_regeneration,
            "current_step": next_step
        }
    
    def feedback_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Handles user feedback and iterations"""
        
        system_prompt = """You are a design iteration specialist. Analyze user feedback and determine next steps.
        
        Based on the feedback, decide:
        1. If changes require new design concepts (back to designer)
        2. If changes require only regeneration with modified prompts
        3. If user wants to proceed with current designs
        4. If user wants to package final logos
        
        Return decision in JSON format:
        {
            "action": "redesign/regenerate/approve/package",
            "reason": "Explanation of decision",
            "modifications": "Specific changes needed",
            "updated_requirements": {...}  // If requirements changed
        }"""
        
        feedback_context = {
            "user_feedback": state.get("user_feedback", ""),
            "current_designs": state.get("design_concepts", []),
            "ranking_results": state.get("ranking_results", {}),
            "iteration_count": state.get("iteration_count", 0)
        }
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Feedback Context:\n{json.dumps(feedback_context, indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            feedback_analysis = json.loads(response.content)
            
            # Determine next step based on feedback
            action_map = {
                "redesign": "design",
                "regenerate": "generate",
                "approve": "package",
                "package": "package"
            }
            
            next_step = action_map.get(feedback_analysis["action"], "user_review")
            
            return {
                **state,
                "current_step": next_step,
                "iteration_count": state.get("iteration_count", 0) + 1,
                "user_feedback": ""  # Clear feedback after processing
            }
            
        except json.JSONDecodeError:
            return {
                **state,
                "error_message": "Failed to parse feedback analysis",
                "current_step": "error"
            }
    
    def package_agent(self, state: LogoDesignState) -> LogoDesignState:
        """Creates final package with all logo assets"""
        
        # Get the best logo concepts based on ranking
        best_concepts = []
        if state.get("ranking_results"):
            best_concept_id = state["ranking_results"]["best_concept_id"]
            best_concepts = [
                logo for logo in state["generated_logos"] 
                if logo["concept_id"] == best_concept_id
            ]
        
        # Create package structure
        package_data = {
            "package_id": f"logo_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "client_info": state.get("client_requirements", {}),
            "final_logos": best_concepts,
            "color_palette": self._extract_color_palette(state),
            "brand_guidelines": self._create_brand_guidelines(state),
            "file_deliverables": {
                "svg_files": ["logo.svg", "logo_horizontal.svg", "logo_icon.svg"],
                "png_files": ["logo_300dpi.png", "logo_web.png"],
                "pdf_files": ["logo_vector.pdf", "brand_guidelines.pdf"],
                "additional": ["favicon.ico", "social_media_kit.zip"]
            },
            "usage_guidelines": self._create_usage_guidelines(state),
            "technical_specs": {
                "color_codes": {"primary": "#000000", "secondary": "#ffffff"},
                "fonts": ["Arial", "Helvetica"],
                "minimum_sizes": {"print": "1 inch", "digital": "32px"}
            }
        }
        
        # In production, you'd actually generate PDF, ZIP files, etc.
        package_path = f"packages/{package_data['package_id']}.pdf"
        
        return {
            **state,
            "final_package": package_path,
            "current_step": "complete"
        }
    
    def _extract_color_palette(self, state: LogoDesignState) -> Dict[str, str]:
        """Extract color palette from design concepts"""
        if not state.get("design_concepts"):
            return {}
        
        # Get colors from the best concept
        best_concept = state["design_concepts"][0]  # Simplified
        return best_concept.get("color_palette", {})
    
    def _create_brand_guidelines(self, state: LogoDesignState) -> Dict[str, Any]:
        """Create basic brand guidelines"""
        return {
            "logo_usage": "Guidelines for proper logo usage",
            "color_usage": "When and how to use brand colors",
            "typography": "Recommended fonts and text treatments",
            "spacing": "Minimum clear space requirements",
            "backgrounds": "Approved background treatments"
        }
    
    def _create_usage_guidelines(self, state: LogoDesignState) -> List[str]:
        """Create usage guidelines"""
        return [
            "Always maintain minimum clear space around logo",
            "Do not alter logo colors without approval",
            "Use vector formats when possible for scalability",
            "Ensure adequate contrast on all backgrounds",
            "Do not stretch, skew, or modify logo proportions"
        ]